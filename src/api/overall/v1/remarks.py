from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated

from ....setup.dependencies import get_db, CurrentUser
from ....schema.overall.remarks import (
    AppraisalRemarksResponse, AppraisalRemarksCreate,
    HODRemarksResponse, HODRemarksCreate,
    DirectorRemarksResponse, DirectorRemarksCreate,
    DeanRemarksResponse, DeanRemarksCreate,
    FinalApprovalResponse, FinalApprovalCreate
)
from ....crud.overall import remarks as crud_remarks

router = APIRouter()

@router.get("/appraisal-remarks/{faculty_id}", response_model=List[AppraisalRemarksResponse])
async def get_remarks(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(...)],
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view these remarks")
    
    return await crud_remarks.get_appraisal_remarks_by_faculty(db, faculty_id)

@router.post("/appraisal-remarks/{faculty_id}", response_model=AppraisalRemarksResponse)
async def add_remarks(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(...)],
    data: AppraisalRemarksCreate,
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add remarks for this faculty")
    
    return await crud_remarks.create_appraisal_remarks(db, faculty_id, data)

# HOD Endpoints
@router.get("/appraisal-remarks/hod/{faculty_id}", response_model=HODRemarksResponse)
async def get_hod_remarks(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(...)],
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    remarks = await crud_remarks.get_hod_remarks_by_faculty(db, faculty_id)
    if not remarks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="HOD remarks not found")
    return remarks

@router.put("/appraisal-remarks/hod/{faculty_id}", response_model=HODRemarksResponse)
async def update_hod_remarks(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(...)],
    data: HODRemarksCreate,
):
    if "hod" not in current_user.roles and "admin" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only HOD can update HOD remarks")
    
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return await crud_remarks.create_or_update_hod_remarks(db, faculty_id, data)

# Director Endpoints
@router.get("/appraisal-remarks/director/{faculty_id}", response_model=DirectorRemarksResponse)
async def get_director_remarks(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(...)],
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    remarks = await crud_remarks.get_director_remarks_by_faculty(db, faculty_id)
    if not remarks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Director remarks not found")
    return remarks

@router.put("/appraisal-remarks/director/{faculty_id}", response_model=DirectorRemarksResponse)
async def update_director_remarks(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(...)],
    data: DirectorRemarksCreate,
):
    if "director" not in current_user.roles and "admin" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Director can update Director remarks")
    
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return await crud_remarks.create_or_update_director_remarks(db, faculty_id, data)

# Dean Endpoints
@router.get("/appraisal-remarks/dean/{faculty_id}", response_model=DeanRemarksResponse)
async def get_dean_remarks(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(...)],
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    remarks = await crud_remarks.get_dean_remarks_by_faculty(db, faculty_id)
    if not remarks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dean remarks not found")
    return remarks

@router.put("/appraisal-remarks/dean/{faculty_id}", response_model=DeanRemarksResponse)
async def update_dean_remarks(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(...)],
    data: DeanRemarksCreate,
):
    if "dean" not in current_user.roles and "admin" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Dean can update Dean remarks")
    
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return await crud_remarks.create_or_update_dean_remarks(db, faculty_id, data)

# Final Approval Endpoints
@router.get("/appraisal-remarks/final/{faculty_id}", response_model=FinalApprovalResponse)
async def get_vc_approval(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(...)],
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    remarks = await crud_remarks.get_final_approval_by_faculty(db, faculty_id)
    if not remarks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="VC approval not found")
    return remarks

@router.put("/appraisal-remarks/final/{faculty_id}", response_model=FinalApprovalResponse)
async def update_vc_remarks(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(...)],
    data: FinalApprovalCreate,
):
    if "vc" not in current_user.roles and "admin" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only VC can update VC remarks")
    
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return await crud_remarks.create_or_update_final_approval(db, faculty_id, data)
