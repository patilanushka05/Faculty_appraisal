from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.setup.database import get_db
from src.setup.dependencies import CurrentUser
from src.models.core import AppraisalSnapshot, Declaration, AppraisalDocument, AppraisalReview, FormSectionDefinition
from src.crud.core import create_or_update_declaration
from src.models import part_a as models_a
from src.models import part_b as models_b
from sqlalchemy import select, delete
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging
import traceback

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/appraisal", tags=["Appraisal Form"])

def _safe_db_value(value):
    """Convert frontend form values to DB-compatible Python types."""
    if value is None or value == '':
        return None
    if isinstance(value, str):
        stripped = value.strip()
        if stripped == '':
            return None
        try:
            return int(stripped) if stripped.lstrip('-').isdigit() else float(stripped)
        except (ValueError, TypeError):
            pass
    return value

def _safe_num(value, default=0):
    """Coerce a value to float for totals, falling back to default."""
    if value is None or value == '':
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

@router.get("/snapshot")
async def get_snapshot(academic_year: str, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(AppraisalSnapshot).where(
            AppraisalSnapshot.faculty_email == current_user.email,
            AppraisalSnapshot.academic_year == academic_year
        ))
        snapshot = result.scalar_one_or_none()
        return snapshot
    except Exception as e:
        logger.error(f"Error fetching snapshot: {str(e)}")
        return None

