from ...utils import mask_scores
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Annotated

from ....setup.dependencies import get_db, CurrentUser
from ....setup.storage_utils import upload_file_to_supabase
from ....schema.Part_B.ict_pedagogy import (
    ICTPedagogyCreate,
    ICTPedagogyUpdateFaculty,
    ICTPedagogyUpdateHOD,
    ICTPedagogyUpdateDirector,
    ICTPedagogyUpdateDean,
    ICTPedagogyUpdateVC,
    ICTPedagogyResponse,
    ICTPedagogySummary,)
from ....crud.Part_B import ict_pedagogy as crud_ict_pedagogy
from ....models.Part_B.ict_pedagogy import ICTPedagogy as DBICTPedagogy

router = APIRouter()

@router.post("/pedagogy", response_model=ICTPedagogyResponse, status_code=status.HTTP_201_CREATED)
async def create_ict_pedagogy(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    title: Annotated[str, Form()] = ...,
    description: Annotated[str, Form()] = ...,
    pedagogy_type: Annotated[str, Form()] = ...,
    quadrants: Annotated[int, Form()] = ...,
    department: Annotated[Optional[str], Form()] = None,
    file: Optional[UploadFile] = File(None)
):
    if "faculty" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create ICT pedagogies")
    
    document_path = None
    if file:
        document_path = await upload_file_to_supabase(file, current_user.id)
    
    pedagogy = ICTPedagogyCreate(
        title=title,
        description=description,
        pedagogy_type=pedagogy_type,
        quadrants=quadrants,
        department=department,
        document=document_path
    )
    
    return mask_scores(await crud_ict_pedagogy.create_ict_pedagogy(db=db, pedagogy=pedagogy, faculty_id=current_user.id), current_user)

@router.get("/pedagogy/faculty/{faculty_id}", response_model=List[ICTPedagogyResponse])
async def read_ict_pedagogies_by_faculty(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    faculty_id: str = Path(...),
    skip: int = Query(0),
    limit: int = Query(100)
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this faculty's ICT pedagogies")
    
    pedagogies = await crud_ict_pedagogy.get_ict_pedagogies_by_faculty(db, faculty_id=faculty_id, skip=skip, limit=limit)
    return pedagogies

@router.get("/pedagogy", response_model=List[ICTPedagogyResponse])
async def read_all_ict_pedagogies(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    skip: int = Query(0),
    limit: int = Query(100)
):
    if not any(role in ["admin", "dean", "vc"] for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view all ICT pedagogies")
    
    pedagogies = await crud_ict_pedagogy.get_all_ict_pedagogies(db, skip=skip, limit=limit)
    return pedagogies

@router.put("/pedagogy/{pedagogy_id}", response_model=ICTPedagogyResponse)
async def update_ict_pedagogy(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    pedagogy_id: str = Path(...),
    pedagogy_update: ICTPedagogyUpdateFaculty | ICTPedagogyUpdateHOD | ICTPedagogyUpdateDirector | ICTPedagogyUpdateDean | ICTPedagogyUpdateVC = None
):
    db_pedagogy = await crud_ict_pedagogy.get_ict_pedagogy(db, pedagogy_id)
    if db_pedagogy is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ICT Pedagogy entry not found")

    if not current_user.has_authority_over(db_pedagogy.faculty_id, "faculty", getattr(db_pedagogy, "department", None)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this ICT pedagogy entry")

    # Role-based update logic
    if "vc" in current_user.roles:
        if not isinstance(pedagogy_update, ICTPedagogyUpdateVC):
             raise HTTPException(status_code=400, detail="Invalid update schema for VC")
        updated_pedagogy = await crud_ict_pedagogy.update_ict_pedagogy_vc(db, pedagogy_id, pedagogy_update)
    elif "dean" in current_user.roles:
        if not isinstance(pedagogy_update, ICTPedagogyUpdateDean):
             raise HTTPException(status_code=400, detail="Invalid update schema for Dean")
        updated_pedagogy = await crud_ict_pedagogy.update_ict_pedagogy_dean(db, pedagogy_id, pedagogy_update)
    elif "admin" in current_user.roles:
        updated_pedagogy = await crud_ict_pedagogy.update_ict_pedagogy_faculty(db, pedagogy_id, pedagogy_update)
    elif "hod" in current_user.roles:
        updated_pedagogy = await crud_ict_pedagogy.update_ict_pedagogy_hod(db, pedagogy_id, pedagogy_update)
    elif "director" in current_user.roles:
        updated_pedagogy = await crud_ict_pedagogy.update_ict_pedagogy_director(db, pedagogy_id, pedagogy_update)
    elif "faculty" in current_user.roles and db_pedagogy.faculty_id == current_user.id:
        updated_pedagogy = await crud_ict_pedagogy.update_ict_pedagogy_faculty(db, pedagogy_id, pedagogy_update)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this ICT pedagogy entry")

    if updated_pedagogy is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update ICT pedagogy entry")
    return updated_pedagogy

@router.delete("/pedagogy/{pedagogy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ict_pedagogy(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    pedagogy_id: str = Path(...)
):
    db_pedagogy = await crud_ict_pedagogy.get_ict_pedagogy(db, pedagogy_id)
    if db_pedagogy is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ICT Pedagogy entry not found")

    if not current_user.has_authority_over(db_pedagogy.faculty_id, "faculty", getattr(db_pedagogy, "department", None)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this ICT pedagogy entry")
    
    await crud_ict_pedagogy.delete_ict_pedagogy(db, pedagogy_id)
    return {"message": "ICT Pedagogy entry deleted successfully"}

@router.get("/pedagogy/summary/{faculty_id}", response_model=ICTPedagogySummary)
async def get_ict_pedagogies_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    faculty_id: str = Path(...)
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this faculty's summary")
    
    total_score = await crud_ict_pedagogy.get_ict_pedagogies_total_score(db, faculty_id)
    return ICTPedagogySummary(total_score=total_score)
