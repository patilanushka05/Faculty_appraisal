from ...utils import mask_scores
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Annotated, Union
from uuid import UUID

from ....setup.dependencies import get_db, CurrentUser
from ....setup.storage_utils import upload_file_to_supabase
from ....schema.Part_B.popular_writings import (
    PopularWritingsCreate,
    PopularWritingsResponse,
    PopularWritingsSummary,
    PopularWritingsUpdateFaculty,
    PopularWritingsUpdateHOD,
    PopularWritingsUpdateDirector,
    PopularWritingsUpdateDean,
    PopularWritingsUpdateVC,
)
from ....crud.Part_B import popular_writings as crud_popular_writings

router = APIRouter()

@router.post("/popular-writings", response_model=PopularWritingsResponse, status_code=status.HTTP_201_CREATED)
async def create_popular_writing(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    title: Annotated[str, Form(...)],
    writing_type: Annotated[str, Form(...)],
    date: Annotated[str, Form(...)],
    publisher_agency: Annotated[Optional[str], Form()] = None,
    sr_no: Annotated[Optional[int], Form()] = None,
    department: Annotated[Optional[str], Form()] = None,
    file: Annotated[Optional[UploadFile], File()] = None,
):
    if "faculty" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create entries")
    
    document_path = None
    if file:
        document_path = await upload_file_to_supabase(file, current_user.id)
    
    writing_data = PopularWritingsCreate(
        title=title,
        writing_type=writing_type,
        date=date,
        publisher_agency=publisher_agency,
        sr_no=sr_no,
        department=department,
        document=document_path
    )
    
    return mask_scores(await crud_popular_writings.create_popular_writing(db=db, writing=writing_data, faculty_id=current_user.id), current_user)

@router.get("/popular-writings/faculty/{faculty_id}", response_model=List[PopularWritingsResponse])
async def read_popular_writings_by_faculty(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[UUID, Path(...)],
    skip: int = 0,
    limit: int = 100,
):
    if not current_user.has_authority_over(str(faculty_id), "faculty"):
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    return mask_scores(await crud_popular_writings.get_popular_writings_by_faculty(db, faculty_id=faculty_id, skip=skip, limit=limit), current_user)

@router.get("/popular-writings/{writing_id}", response_model=PopularWritingsResponse)
async def read_popular_writing(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    writing_id: Annotated[UUID, Path(...)],
):
    db_writing = await crud_popular_writings.get_popular_writing(db, writing_id)
    if not db_writing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        
    if not current_user.has_authority_over(str(db_writing.faculty_id), "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        
    return mask_scores(db_writing, current_user)

@router.put("/popular-writings/{writing_id}", response_model=PopularWritingsResponse)
async def update_popular_writing(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    writing_id: Annotated[UUID, Path(...)],
    writing_update: Union[PopularWritingsUpdateFaculty, PopularWritingsUpdateHOD, PopularWritingsUpdateDirector, PopularWritingsUpdateDean, PopularWritingsUpdateVC],
):
    db_writing = await crud_popular_writings.get_popular_writing(db, writing_id)
    if not db_writing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if not current_user.has_authority_over(str(db_writing.faculty_id), "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    if "admin" in current_user.roles:
        res = await crud_popular_writings.update_popular_writing_faculty(db, writing_id, writing_update)
    elif "vc" in current_user.roles:
        res = await crud_popular_writings.update_popular_writing_vc(db, writing_id, writing_update)
    elif "dean" in current_user.roles:
        res = await crud_popular_writings.update_popular_writing_dean(db, writing_id, writing_update)
    elif "director" in current_user.roles:
        res = await crud_popular_writings.update_popular_writing_director(db, writing_id, writing_update)
    elif "hod" in current_user.roles:
        res = await crud_popular_writings.update_popular_writing_hod(db, writing_id, writing_update)
    elif "faculty" in current_user.roles and str(db_writing.faculty_id) == str(current_user.id):
        res = await crud_popular_writings.update_popular_writing_faculty(db, writing_id, writing_update)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return mask_scores(res, current_user)

@router.delete("/popular-writings/{writing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_popular_writing(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    writing_id: Annotated[UUID, Path(...)],
):
    db_writing = await crud_popular_writings.get_popular_writing(db, writing_id)
    if not db_writing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if str(db_writing.faculty_id) != str(current_user.id) and "admin" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    await crud_popular_writings.delete_popular_writing(db, writing_id)
    return None

@router.get("/popular-writings/summary/{faculty_id}", response_model=PopularWritingsSummary)
async def get_popular_writings_summary(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[UUID, Path(...)],
):
    if not current_user.has_authority_over(str(faculty_id), "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    total_score = await crud_popular_writings.get_popular_writings_total_score(db, faculty_id)
    return PopularWritingsSummary(total_score=total_score)
