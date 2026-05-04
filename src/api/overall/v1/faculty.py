from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from ....setup.dependencies import get_db, CurrentUser
from ....schema.overall.faculty import FacultyResponse, FacultyUpdate
from ....crud.overall import faculty as crud_faculty

router = APIRouter()

@router.get("/profile", response_model=FacultyResponse)
async def get_my_profile(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Returns the profile details of the currently logged-in user.
    """
    db_faculty = await crud_faculty.get_faculty(db, current_user.id)
    if not db_faculty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faculty profile not found")
    return db_faculty

@router.get("/profile/{faculty_id}", response_model=FacultyResponse)
async def get_faculty_profile(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(...)],
):
    """
    Allows authorities (HOD, Director, Dean, VC) to view a subordinate's profile.
    """
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this profile")
    
    db_faculty = await crud_faculty.get_faculty(db, faculty_id)
    if not db_faculty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faculty profile not found")
    return db_faculty

@router.put("/profile", response_model=FacultyResponse)
async def update_my_profile(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_data: FacultyUpdate,
):
    """
    Updates the profile details of the currently logged-in user.
    """
    db_faculty = await crud_faculty.update_faculty(db, current_user.id, faculty_data)
    if not db_faculty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faculty profile not found")
    return db_faculty
