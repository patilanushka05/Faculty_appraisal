from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Annotated
from datetime import date

from ....setup.dependencies import get_db, CurrentUser
from ....setup.storage_utils import upload_file_to_supabase
from ....schema.Part_B.research_award import (
    ResearchAwardCreate,
    ResearchAwardUpdateFaculty,
    ResearchAwardUpdateHOD,
    ResearchAwardUpdateDirector,
    ResearchAwardResponse,
    ResearchAwardSummary,
)
from ....crud.Part_B import research_award as crud_research_award

router = APIRouter()

@router.post("/research-awards", response_model=ResearchAwardResponse, status_code=status.HTTP_201_CREATED)
async def create_research_award(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    award_name: Annotated[str, Form(...)],
    award_date: Annotated[date, Form(...)],
    awarding_agency: Annotated[str, Form(...)],
    level: Annotated[str, Form(...)],
    department: Annotated[Optional[str], Form()] = None,
    file: Annotated[Optional[UploadFile], File()] = None,
):
    if "faculty" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create research awards")
    
    document_path = None
    if file:
        document_path = await upload_file_to_supabase(file, current_user.id)
    
    award = ResearchAwardCreate(
        award_name=award_name,
        award_date=award_date,
        awarding_agency=awarding_agency,
        level=level,
        department=department,
        document=document_path
    )
    
    return await crud_research_award.create_research_award(db=db, award=award, faculty_id=current_user.id)

@router.get("/research-awards/faculty/{faculty_id}", response_model=List[ResearchAwardResponse])
async def read_research_awards_by_faculty(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(...)],
    skip: int = 0,
    limit: int = 100,
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this faculty's research awards")
    
    awards = await crud_research_award.get_research_awards_by_faculty(db, faculty_id=faculty_id, skip=skip, limit=limit)
    return awards

@router.get("/research-awards", response_model=List[ResearchAwardResponse])
async def read_all_research_awards(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
):
    if not any(role in ["admin", "dean", "vc"] for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view all research awards")
    
    awards = await crud_research_award.get_all_research_awards(db, skip=skip, limit=limit)
    return awards

@router.put("/research-awards/{award_id}", response_model=ResearchAwardResponse)
async def update_research_award(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    award_id: Annotated[str, Path(...)],
    award_update: ResearchAwardUpdateFaculty | ResearchAwardUpdateHOD | ResearchAwardUpdateDirector,
):
    db_award = await crud_research_award.get_research_award(db, award_id)
    if db_award is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research Award not found")

    if not current_user.has_authority_over(db_award.faculty_id, "faculty", getattr(db_award, "department", None)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this research award")

    # Role-based update logic
    if "admin" in current_user.roles:
        updated_award = await crud_research_award.update_research_award_faculty(db, award_id, award_update)
    elif "hod" in current_user.roles:
        if not isinstance(award_update, ResearchAwardUpdateHOD):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="HOD can only update research_score_hod")
        updated_award = await crud_research_award.update_research_award_hod(db, award_id, award_update)
    elif "director" in current_user.roles:
        if not isinstance(award_update, ResearchAwardUpdateDirector):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Director can only update research_score_director")
        updated_award = await crud_research_award.update_research_award_director(db, award_id, award_update)
    elif "faculty" in current_user.roles and db_award.faculty_id == current_user.id:
        updated_award = await crud_research_award.update_research_award_faculty(db, award_id, award_update)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this research award")

    if updated_award is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update research award")
    return updated_award

@router.delete("/research-awards/{award_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_research_award(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    award_id: Annotated[str, Path(...)],
):
    db_award = await crud_research_award.get_research_award(db, award_id)
    if db_award is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research Award not found")

    if not current_user.has_authority_over(db_award.faculty_id, "faculty", getattr(db_award, "department", None)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this research award")
    
    await crud_research_award.delete_research_award(db, award_id)
    return {"message": "Research Award deleted successfully"}

@router.get("/research-awards/summary/{faculty_id}", response_model=ResearchAwardSummary)
async def get_research_awards_summary(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(...)],
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this faculty's summary")
    
    total_score = await crud_research_award.get_research_awards_total_score(db, faculty_id)
    return ResearchAwardSummary(total_score=total_score)
