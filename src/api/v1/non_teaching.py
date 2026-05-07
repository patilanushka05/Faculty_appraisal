from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.setup.database import get_db
from src.setup.dependencies import CurrentUser
from src.models.non_teaching import NonTeachingAppraisal
from src.crud import non_teaching as crud
from src.models.core import FacultyProfile
from sqlalchemy import select
from typing import List, Optional, Dict, Any

router = APIRouter(prefix="/non-teaching", tags=["Non-Teaching"])

@router.get("/appraisal")
async def get_my_appraisal(academic_year: str, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    return await crud.get_non_teaching_appraisal(db, current_user.email, academic_year)

@router.put("/appraisal")
async def upsert_my_appraisal(data: Dict[str, Any], current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    data['staff_email'] = current_user.email
    return await crud.create_or_update_non_teaching_appraisal(db, data)

@router.get("/subordinates")
async def get_non_teaching_subordinates(academic_year: str, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    # Registrar/RO logic
    query = select(NonTeachingAppraisal, FacultyProfile).join(
        FacultyProfile, NonTeachingAppraisal.staff_email == FacultyProfile.email
    ).where(NonTeachingAppraisal.academic_year == academic_year)
    
    # 1. Authority filtering
    if "registrar" in current_user.roles or "vc" in current_user.roles:
        # Sees all non-teaching pending review
        pass
    elif "reporting_officer" in current_user.roles:
        # RO: Sees only those in their school/dept
        query = query.where(FacultyProfile.school == current_user.school, FacultyProfile.department == current_user.department)
    else:
        return []

    result = await db.execute(query)
    rows = result.all()
    
    subordinates = []
    for appr, profile in rows:
        subordinates.append({
            "staff_email": appr.staff_email,
            "name": profile.full_name,
            "designation": profile.designation,
            "department": profile.department,
            "appraisalRole": profile.appraisal_role,
            "status": appr.status,
            "submittedOn": appr.submitted_at.date() if appr.submitted_at else None,
            "selfTotal": appr.self_total,
            "roTotal": appr.ro_total or 0,
            "registrarTotal": appr.registrar_total or 0,
            "vcTotal": appr.vc_total or 0,
            "payload": appr.payload
        })
    return subordinates

@router.put("/review/{email}")
async def review_non_teaching(email: str, data: Dict[str, Any], current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    data['staff_email'] = email
    # Update totals based on role
    # ... logic for ro_total vs registrar_total ...
    return await crud.create_or_update_non_teaching_appraisal(db, data)
