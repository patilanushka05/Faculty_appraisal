from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Annotated

from ....setup.dependencies import get_db, CurrentUser
from ....setup.storage_utils import upload_file_to_supabase
from ....schema.Part_B.research_proposal import (
    ResearchProposalCreate,
    ResearchProposalUpdateFaculty,
    ResearchProposalUpdateHOD,
    ResearchProposalUpdateDirector,
    ResearchProposalResponse,
    ResearchProposalSummary,
)
from ....crud.Part_B import research_proposal as crud_research_proposal

router = APIRouter()

@router.post("/research-proposals", response_model=ResearchProposalResponse, status_code=status.HTTP_201_CREATED)
async def create_research_proposal(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    proposal_title: Annotated[str, Form(...)],
    duration: Annotated[str, Form(...)],
    funding_agency: Annotated[str, Form(...)],
    grant_amount: Annotated[float, Form(...)],
    department: Annotated[Optional[str], Form()] = None,
    file: Annotated[Optional[UploadFile], File()] = None,
):
    if "faculty" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create research proposals")
    
    document_path = None
    if file:
        document_path = await upload_file_to_supabase(file, current_user.id)
    
    proposal = ResearchProposalCreate(
        proposal_title=proposal_title,
        duration=duration,
        funding_agency=funding_agency,
        grant_amount=grant_amount,
        department=department,
        document=document_path
    )
    
    return await crud_research_proposal.create_research_proposal(db=db, proposal=proposal, faculty_id=current_user.id)

@router.get("/research-proposals/faculty/{faculty_id}", response_model=List[ResearchProposalResponse])
async def read_research_proposals_by_faculty(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(...)],
    skip: int = 0,
    limit: int = 100,
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this faculty's research proposals")
    
    proposals = await crud_research_proposal.get_research_proposals_by_faculty(db, faculty_id=faculty_id, skip=skip, limit=limit)
    return proposals

@router.get("/research-proposals", response_model=List[ResearchProposalResponse])
async def read_all_research_proposals(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
):
    if not any(role in ["admin", "dean", "vc"] for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view all research proposals")
    
    proposals = await crud_research_proposal.get_all_research_proposals(db, skip=skip, limit=limit)
    return proposals

@router.put("/research-proposals/{proposal_id}", response_model=ResearchProposalResponse)
async def update_research_proposal(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    proposal_id: Annotated[str, Path(...)],
    proposal_update: ResearchProposalUpdateFaculty | ResearchProposalUpdateHOD | ResearchProposalUpdateDirector,
):
    db_proposal = await crud_research_proposal.get_research_proposal(db, proposal_id)
    if db_proposal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research Proposal not found")

    if not current_user.has_authority_over(db_proposal.faculty_id, "faculty", getattr(db_proposal, "department", None)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this research proposal")

    # Role-based update logic
    if "admin" in current_user.roles:
        updated_proposal = await crud_research_proposal.update_research_proposal_faculty(db, proposal_id, proposal_update)
    elif "hod" in current_user.roles:
        if not isinstance(proposal_update, ResearchProposalUpdateHOD):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="HOD can only update api_score_hod")
        updated_proposal = await crud_research_proposal.update_research_proposal_hod(db, proposal_id, proposal_update)
    elif "director" in current_user.roles:
        if not isinstance(proposal_update, ResearchProposalUpdateDirector):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Director can only update api_score_director")
        updated_proposal = await crud_research_proposal.update_research_proposal_director(db, proposal_id, proposal_update)
    elif "faculty" in current_user.roles and db_proposal.faculty_id == current_user.id:
        updated_proposal = await crud_research_proposal.update_research_proposal_faculty(db, proposal_id, proposal_update)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this research proposal")

    if updated_proposal is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update research proposal")
    return updated_proposal

@router.delete("/research-proposals/{proposal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_research_proposal(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    proposal_id: Annotated[str, Path(...)],
):
    db_proposal = await crud_research_proposal.get_research_proposal(db, proposal_id)
    if db_proposal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research Proposal not found")

    if not current_user.has_authority_over(db_proposal.faculty_id, "faculty", getattr(db_proposal, "department", None)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this research proposal")
    
    await crud_research_proposal.delete_research_proposal(db, proposal_id)
    return {"message": "Research Proposal deleted successfully"}

@router.get("/research-proposals/summary/{faculty_id}", response_model=ResearchProposalSummary)
async def get_research_proposals_summary(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(...)],
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this faculty's summary")
    
    total_score = await crud_research_proposal.get_research_proposals_total_score(db, faculty_id)
    return ResearchProposalSummary(total_score=total_score)
