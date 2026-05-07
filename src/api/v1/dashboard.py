from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.setup.database import get_db
from src.setup.dependencies import CurrentUser
from src.models.core import FacultyProfile, Declaration, AppraisalSnapshot, AppraisalReview
from sqlalchemy import select
from typing import List, Optional

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/subordinates")
async def get_subordinates(
    current_user: CurrentUser,
    academic_year: str = Query(...), 
    schools: Optional[str] = None, 
    db: AsyncSession = Depends(get_db)
):
    # Role-based filtering
    query = select(FacultyProfile, Declaration).outerjoin(
        Declaration, FacultyProfile.email == Declaration.faculty_email
    )
    
    # 1. Authority filtering (School/Dept/Division)
    if "vc" in current_user.roles or "registrar" in current_user.roles:
        # VC/Registrar: Can see all schools, or filter by specific schools if provided
        if schools:
            school_list = schools.split(",")
            query = query.where(FacultyProfile.school.in_(school_list))
    elif "dean" in current_user.roles:
        # Dean: Sees all schools within their division (Engineering/Non-Engineering)
        # We need the division from the school table or faculty profile
        query = query.where(FacultyProfile.division == current_user.division)
    elif "center_head" in current_user.roles:
        # Center Head: specifically for CISR
        query = query.where(FacultyProfile.school == "CISR")
    elif "director" in current_user.roles or "reporting_officer" in current_user.roles:
        # Director/Reporting Officer: Sees everyone in their school
        query = query.where(FacultyProfile.school == current_user.school)
    elif "hod" in current_user.roles:
        # HOD: Sees everyone in their department within their school
        query = query.where(FacultyProfile.school == current_user.school, FacultyProfile.department == current_user.department)
    else:
        # Faculty/Non-Teaching Staff: Cannot see subordinates
        return []

    result = await db.execute(query)
    rows = result.all()
    
    subordinates = []
    for faculty, decl in rows:
        # Get reviews to fill the scores
        rev_res = await db.execute(select(AppraisalReview).where(
            AppraisalReview.faculty_email == faculty.email,
            AppraisalReview.academic_year == academic_year
        ))
        reviews = rev_res.scalars().all()
        
        # Simplified mapping for dashboard
        sub = {
            "email": faculty.email,
            "name": faculty.full_name,
            "department": faculty.department,
            "school": faculty.school,
            "appraisalRole": faculty.appraisal_role,
            "status": decl.status if decl else "pending",
            "submittedOn": decl.submitted_at.date() if decl else None,
            "selfPartA": decl.part_a_total if decl else 0,
            "selfPartB": decl.part_b_total if decl else 0,
            "selfTotal": decl.grand_total if decl else 0
        }
        
        # Add authority scores from reviews
        for rev in reviews:
            role = rev.reviewer_role
            sub[f"{role}PartA"] = rev.part_a_score
            sub[f"{role}PartB"] = rev.part_b_score
            sub[f"{role}Total"] = rev.total_score
            sub[f"{role}Remarks"] = rev.remarks
            
        subordinates.append(sub)
        
    return subordinates

@router.get("/faculty/{email}")
async def get_faculty_snapshot(email: str, academic_year: str, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    # 0. Authorization check
    target_res = await db.execute(select(FacultyProfile).where(FacultyProfile.email == email))
    target = target_res.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    if not current_user.has_authority_over(email, target.appraisal_role, target.department, target.school, target.division):
        raise HTTPException(status_code=403, detail="Not authorized to view this faculty's data")
    
    res = await db.execute(select(AppraisalSnapshot).where(
        AppraisalSnapshot.faculty_email == email,
        AppraisalSnapshot.academic_year == academic_year
    ))
    snapshot = res.scalar_one_or_none()
    return snapshot
