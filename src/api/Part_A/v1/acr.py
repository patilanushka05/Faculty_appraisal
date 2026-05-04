from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Annotated

from ....setup.dependencies import get_db, CurrentUser
from ....setup.storage_utils import upload_file_to_supabase
from ....schema.Part_A.acr import (
    ACRCreate,
    ACRUpdateHOD,
    ACRUpdateDirector,
    ACRResponse,
)
from ....crud.Part_A import acr as crud_acr

router = APIRouter()

@router.post("/acr", response_model=ACRResponse, status_code=status.HTTP_201_CREATED)
async def create_acr(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Form()],
    subject: Annotated[str, Form()],
    sr_no: Annotated[Optional[int], Form()] = None,
    department: Annotated[Optional[str], Form()] = None,
    file: Annotated[Optional[UploadFile], File()] = None,
):
    if "admin" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can pre-create ACR rows")
    
    document_path = None
    if file:
        document_path = await upload_file_to_supabase(file, faculty_id)
    
    acr_data = ACRCreate(
        faculty_id=faculty_id,
        sr_no=sr_no,
        subject=subject,
        department=department,
        document=document_path
    )
    return await crud_acr.create_acr(db, acr_data)

@router.get("/acr/faculty/{faculty_id}", response_model=List[ACRResponse])
async def read_acr_by_faculty(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path()],
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=403, detail="Not authorized")
    return await crud_acr.get_acr_by_faculty(db, faculty_id)

@router.get("/acr", response_model=List[ACRResponse])
async def read_all_acr(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    allowed_roles = {"admin", "dean", "vc"}
    if not any(role in allowed_roles for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin, dean, or vc can view all data")
    
    result = await db.execute(select(crud_acr.ACR))
    return result.scalars().all()

@router.put("/acr/{id}", response_model=ACRResponse)
async def update_acr(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    id: Annotated[str, Path()],
    acr_update: ACRUpdateHOD,
):
    db_entry = await crud_acr.get_acr(db, id)
    if not db_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if not current_user.has_authority_over(db_entry.faculty_id, "faculty", db_entry.department):
        raise HTTPException(status_code=403, detail="Not authorized")

    if "hod" in current_user.roles:
        return await crud_acr.update_acr_hod(db, id, acr_update)
    elif "director" in current_user.roles:
        return await crud_acr.update_acr_director(db, id, acr_update)
    elif "admin" in current_user.roles:
        return await crud_acr.update_acr_hod(db, id, acr_update)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access for this role")

@router.get("/acr/summary/{faculty_id}")
async def get_acr_summary(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path()],
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    entries = await crud_acr.get_acr_by_faculty(db, faculty_id)
    total_score = sum([e.api_score_hod or 0.0 for e in entries])
    return {"totalScore": min(total_score, 25)}
