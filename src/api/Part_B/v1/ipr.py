from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Annotated
from datetime import date

from ....setup.dependencies import get_db, CurrentUser
from ....setup.storage_utils import upload_file_to_supabase
from ....schema.Part_B.ipr import (
    IPRCreate,
    IPRUpdateFaculty,
    IPRUpdateHOD,
    IPRUpdateDirector,
    IPRResponse,
    IPRSummary,
)
from ....crud.Part_B import ipr as crud_ipr
from ....models.Part_B.ipr import IPR as DBIPR

router = APIRouter()

@router.post("/ipr", response_model=IPRResponse, status_code=status.HTTP_201_CREATED)
async def create_ipr(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    title: Annotated[str, Form()] = ...,
    scope: Annotated[str, Form()] = ...,
    filing_date: Annotated[date, Form()] = ...,
    status: Annotated[str, Form()] = ...,
    patent_file_no: Annotated[str, Form()] = ...,
    department: Annotated[Optional[str], Form()] = None,
    file: Optional[UploadFile] = File(None)
):
    if "faculty" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create IPR entries")
    
    document_path = None
    if file:
        document_path = await upload_file_to_supabase(file, current_user.id)
    
    ipr = IPRCreate(
        title=title,
        scope=scope,
        filing_date=filing_date,
        status=status,
        patent_file_no=patent_file_no,
        department=department,
        document=document_path
    )
    
    return await crud_ipr.create_ipr(db=db, ipr=ipr, faculty_id=current_user.id)

@router.get("/ipr/faculty/{faculty_id}", response_model=List[IPRResponse])
async def read_ipr_by_faculty(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    faculty_id: str = Path(...),
    skip: int = Query(0),
    limit: int = Query(100)
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this faculty's IPR entries")
    
    ipr_entries = await crud_ipr.get_ipr_by_faculty(db, faculty_id=faculty_id, skip=skip, limit=limit)
    return ipr_entries

@router.get("/ipr", response_model=List[IPRResponse])
async def read_all_ipr(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    skip: int = Query(0),
    limit: int = Query(100)
):
    if not any(role in ["admin", "dean", "vc"] for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view all IPR entries")
    
    ipr_entries = await crud_ipr.get_all_ipr(db, skip=skip, limit=limit)
    return ipr_entries

@router.put("/ipr/{ipr_id}", response_model=IPRResponse)
async def update_ipr(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    ipr_id: str = Path(...),
    ipr_update: IPRUpdateFaculty = None
):
    db_ipr = await crud_ipr.get_ipr(db, ipr_id)
    if db_ipr is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="IPR entry not found")

    if not current_user.has_authority_over(db_ipr.faculty_id, "faculty", getattr(db_ipr, "department", None)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this IPR entry")

    # Role-based update logic
    if "admin" in current_user.roles:
        updated_ipr = await crud_ipr.update_ipr_faculty(db, ipr_id, ipr_update)
    elif "hod" in current_user.roles:
        updated_ipr = await crud_ipr.update_ipr_hod(db, ipr_id, ipr_update)
    elif "director" in current_user.roles:
        updated_ipr = await crud_ipr.update_ipr_director(db, ipr_id, ipr_update)
    elif "faculty" in current_user.roles and db_ipr.faculty_id == current_user.id:
        updated_ipr = await crud_ipr.update_ipr_faculty(db, ipr_id, ipr_update)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this IPR entry")

    if updated_ipr is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update IPR entry")
    return updated_ipr

@router.delete("/ipr/{ipr_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ipr(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    ipr_id: str = Path(...)
):
    db_ipr = await crud_ipr.get_ipr(db, ipr_id)
    if db_ipr is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="IPR entry not found")

    if not current_user.has_authority_over(db_ipr.faculty_id, "faculty", getattr(db_ipr, "department", None)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this IPR entry")
    
    await crud_ipr.delete_ipr(db, ipr_id)
    return {"message": "IPR entry deleted successfully"}

@router.get("/ipr/summary/{faculty_id}", response_model=IPRSummary)
async def get_ipr_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    faculty_id: str = Path(...)
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this faculty's summary")
    
    total_score = await crud_ipr.get_ipr_total_score(db, faculty_id)
    return IPRSummary(total_score=total_score)
