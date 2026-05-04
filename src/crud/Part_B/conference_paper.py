from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from src.models.Part_B.conference_paper import ConferencePaper
from src.schema.Part_B.conference_paper import (
    ConferencePaperCreate,
    ConferencePaperUpdateFaculty,
    ConferencePaperUpdateHOD,
    ConferencePaperUpdateDirector,
)

async def get_conference_paper(db: AsyncSession, paper_id: str) -> Optional[ConferencePaper]:
    result = await db.execute(select(ConferencePaper).where(ConferencePaper.id == paper_id))
    return result.scalars().first()

async def get_conference_papers_by_faculty(db: AsyncSession, faculty_id: str, skip: int = 0, limit: int = 100) -> List[ConferencePaper]:
    result = await db.execute(select(ConferencePaper).where(ConferencePaper.faculty_id == faculty_id).offset(skip).limit(limit))
    return result.scalars().all()

async def get_all_conference_papers(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ConferencePaper]:
    result = await db.execute(select(ConferencePaper).offset(skip).limit(limit))
    return result.scalars().all()

async def create_conference_paper(db: AsyncSession, paper: ConferencePaperCreate, faculty_id: str) -> ConferencePaper:
    db_paper = ConferencePaper(**paper.model_dump(), faculty_id=faculty_id)
    db.add(db_paper)
    await db.commit()
    await db.refresh(db_paper)
    return db_paper

async def update_conference_paper_faculty(
    db: AsyncSession, paper_id: str, paper_update: ConferencePaperUpdateFaculty
) -> Optional[ConferencePaper]:
    db_paper = await get_conference_paper(db, paper_id)
    if db_paper:
        update_data = paper_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_paper, key, value)
        await db.commit()
        await db.refresh(db_paper)
    return db_paper

async def update_conference_paper_hod(
    db: AsyncSession, paper_id: str, paper_update: ConferencePaperUpdateHOD
) -> Optional[ConferencePaper]:
    db_paper = await get_conference_paper(db, paper_id)
    if db_paper:
        db_paper.research_score_hod = paper_update.research_score_hod
        await db.commit()
        await db.refresh(db_paper)
    return db_paper

async def update_conference_paper_director(
    db: AsyncSession, paper_id: str, paper_update: ConferencePaperUpdateDirector
) -> Optional[ConferencePaper]:
    db_paper = await get_conference_paper(db, paper_id)
    if db_paper:
        db_paper.research_score_director = paper_update.research_score_director
        await db.commit()
        await db.refresh(db_paper)
    return db_paper

async def delete_conference_paper(db: AsyncSession, paper_id: str) -> Optional[ConferencePaper]:
    db_paper = await get_conference_paper(db, paper_id)
    if db_paper:
        await db.delete(db_paper)
        await db.commit()
    return db_paper

async def get_conference_papers_total_score(db: AsyncSession, faculty_id: str) -> float:
    result = await db.execute(select(ConferencePaper).where(ConferencePaper.faculty_id == faculty_id))
    papers = result.scalars().all()
    total_score = sum([paper.research_score_faculty or 0.0 for paper in papers])
    return total_score
