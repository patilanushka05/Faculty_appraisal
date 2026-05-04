from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Annotated
from datetime import date

from ....setup.dependencies import get_db, CurrentUser
from ....setup.storage_utils import upload_file_to_supabase
from ....schema.Part_B.research_guidance import (
    ResearchGuidanceCreate,
    ResearchGuidanceUpdateFaculty,
    ResearchGuidanceUpdateHOD,
    ResearchGuidanceUpdateDirector,
    ResearchGuidanceResponse,
    ResearchGuidanceSummary,
)
from ....crud.Part_B import research_guidance as crud_research_guidance

router = APIRouter()

@router.post("/research-guidance", response_model=ResearchGuidanceResponse, status_code=status.HTTP_201_CREATED)
async def create_research_guidance(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    degree: Annotated[str, Form(...)],
    student_name: Annotated[str, Form(...)],
    submission_status: Annotated[str, Form(...)],
    award_date: Annotated[Optional[date], Form()] = None,
    department: Annotated[Optional[str], Form()] = None,
    file: Annotated[Optional[UploadFile], File()] = None,
):
    if "faculty" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create research guidance entries")
    
    document_path = None
    if file:
        document_path = await upload_file_to_supabase(file, current_user.id)
    
    guidance = ResearchGuidanceCreate(
        degree=degree,
        student_name=student_name,
        submission_status=submission_status,
        award_date=award_date,
        department=department,
        document=document_path
    )
    
    return await crud_research_guidance.create_research_guidance(db=db, guidance=guidance, faculty_id=current_user.id)

@router.get("/research-guidance/faculty/{faculty_id}", response_model=List[ResearchGuidanceResponse])
async def read_research_guidance_by_faculty(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(...)],
    skip: int = 0,
    limit: int = 100,
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this faculty's research guidance entries")
    
    guidance_entries = await crud_research_guidance.get_research_guidance_by_faculty(db, faculty_id=faculty_id, skip=skip, limit=limit)
    return guidance_entries

@router.get("/research-guidance", response_model=List[ResearchGuidanceResponse])
async def read_all_research_guidance(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
):
    if not any(role in ["admin", "dean", "vc"] for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view all research guidance entries")
    
    guidance_entries = await crud_research_guidance.get_all_research_guidance(db, skip=skip, limit=limit)
    return guidance_entries

@router.put("/research-guidance/{guidance_id}", response_model=ResearchGuidanceResponse)
async def update_research_guidance(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    guidance_id: Annotated[str, Path(...)],
    guidance_update: ResearchGuidanceUpdateFaculty | ResearchGuidanceUpdateHOD | ResearchGuidanceUpdateDirector,
):
    db_guidance = await crud_research_guidance.get_research_guidance(db, guidance_id)
    if db_guidance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research Guidance entry not found")

    if not current_user.has_authority_over(db_guidance.faculty_id, "faculty", getattr(db_guidance, "department", None)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this research guidance entry")

    # Role-based update logic
    if "admin" in current_user.roles:
        updated_guidance = await crud_research_guidance.update_research_guidance_faculty(db, guidance_id, guidance_update)
    elif "hod" in current_user.roles:
        if not isinstance(guidance_update, ResearchGuidanceUpdateHOD):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="HOD can only update api_score_hod")
        updated_guidance = await crud_research_guidance.update_research_guidance_hod(db, guidance_id, guidance_update)
    elif "director" in current_user.roles:
        if not isinstance(guidance_update, ResearchGuidanceUpdateDirector):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Director can only update api_score_director")
        updated_guidance = await crud_research_guidance.update_research_guidance_director(db, guidance_id, guidance_update)
    elif "faculty" in current_user.roles and db_guidance.faculty_id == current_user.id:
        updated_guidance = await crud_research_guidance.update_research_guidance_faculty(db, guidance_id, guidance_update)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this research guidance entry")

    if updated_guidance is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update research guidance entry")
    return updated_guidance

@router.delete("/research-guidance/{guidance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_research_guidance(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    guidance_id: Annotated[str, Path(...)],
):
    db_guidance = await crud_research_guidance.get_research_guidance(db, guidance_id)
    if db_guidance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research Guidance entry not found")

    if not current_user.has_authority_over(db_guidance.faculty_id, "faculty", getattr(db_guidance, "department", None)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this research guidance entry")
    
    await crud_research_guidance.delete_research_guidance(db, guidance_id)
    return {"message": "Research Guidance entry deleted successfully"}

@router.get("/research-guidance/summary/{faculty_id}", response_model=ResearchGuidanceSummary)
async def get_research_guidance_summary(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(...)],
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this faculty's summary")
    
    summary_data = await crud_research_guidance.get_research_guidance_total_score(db, faculty_id)
    return ResearchGuidanceSummary(**summary_data)
