from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.setup.database import get_db
from src.setup.dependencies import CurrentUser
from src.models.core import AppraisalReview, Declaration, FacultyProfile
from src.crud.core import create_or_update_review
from src.schema.core import AppraisalReviewBase
from typing import Dict, Any
from sqlalchemy import select, update
from src.models import part_a as models_a
from src.models import part_b as models_b

router = APIRouter(prefix="/appraisal-remarks", tags=["Appraisal Remarks"])

async def update_item_scores(db: AsyncSession, email: str, year: str, role: str, section_scores: Dict[str, float]):
    """
    Updates individual item scores in normalized tables based on authority review.
    Samarth's note: authority's per-section scores must be written into individual section tables.
    """
    column_map = {
        "hod": "hod_score",
        "center_head": "director_score", 
        "director": "director_score",
        "dean": "dean_score",
        "vc": "vc_score"
    }
    
    col = column_map.get(role)
    if not col: return

    # Mapping of frontend section keys to Models
    section_map = {
        "lectures": models_a.TeachingProcess,
        "courseFile": models_a.CourseFile,
        "innovDetails": models_a.InnovativeTeaching,
        "projects": models_a.ProjectGuided,
        "quals": models_a.QualificationEnhancement,
        "feedback": models_a.StudentFeedback,
        "deptActs": models_a.DepartmentActivity,
        "uniActs": models_a.UniversityActivity,
        "society": models_a.SocialContribution,
        "industry": models_a.IndustryConnect,
        "acr": models_a.ACRScore,
        "journals": models_b.JournalPublication,
        "books": models_b.BookPublication,
        "ict": models_b.ICTPedagogy,
        "research": models_b.ResearchGuidance,
        "projects2": models_b.ResearchProject,
        "externalProjects": models_b.ExternalResearchProject,
        "patents": models_b.Patent,
        "awards": models_b.Award,
        "confs": models_b.Conference,
        "proposals": models_b.ResearchProposal,
        "products": models_b.ProductDeveloped,
        "fdps": models_b.SelfDevelopment,
        "training": models_b.IndustrialTraining,
    }

    for section_key, score in section_scores.items():
        model = section_map.get(section_key)
        if model:
            # Check if column exists (BasePartA/B models have these)
            if hasattr(model, col):
                await db.execute(
                    update(model)
                    .where(model.faculty_email == email, model.academic_year == year)
                    .values({col: score})
                )

async def handle_review(role: str, email: str, data: Dict[str, Any], current_user: CurrentUser, db: AsyncSession):
    # 0. Authorization check
    target_res = await db.execute(select(FacultyProfile).where(FacultyProfile.email == email))
    target = target_res.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    if not current_user.has_authority_over(email, target.appraisal_role, target.department, target.school):
        raise HTTPException(status_code=403, detail="Not authorized to update remarks for this faculty")

    # 1. Update Review Table
    review_in = AppraisalReviewBase(
        faculty_email=email,
        academic_year=data['academic_year'],
        reviewer_email=current_user.email,
        reviewer_role=role,
        part_a_score=data['part_a_score'],
        part_b_score=data['part_b_score'],
        total_score=data['total_score'],
        remarks=data['remarks'],
        status='Reviewed'
    )
    await create_or_update_review(db, review_in)
    
    # 2. Shred Section Scores into normalized tables
    if 'section_scores' in data:
        await update_item_scores(db, email, data['academic_year'], role, data['section_scores'])

    # 3. Update Declaration Status
    status_map = {
        "hod": "pending_director",
        "center_head": "pending_director",
        "director": "pending_dean",
        "dean": "pending_vc",
        "vc": "completed" # VC is final
    }
    
    res = await db.execute(select(Declaration).where(
        Declaration.faculty_email == email,
        Declaration.academic_year == data['academic_year']
    ))
    decl = res.scalar_one_or_none()
    if decl:
        decl.status = status_map.get(role, decl.status)
    
    await db.commit()
    return {"message": "Review submitted", "status": decl.status if decl else "unknown"}

@router.put("/hod/{email}")
async def review_hod(email: str, data: Dict[str, Any], current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    if "hod" not in current_user.roles and "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="HOD role required")
    return await handle_review("hod", email, data, current_user, db)

@router.put("/center-head/{email}")
async def review_center_head(email: str, data: Dict[str, Any], current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    if "center_head" not in current_user.roles and "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Center Head role required")
    return await handle_review("center_head", email, data, current_user, db)

@router.put("/director/{email}")
async def review_director(email: str, data: Dict[str, Any], current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    if "director" not in current_user.roles and "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Director role required")
    return await handle_review("director", email, data, current_user, db)

@router.put("/dean/{email}")
async def review_dean(email: str, data: Dict[str, Any], current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    if "dean" not in current_user.roles and "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Dean role required")
    return await handle_review("dean", email, data, current_user, db)

@router.put("/final/{email}")
async def review_final(email: str, data: Dict[str, Any], current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    if "vc" not in current_user.roles and "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="VC role required")
    return await handle_review("vc", email, data, current_user, db)
