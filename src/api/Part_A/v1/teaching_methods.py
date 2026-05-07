from ...utils import mask_scores
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Annotated

from ....setup.dependencies import get_db, get_current_user, CurrentUser
from ....setup.storage_utils import upload_file_to_supabase
from ....schema.Part_A.teaching_methods import (
    TeachingMethodsCreate,
    TeachingMethodsUpdateFaculty,
    TeachingMethodsUpdateHOD,
    TeachingMethodsResponse,
)
from ....crud.Part_A import teaching_methods as crud_teaching_methods

router = APIRouter()

@router.post("/teaching-methods", response_model=TeachingMethodsResponse, status_code=status.HTTP_201_CREATED)
async def create_teaching_methods(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    sr_no: Annotated[Optional[int], Form()] = None,
    short_description: Annotated[str, Form()] = ...,
    details_proof: Annotated[bool, Form()] = False,
    department: Annotated[Optional[str], Form()] = None,
    file: Optional[UploadFile] = File(None)
):
    if "faculty" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only faculty can create entries")
    
    document_path = None
    if file:
        document_path = await upload_file_to_supabase(file, current_user.id)
    
    methods_data = TeachingMethodsCreate(
        sr_no=sr_no,
        short_description=short_description,
        details_proof=details_proof,
        department=department,
        document=document_path
    )
    return mask_scores(await crud_teaching_methods.create_teaching_methods(db, methods_data, current_user.id), current_user)

@router.get("/teaching-methods/faculty/{faculty_id}", response_model=List[TeachingMethodsResponse])
async def read_teaching_methods_by_faculty(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    faculty_id: str = Path(...)
):
    if "admin" not in current_user.roles and current_user.id != faculty_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return mask_scores(await crud_teaching_methods.get_teaching_methods_by_faculty(db, faculty_id), current_user)

@router.get("/teaching-methods", response_model=List[TeachingMethodsResponse])
async def read_all_teaching_methods(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser
):
    if "admin" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can view all data")
    from sqlalchemy import select
    result = await db.execute(select(crud_teaching_methods.TeachingMethods))
    return result.scalars().all()

@router.put("/teaching-methods/{id}", response_model=TeachingMethodsResponse)
async def update_teaching_methods(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    id: str = Path(...),
    methods_update: TeachingMethodsUpdateFaculty = None
):
    db_entry = await crud_teaching_methods.get_teaching_methods(db, id)
    if not db_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if "admin" in current_user.roles or "hod" in current_user.roles:
        return mask_scores(await crud_teaching_methods.update_teaching_methods_hod(db, id, methods_update), current_user)
    elif "faculty" in current_user.roles and db_entry.faculty_id == current_user.id:
        return mask_scores(await crud_teaching_methods.update_teaching_methods_faculty(db, id, methods_update), current_user)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

@router.delete("/teaching-methods/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teaching_methods(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    id: str = Path(...)
):
    if "admin" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can delete entries")
    await crud_teaching_methods.delete_teaching_methods(db, id)
    return None

@router.get("/teaching-methods/summary/{faculty_id}")
async def read_teaching_methods_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    faculty_id: str = Path(...)
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    total_score = await crud_teaching_methods.get_teaching_methods_total_score(db, faculty_id)
    return {"totalScore": total_score}
