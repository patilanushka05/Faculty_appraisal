from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from src.models.Part_B.research_proposal import ResearchProposal
from src.schema.Part_B.research_proposal import (
    ResearchProposalCreate,
    ResearchProposalUpdateFaculty,
    ResearchProposalUpdateHOD,
    ResearchProposalUpdateDirector,
)

async def get_research_proposal(db: AsyncSession, proposal_id: str) -> Optional[ResearchProposal]:
    result = await db.execute(select(ResearchProposal).where(ResearchProposal.id == proposal_id))
    return result.scalars().first()

async def get_research_proposals_by_faculty(db: AsyncSession, faculty_id: str, skip: int = 0, limit: int = 100) -> List[ResearchProposal]:
    result = await db.execute(select(ResearchProposal).where(ResearchProposal.faculty_id == faculty_id).offset(skip).limit(limit))
    return result.scalars().all()

async def get_all_research_proposals(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ResearchProposal]:
    result = await db.execute(select(ResearchProposal).offset(skip).limit(limit))
    return result.scalars().all()

async def create_research_proposal(db: AsyncSession, proposal: ResearchProposalCreate, faculty_id: str) -> ResearchProposal:
    db_proposal = ResearchProposal(**proposal.model_dump(), faculty_id=faculty_id)
    db.add(db_proposal)
    await db.commit()
    await db.refresh(db_proposal)
    return db_proposal

async def update_research_proposal_faculty(
    db: AsyncSession, proposal_id: str, proposal_update: ResearchProposalUpdateFaculty
) -> Optional[ResearchProposal]:
    db_proposal = await get_research_proposal(db, proposal_id)
    if db_proposal:
        update_data = proposal_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_proposal, key, value)
        await db.commit()
        await db.refresh(db_proposal)
    return db_proposal

async def update_research_proposal_hod(
    db: AsyncSession, proposal_id: str, proposal_update: ResearchProposalUpdateHOD
) -> Optional[ResearchProposal]:
    db_proposal = await get_research_proposal(db, proposal_id)
    if db_proposal:
        db_proposal.api_score_hod = proposal_update.api_score_hod
        await db.commit()
        await db.refresh(db_proposal)
    return db_proposal

async def update_research_proposal_director(
    db: AsyncSession, proposal_id: str, proposal_update: ResearchProposalUpdateDirector
) -> Optional[ResearchProposal]:
    db_proposal = await get_research_proposal(db, proposal_id)
    if db_proposal:
        db_proposal.api_score_director = proposal_update.api_score_director
        await db.commit()
        await db.refresh(db_proposal)
    return db_proposal

async def delete_research_proposal(db: AsyncSession, proposal_id: str) -> Optional[ResearchProposal]:
    db_proposal = await get_research_proposal(db, proposal_id)
    if db_proposal:
        await db.delete(db_proposal)
        await db.commit()
    return db_proposal

async def get_research_proposals_total_score(db: AsyncSession, faculty_id: str) -> float:
    proposals = await get_research_proposals_by_faculty(db, faculty_id, limit=1000)
    total_score = sum([p.api_score_faculty or 0.0 for p in proposals])
    return total_score
