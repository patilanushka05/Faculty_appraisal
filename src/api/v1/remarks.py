from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.setup.database import get_db
from src.setup.dependencies import CurrentUser
from src.models.core import AppraisalReview, Declaration
from src.crud.core import create_or_update_review
from src.schema.core import AppraisalReviewBase
from typing import Dict
from sqlalchemy import select

router = APIRouter(prefix="/appraisal-remarks", tags=["Appraisal Remarks"])

async def handle_review(role: str, email: str, data: dict, current_user: CurrentUser, db: AsyncSession):
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
    
    # 2. Update Declaration Status
    status_map = {
        "hod": "pending_director",
        "center_head": "pending_director",
        "director": "pending_dean",
        "dean": "pending_vc",
        "final": "completed"
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
async def review_hod(email: str, data: dict, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    return await handle_review("hod", email, data, current_user, db)

@router.put("/center-head/{email}")
async def review_center_head(email: str, data: dict, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    return await handle_review("center_head", email, data, current_user, db)

@router.put("/director/{email}")
async def review_director(email: str, data: dict, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    return await handle_review("director", email, data, current_user, db)

@router.put("/dean/{email}")
async def review_dean(email: str, data: dict, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    return await handle_review("dean", email, data, current_user, db)

@router.put("/final/{email}")
async def review_final(email: str, data: dict, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    return await handle_review("vc", email, data, current_user, db)