@router.put("/snapshot")
async def upsert_snapshot(data: Dict[str, Any], current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    academic_year = data.get('academic_year')
    payload = data.get('payload')
    
    try:
        result = await db.execute(select(AppraisalSnapshot).where(
            AppraisalSnapshot.faculty_email == current_user.email,
            AppraisalSnapshot.academic_year == academic_year
        ))
        db_snapshot = result.scalar_one_or_none()
        
        if db_snapshot:
            db_snapshot.payload = payload
        else:
            db_snapshot = AppraisalSnapshot(
                faculty_email=current_user.email,
                academic_year=academic_year,
                payload=payload
            )
            db.add(db_snapshot)
        
        await db.commit()
        return {"message": "Saved"}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error saving snapshot for {current_user.email}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to save draft snapshot")

async def shred_form(db: AsyncSession, email: str, year: str, form_data: Dict[str, Any], form_family: str):
    """
    Takes the JSON form data and populates normalized tables.
    """
    mappings = {
        "lectures": (models_a.TeachingProcess, "A1. Lectures / Tutorials / Practicals"),
        "courseFile": (models_a.CourseFile, "A2. Course File"),
        "innovDetails": (models_a.InnovativeTeaching, "A3. Innovative Teaching-Learning"),
        "projects": (models_a.ProjectGuided, "A4. Projects"),
        "quals": (models_a.QualificationEnhancement, "A5. Qualification Enhancement"),
        "feedback": (models_a.StudentFeedback, "Student Feedback"),
        "deptActs": (models_a.DepartmentActivity, "Departmental / School Activities"),
        "uniActs": (models_a.UniversityActivity, "University Level Activities"),
        "society": (models_a.SocialContribution, "Contribution to Society"),
        "industry": (models_a.IndustryConnect, "Industry Connect"),
        "acr": (models_a.ACRScore, "Annual Confidential Report - School Level"),
        "journals": (models_b.JournalPublication, "B1. Research Papers / Journal Publications"),
        "books": (models_b.BookPublication, "B2. Books / Book Chapters"),
        "ict": (models_b.ICTPedagogy, "B3. ICT / E-Content / Pedagogy"),
        "research": (models_b.ResearchGuidance, "B4(a). Research Guidance - PhD / PG"),
        "projects2": (models_b.ResearchProject, "B4(b). Research / Consultancy Internal Projects"),
        "externalProjects": (models_b.ExternalResearchProject, "B4(c). Research / Consultancy External Projects"),
        "patents": (models_b.Patent, "B5(a). Patents (IPR)"),
        "awards": (models_b.Award, "B5(b). Awards"),
        "confs": (models_b.Conference, "B6. Invited Lectures / Resource Person / Paper Presentations"),
        "proposals": (models_b.ResearchProposal, "B7(a). Submitted Research Proposals"),
        "products": (models_b.ProductDeveloped, "B7(b). Product Developed and Used by Students"),
        "fdps": (models_b.SelfDevelopment, "B8(a). FDP / Self Development"),
        "training": (models_b.IndustrialTraining, "B8(b). Industrial Training"),
    }

    # Save innovScore into InnovativeTeaching separately
    innov_score = _safe_db_value(form_data.get('innovScore'))

    for key, (model, title) in mappings.items():
        await db.execute(delete(model).where(
            model.faculty_email == email,
            model.academic_year == year
        ))

        section_data = form_data.get(key)
        if not section_data and section_data != 0:
            continue
        
        items = section_data if isinstance(section_data, list) else [section_data]
        
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                continue

            kwargs = {
                "faculty_email": email,
                "academic_year": year,
                "form_family": form_family,
                "section_title": title,
            }
            if hasattr(model, 'row_no'):
                kwargs["row_no"] = idx + 1

            # Apply innovScore to InnovativeTeaching score field if applicable
            if model is models_a.InnovativeTeaching and innov_score is not None:
                kwargs["score"] = innov_score

            db_item = model(**kwargs)

            # Field name mapping for reviewer scores and common frontend/backend mismatches
            field_map = {
                "hod": "hod_score",
                "director": "director_score",
                "dean": "dean_score",
                "vc": "vc_score",
                "maxMarks": "max_marks"
            }

            for field_name, value in item.items():
                target_field = field_map.get(field_name, field_name)
                if not hasattr(db_item, target_field):
                    continue
                safe_val = _safe_db_value(value)
                if safe_val is None:
                    continue  # let DB column defaults apply
                setattr(db_item, target_field, safe_val)
            
            db.add(db_item)

@router.post("/submit")
async def submit_appraisal(data: Dict[str, Any], current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    academic_year = data.get('academic_year')
    form = data.get('form', {})
    totals = data.get('totals', {})
    
    if not academic_year:
        raise HTTPException(status_code=422, detail="academic_year is required")

    try:
        # Identify user's form family
        from src.crud.core import get_faculty_by_email
        from src.setup.dependencies import get_form_family
        user = await get_faculty_by_email(db, current_user.email)
        form_family = get_form_family(user.school) if user else "standard"
        
        # 1. Shred JSON into normalized tables
        await shred_form(db, current_user.email, academic_year, form, form_family)

        # 2. Update/Create Declaration
        from src.schema.core import DeclarationBase
        decl_data = DeclarationBase(
            faculty_email=current_user.email,
            academic_year=academic_year,
            part_a_total=_safe_num(totals.get('partATotal')),
            part_b_total=_safe_num(totals.get('partBTotal')),
            grand_total=_safe_num(totals.get('grandTotal')),
            status='Submitted'
        )
        await create_or_update_declaration(db, decl_data)
        
        # 3. Update Snapshot (Draft -> Latest)
        result = await db.execute(select(AppraisalSnapshot).where(
            AppraisalSnapshot.faculty_email == current_user.email,
            AppraisalSnapshot.academic_year == academic_year
        ))
        db_snapshot = result.scalar_one_or_none()
        if db_snapshot:
            db_snapshot.payload = data # Save the full submit payload
        else:
            db.add(AppraisalSnapshot(
                faculty_email=current_user.email,
                academic_year=academic_year,
                payload=data
            ))
        
        await db.commit()
        return {"message": "Submitted successfully", "submitted_at": datetime.utcnow().isoformat()}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error during appraisal submission for {current_user.email}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Submission failed: {str(e)}")

@router.get("/status")
async def get_appraisal_status(academic_year: str, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    try:
        decl_res = await db.execute(select(Declaration).where(
            Declaration.faculty_email == current_user.email,
            Declaration.academic_year == academic_year
        ))
        declaration = decl_res.scalar_one_or_none()
        
        rev_res = await db.execute(select(AppraisalReview).where(
            AppraisalReview.faculty_email == current_user.email,
            AppraisalReview.academic_year == academic_year
        ))
        reviews = rev_res.scalars().all()
        
        return {
            "declaration": declaration,
            "reviews": reviews
        }
    except Exception as e:
        logger.error(f"Error fetching status: {str(e)}")
        return {"declaration": None, "reviews": []}
