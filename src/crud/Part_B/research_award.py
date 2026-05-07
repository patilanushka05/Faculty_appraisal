from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from src.models.Part_B.research_award import ResearchAward
from src.schema.Part_B.research_award import (
    ResearchAwardCreate,
    ResearchAwardUpdateFaculty,
    ResearchAwardUpdateHOD,
    ResearchAwardUpdateDirector,
    ResearchAwardUpdateDean,
    ResearchAwardUpdateVC,)

async def get_research_award(db: AsyncSession, award_id: str) -> Optional[ResearchAward]:
    result = await db.execute(select(ResearchAward).where(ResearchAward.id == award_id))
    return result.scalars().first()

async def get_research_awards_by_faculty(db: AsyncSession, faculty_id: str, skip: int = 0, limit: int = 100) -> List[ResearchAward]:
    result = await db.execute(select(ResearchAward).where(ResearchAward.faculty_id == faculty_id).offset(skip).limit(limit))
    return result.scalars().all()

async def get_all_research_awards(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ResearchAward]:
    result = await db.execute(select(ResearchAward).offset(skip).limit(limit))
    return result.scalars().all()

async def create_research_award(db: AsyncSession, award: ResearchAwardCreate, faculty_id: str) -> ResearchAward:
    db_award = ResearchAward(**award.model_dump(), faculty_id=faculty_id)
    db.add(db_award)
    await db.commit()
    await db.refresh(db_award)
    return db_award

async def update_research_award_faculty(
    db: AsyncSession, award_id: str, award_update: ResearchAwardUpdateFaculty
) -> Optional[ResearchAward]:
    db_award = await get_research_award(db, award_id)
    if db_award:
        update_data = award_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_award, key, value)
        await db.commit()
        await db.refresh(db_award)
    return db_award

async def update_research_award_hod(
    db: AsyncSession, award_id: str, award_update: ResearchAwardUpdateHOD
) -> Optional[ResearchAward]:
    db_award = await get_research_award(db, award_id)
    if db_award:
        db_award.research_score_hod = award_update.research_score_hod
        await db.commit()
        await db.refresh(db_award)
    return db_award

async def update_research_award_director(
    db: AsyncSession, award_id: str, award_update: ResearchAwardUpdateDirector
) -> Optional[ResearchAward]:
    db_award = await get_research_award(db, award_id)
    if db_award:
        db_award.research_score_director = award_update.research_score_director
        await db.commit()
        await db.refresh(db_award)
    return db_award

async def delete_research_award(db: AsyncSession, award_id: str) -> Optional[ResearchAward]:
    db_award = await get_research_award(db, award_id)
    if db_award:
        await db.delete(db_award)
        await db.commit()
    return db_award

async def get_research_awards_total_score(db: AsyncSession, faculty_id: str) -> float:
    result = await db.execute(select(ResearchAward).where(ResearchAward.faculty_id == faculty_id))
    awards = result.scalars().all()
    total_score = sum([award.research_score_faculty or 0.0 for award in awards])
    return total_score

async def update_research_award_dean(
    db: AsyncSession, id: str, update: ResearchAwardUpdateDean
) -> Optional[ResearchAward]:
    db_obj = await get_research_award(db, id)
    if db_obj:
        db_obj.api_score_dean = update.api_score_dean
        await db.commit()
        await db.refresh(db_obj)
    return db_obj

async def update_research_award_vc(
    db: AsyncSession, id: str, update: ResearchAwardUpdateVC
) -> Optional[ResearchAward]:
    db_obj = await get_research_award(db, id)
    if db_obj:
        db_obj.api_score_vc = update.api_score_vc
        await db.commit()
        await db.refresh(db_obj)
    return db_obj
