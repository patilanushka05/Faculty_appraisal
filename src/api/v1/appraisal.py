from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.setup.database import get_db
from src.setup.dependencies import CurrentUser
from src.models.core import AppraisalSnapshot, Declaration, AppraisalDocument, AppraisalReview, FormSectionDefinition
from src.crud.core import create_or_update_declaration
from src.models import part_a as models_a
from src.models import part_b as models_b
from sqlalchemy import select, delete, inspect as sa_inspect, Numeric as SANumeric, Integer as SAInteger, String as SAString
from sqlalchemy.orm import flag_modified
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging
import traceback

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/appraisal", tags=["Appraisal Form"])

def _coerce_for_column(model_instance, field_name, value):
    """Coerce value to match the actual DB column type."""
    if value is None:
        return None
    if isinstance(value, str) and value.strip() == '':
        return None

    try:
        col = sa_inspect(type(model_instance)).columns.get(field_name)
        if col is not None:
            col_type = col.type
            if isinstance(col_type, SAInteger):
                try:
                    # Handle case where value might be a float string like "5.0"
                    return int(float(value))
                except (ValueError, TypeError):
                    return None
            elif isinstance(col_type, SANumeric):
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return None
            else:
                # VARCHAR / Text / String — always convert to str
                if isinstance(value, (int, float)):
                    return str(value)
    except Exception:
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
            flag_modified(db_snapshot, "payload")
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
    # Mapping of frontend form keys to (Model, Section Title)
    mappings = {
        "lectures": (models_a.TeachingProcess, "A1. Lectures / Tutorials / Practicals"),
        "courseFile": (models_a.CourseFile, "A2. Course File"),
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
        "fdps": (models_b.SelfDevelopment, "B8(a). FDP / Workshops"),
        "training": (models_b.IndustrialTraining, "B8(b). Industrial Training"),
    }

    # Field Aliases Mapping (Frontend -> Backend)
    field_aliases = {
        "title_with_page_nos": "title",
        "journal_details": "journal",
        "issn_isbn_no": "issn",
        "issn_isbn": "issn",
        "course_code_name": "course_code",
        "course_paper": "course",
        "nature_of_activity": "nature",
        "activity_type": "activity",
        "details_of_activity": "details",
        "project_type": "label",
        "qualification_type": "label",
        "short_description": "details",
        "title_and_pages": "title",
        "book_title_editor": "book",
        "event_title": "title",
        "hosting_organization": "organization",
        "event_level": "level",
        "pedagogy_type": "type",
        "company_industry": "company",
        "duration_days": "duration",
        "nature_of_training": "nature",
        "hod": "hod_score",
        "director": "director_score",
        "dean": "dean_score",
        "vc": "vc_score",
        "maxMarks": "max_marks"
    }

    # 1. Handle InnovativeTeaching separately (Scalar text field)
    await db.execute(delete(models_a.InnovativeTeaching).where(
        models_a.InnovativeTeaching.faculty_email == email,
        models_a.InnovativeTeaching.academic_year == year
    ))
    innov_details = form_data.get("innovDetails")
    innov_score_raw = form_data.get('innovScore')
    
    if innov_details or innov_score_raw:
        innov = models_a.InnovativeTeaching(
            faculty_email=email,
            academic_year=year,
            form_family=form_family,
            section_title="A3. Innovative Teaching-Learning",
            details=str(innov_details) if not isinstance(innov_details, dict) else innov_details.get("details")
        )
        if innov_score_raw is not None:
            innov.score = _coerce_for_column(innov, 'score', innov_score_raw)
        db.add(innov)

    # 2. Handle all other sections (List of objects)
    for key, (model, title) in mappings.items():
        # Clean existing records for this user/year/section to avoid duplicates on re-submit
        await db.execute(delete(model).where(
            model.faculty_email == email,
            model.academic_year == year
        ))

        section_data = form_data.get(key)
        if not section_data and section_data != 0:
            continue
        
        # Handle both list and object inputs (some sections are single objects)
        items = section_data if isinstance(section_data, list) else [section_data]
        
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                continue

            # Build constructor kwargs safely
            kwargs = {
                "faculty_email": email,
                "academic_year": year,
                "form_family": form_family,
                "section_title": title
            }
            if hasattr(model, "row_no"):
                kwargs["row_no"] = idx + 1
            
            db_item = model(**kwargs)
            
            # Map specific fields from JSON to Model columns
            for field_name, value in item.items():
                target_field = field_aliases.get(field_name, field_name)
                if not hasattr(db_item, target_field):
                    continue
                coerced = _coerce_for_column(db_item, target_field, value)
                if coerced is not None:
                    setattr(db_item, target_field, coerced)
            
            db.add(db_item)

@router.post("/submit")
async def submit_appraisal(data: Dict[str, Any], current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    academic_year = data.get('academic_year')
    
    # Robustness: Check both 'form' and 'payload.form'
    form = data.get('form')
    totals = data.get('totals')
    
    if not form and "payload" in data and isinstance(data["payload"], dict):
        form = data["payload"].get("form")
    if not totals and "payload" in data and isinstance(data["payload"], dict):
        totals = data["payload"].get("totals")

    if not form:
        raise HTTPException(status_code=400, detail="Form data is missing. Ensure 'form' or 'payload.form' key is present.")

    if not academic_year:
        raise HTTPException(status_code=422, detail="academic_year is required")

    totals = totals or {}
    
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
            flag_modified(db_snapshot, "payload")
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
