from ...utils import mask_scores
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Annotated

from ....setup.dependencies import get_db, CurrentUser
from ....setup.storage_utils import upload_file_to_supabase
from ....schema.Part_B.self_development_fdp import (
    SelfDevelopmentFDPCreate,
    SelfDevelopmentFDPResponse,
    SelfDevelopmentFDPSummary,
    SelfDevelopmentFDPUpdateFaculty,
    SelfDevelopmentFDPUpdateHOD,
    SelfDevelopmentFDPUpdateDirector,
    SelfDevelopmentFDPUpdateDean,
    SelfDevelopmentFDPUpdateVC,
)
from ....crud.Part_B import self_development_fdp as crud_self_development_fdp

router = APIRouter()

@router.post("/self-development", response_model=SelfDevelopmentFDPResponse, status_code=status.HTTP_201_CREATED)
async def create_self_development_fdp(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    program_name: Annotated[str, Form(...)],
    duration_days: Annotated[int, Form(...)],
    organizer: Annotated[str, Form(...)],
    department: Annotated[Optional[str], Form()] = None,
    file: Annotated[Optional[UploadFile], File()] = None,
):
    if "faculty" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create self-development FDP entries")
    
    document_path = None
    if file:
        document_path = await upload_file_to_supabase(file, current_user.id)
    
    fdp = SelfDevelopmentFDPCreate(
        program_name=program_name,
        duration_days=duration_days,
        organizer=organizer,
        department=department,
        document=document_path
    )
    
    return mask_scores(await crud_self_development_fdp.create_self_development_fdp(db=db, fdp=fdp, faculty_id=current_user.id), current_user)

@router.get("/self-development/faculty/{faculty_id}", response_model=List[SelfDevelopmentFDPResponse])
async def read_self_development_fdp_by_faculty(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(...)],
    skip: int = 0,
    limit: int = 100,
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this faculty's self-development FDP entries")
    
    fdp_entries = await crud_self_development_fdp.get_self_development_fdp_by_faculty(db, faculty_id=faculty_id, skip=skip, limit=limit)
    return mask_scores(fdp_entries, current_user)

@router.get("/self-development", response_model=List[SelfDevelopmentFDPResponse])
async def read_all_self_development_fdp(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
):
    if not any(role in ["admin", "dean", "vc"] for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view all self-development FDP entries")
    
    fdp_entries = await crud_self_development_fdp.get_all_self_development_fdp(db, skip=skip, limit=limit)
    return mask_scores(fdp_entries, current_user)

@router.put("/self-development/{fdp_id}", response_model=SelfDevelopmentFDPResponse)
async def update_self_development_fdp(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    fdp_id: Annotated[str, Path(...)],
    fdp_update: SelfDevelopmentFDPUpdateFaculty | SelfDevelopmentFDPUpdateHOD | SelfDevelopmentFDPUpdateDirector | SelfDevelopmentFDPUpdateDean | SelfDevelopmentFDPUpdateVC,
):
    db_fdp = await crud_self_development_fdp.get_self_development_fdp(db, fdp_id)
    if db_fdp is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Self-Development FDP entry not found")

    if not current_user.has_authority_over(db_fdp.faculty_id, "faculty", getattr(db_fdp, "department", None)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this self-development FDP entry")

    # Role-based update logic
    if "admin" in current_user.roles:
        updated_fdp = await crud_self_development_fdp.update_self_development_fdp_faculty(db, fdp_id, fdp_update)
    elif "vc" in current_user.roles:
        updated_fdp = await crud_self_development_fdp.update_self_development_fdp_vc(db, fdp_id, fdp_update)
    elif "dean" in current_user.roles:
        updated_fdp = await crud_self_development_fdp.update_self_development_fdp_dean(db, fdp_id, fdp_update)
    elif "director" in current_user.roles:
        updated_fdp = await crud_self_development_fdp.update_self_development_fdp_director(db, fdp_id, fdp_update)
    elif "hod" in current_user.roles:
        updated_fdp = await crud_self_development_fdp.update_self_development_fdp_hod(db, fdp_id, fdp_update)
    elif "faculty" in current_user.roles and db_fdp.faculty_id == current_user.id:
        updated_fdp = await crud_self_development_fdp.update_self_development_fdp_faculty(db, fdp_id, fdp_update)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this self-development FDP entry")

    if updated_fdp is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update self-development FDP entry")
    return mask_scores(updated_fdp, current_user)

@router.delete("/self-development/{fdp_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_self_development_fdp(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    fdp_id: Annotated[str, Path(...)],
):
    db_fdp = await crud_self_development_fdp.get_self_development_fdp(db, fdp_id)
    if db_fdp is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Self-Development FDP entry not found")

    if not current_user.has_authority_over(db_fdp.faculty_id, "faculty", getattr(db_fdp, "department", None)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this self-development FDP entry")
    
    await crud_self_development_fdp.delete_self_development_fdp(db, fdp_id)
    return {"message": "Self-Development FDP entry deleted successfully"}

@router.get("/self-development/summary/{faculty_id}", response_model=SelfDevelopmentFDPSummary)
async def get_self_development_fdp_summary(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(...)],
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this faculty's summary")
    
    total_score = await crud_self_development_fdp.get_self_development_fdp_total_score(db, faculty_id)
    return SelfDevelopmentFDPSummary(total_score=total_score)
