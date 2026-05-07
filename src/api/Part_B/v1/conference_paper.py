from ...utils import mask_scores
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Annotated
from datetime import date

from ....setup.dependencies import get_db, CurrentUser
from ....setup.storage_utils import upload_file_to_supabase
from ....schema.Part_B.conference_paper import (
    ConferencePaperCreate,
    ConferencePaperUpdateFaculty,
    ConferencePaperUpdateHOD,
    ConferencePaperUpdateDirector,
    ConferencePaperUpdateDean,
    ConferencePaperUpdateVC,
    ConferencePaperResponse,
    ConferencePaperSummary,)
from ....crud.Part_B import conference_paper as crud_conference_paper
from ....models.Part_B.conference_paper import ConferencePaper as DBConferencePaper

router = APIRouter()

@router.post("/conferences", response_model=ConferencePaperResponse, status_code=status.HTTP_201_CREATED)
async def create_conference_paper(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    event_title: Annotated[str, Form()] = ...,
    event_date: Annotated[date, Form()] = ...,
    activity_type: Annotated[str, Form()] = ...,
    hosting_organization: Annotated[str, Form()] = ...,
    event_level: Annotated[str, Form()] = ...,
    department: Annotated[Optional[str], Form()] = None,
    file: Optional[UploadFile] = File(None)
):
    if "faculty" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create conference papers")
    
    document_path = None
    if file:
        document_path = await upload_file_to_supabase(file, current_user.id)
    
    paper = ConferencePaperCreate(
        event_title=event_title,
        event_date=event_date,
        activity_type=activity_type,
        hosting_organization=hosting_organization,
        event_level=event_level,
        department=department,
        document=document_path
    )
    
    return mask_scores(await crud_conference_paper.create_conference_paper(db=db, paper=paper, faculty_id=current_user.id), current_user)

@router.get("/conferences/faculty/{faculty_id}", response_model=List[ConferencePaperResponse])
async def read_conference_papers_by_faculty(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    faculty_id: str = Path(...),
    skip: int = Query(0),
    limit: int = Query(100)
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this faculty's conference papers")
    
    papers = await crud_conference_paper.get_conference_papers_by_faculty(db, faculty_id=faculty_id, skip=skip, limit=limit)
    return papers

@router.get("/conferences", response_model=List[ConferencePaperResponse])
async def read_all_conference_papers(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    skip: int = Query(0),
    limit: int = Query(100)
):
    if not any(role in ["admin", "dean", "vc"] for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view all conference papers")
    
    papers = await crud_conference_paper.get_all_conference_papers(db, skip=skip, limit=limit)
    return papers

@router.put("/conferences/{paper_id}", response_model=ConferencePaperResponse)
async def update_conference_paper(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    paper_id: str = Path(...),
    paper_update: ConferencePaperUpdateFaculty | ConferencePaperUpdateHOD | ConferencePaperUpdateDirector | ConferencePaperUpdateDean | ConferencePaperUpdateVC = None
):
    db_paper = await crud_conference_paper.get_conference_paper(db, paper_id)
    if db_paper is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference Paper not found")

    if not current_user.has_authority_over(db_paper.faculty_id, "faculty", getattr(db_paper, "department", None)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this conference paper")

    # Role-based update logic
    if "vc" in current_user.roles:
        if not isinstance(paper_update, ConferencePaperUpdateVC):
             raise HTTPException(status_code=400, detail="Invalid update schema for VC")
        updated_paper = await crud_conference_paper.update_conference_paper_vc(db, paper_id, paper_update)
    elif "dean" in current_user.roles:
        if not isinstance(paper_update, ConferencePaperUpdateDean):
             raise HTTPException(status_code=400, detail="Invalid update schema for Dean")
        updated_paper = await crud_conference_paper.update_conference_paper_dean(db, paper_id, paper_update)
    elif "admin" in current_user.roles:
        updated_paper = await crud_conference_paper.update_conference_paper_faculty(db, paper_id, paper_update)
    elif "hod" in current_user.roles:
        updated_paper = await crud_conference_paper.update_conference_paper_hod(db, paper_id, paper_update)
    elif "director" in current_user.roles:
        updated_paper = await crud_conference_paper.update_conference_paper_director(db, paper_id, paper_update)
    elif "faculty" in current_user.roles and db_paper.faculty_id == current_user.id:
        updated_paper = await crud_conference_paper.update_conference_paper_faculty(db, paper_id, paper_update)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this conference paper")

    if updated_paper is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update conference paper")
    return updated_paper

@router.delete("/conferences/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conference_paper(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    paper_id: str = Path(...)
):
    db_paper = await crud_conference_paper.get_conference_paper(db, paper_id)
    if db_paper is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference Paper not found")

    if not current_user.has_authority_over(db_paper.faculty_id, "faculty", getattr(db_paper, "department", None)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this conference paper")
    
    await crud_conference_paper.delete_conference_paper(db, paper_id)
    return {"message": "Conference Paper deleted successfully"}

@router.get("/conferences/summary/{faculty_id}", response_model=ConferencePaperSummary)
async def get_conference_papers_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    faculty_id: str = Path(...)
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this faculty's summary")
    
    total_score = await crud_conference_paper.get_conference_papers_total_score(db, faculty_id)
    return ConferencePaperSummary(total_score=total_score)
