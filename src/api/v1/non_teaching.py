from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.setup.database import get_db
from src.setup.dependencies import CurrentUser
from src.models.non_teaching import NonTeachingAppraisal
from src.crud import non_teaching as crud
from src.models.core import FacultyProfile
from sqlalchemy import select
from datetime import datetime
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
    # 0. Authorization check
    target_res = await db.execute(select(FacultyProfile).where(FacultyProfile.email == email))
    target = target_res.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="Staff profile not found")
    
    if not current_user.has_authority_over(email, target.appraisal_role, target.department, target.school):
        raise HTTPException(status_code=403, detail="Not authorized to view this staff's data")

    # 1. Update totals based on role
    # Logic: If RO reviews, they update ro_total. If Registrar reviews, registrar_total.
    # The frontend payload usually contains the updated scores in 'payload'.
    
    academic_year = data.get('academic_year')
    if not academic_year:
        raise HTTPException(status_code=422, detail="academic_year is required")
    appr = await crud.get_non_teaching_appraisal(db, email, academic_year)
    if not appr:
        raise HTTPException(status_code=404, detail="Appraisal not found")

    # Mapping roles to database fields and next status
    role_config = {
        "reporting_officer": ("ro_total", "Reporting Officer Reviewed", "ro_reviewed_at"),
        "registrar": ("registrar_total", "Registrar Reviewed", "registrar_reviewed_at"),
        "vc": ("vc_total", "VC Approved", "vc_reviewed_at")
    }

    # Identify primary reviewer role
    primary_role = next((r for r in current_user.roles if r in role_config), None)
    if not primary_role and "admin" not in current_user.roles:
         raise HTTPException(status_code=403, detail="Invalid reviewer role")
    
    if "admin" in current_user.roles and not primary_role:
        primary_role = "registrar" # Default admin review to registrar level

    field, next_status, time_field = role_config[primary_role]
    
    # Update the appraisal object
    appr.status = next_status
    setattr(appr, time_field, datetime.utcnow())
    
    # If the payload contains the new total, save it
    if 'payload' in data:
        appr.payload = data['payload']
        # Optionally extract totals from payload if not explicitly provided
    
    if 'total_score' in data: # Assume frontend sends this
        setattr(appr, field, data['total_score'])

    await db.commit()
    await db.refresh(appr)
    return appr
