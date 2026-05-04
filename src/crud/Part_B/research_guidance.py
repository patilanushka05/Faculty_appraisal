from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from src.models.Part_B.research_guidance import ResearchGuidance
from src.schema.Part_B.research_guidance import (
    ResearchGuidanceCreate,
    ResearchGuidanceUpdateFaculty,
    ResearchGuidanceUpdateHOD,
    ResearchGuidanceUpdateDirector,
)

async def get_research_guidance(db: AsyncSession, guidance_id: str) -> Optional[ResearchGuidance]:
    result = await db.execute(select(ResearchGuidance).where(ResearchGuidance.id == guidance_id))
    return result.scalars().first()

async def get_research_guidance_by_faculty(db: AsyncSession, faculty_id: str, skip: int = 0, limit: int = 100) -> List[ResearchGuidance]:
    result = await db.execute(select(ResearchGuidance).where(ResearchGuidance.faculty_id == faculty_id).offset(skip).limit(limit))
    return result.scalars().all()

async def get_all_research_guidance(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ResearchGuidance]:
    result = await db.execute(select(ResearchGuidance).offset(skip).limit(limit))
    return result.scalars().all()

async def create_research_guidance(db: AsyncSession, guidance: ResearchGuidanceCreate, faculty_id: str) -> ResearchGuidance:
    db_guidance = ResearchGuidance(**guidance.model_dump(), faculty_id=faculty_id)
    db.add(db_guidance)
    await db.commit()
    await db.refresh(db_guidance)
    return db_guidance

async def update_research_guidance_faculty(
    db: AsyncSession, guidance_id: str, guidance_update: ResearchGuidanceUpdateFaculty
) -> Optional[ResearchGuidance]:
    db_guidance = await get_research_guidance(db, guidance_id)
    if db_guidance:
        update_data = guidance_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_guidance, key, value)
        await db.commit()
        await db.refresh(db_guidance)
    return db_guidance

async def update_research_guidance_hod(
    db: AsyncSession, guidance_id: str, guidance_update: ResearchGuidanceUpdateHOD
) -> Optional[ResearchGuidance]:
    db_guidance = await get_research_guidance(db, guidance_id)
    if db_guidance:
        db_guidance.api_score_hod = guidance_update.api_score_hod
        await db.commit()
        await db.refresh(db_guidance)
    return db_guidance

async def update_research_guidance_director(
    db: AsyncSession, guidance_id: str, guidance_update: ResearchGuidanceUpdateDirector
) -> Optional[ResearchGuidance]:
    db_guidance = await get_research_guidance(db, guidance_id)
    if db_guidance:
        db_guidance.api_score_director = guidance_update.api_score_director
        await db.commit()
        await db.refresh(db_guidance)
    return db_guidance

async def delete_research_guidance(db: AsyncSession, guidance_id: str) -> Optional[ResearchGuidance]:
    db_guidance = await get_research_guidance(db, guidance_id)
    if db_guidance:
        await db.delete(db_guidance)
        await db.commit()
    return db_guidance

async def get_research_guidance_total_score(db: AsyncSession, faculty_id: str) -> dict:
    result = await db.execute(select(ResearchGuidance).where(ResearchGuidance.faculty_id == faculty_id))
    guidance_entries = result.scalars().all()
    total_score = sum([entry.api_score_faculty or 0.0 for entry in guidance_entries])
    
    total_students_me = sum(1 for entry in guidance_entries if entry.degree.lower() == "me")
    total_students_phd = sum(1 for entry in guidance_entries if entry.degree.lower() == "phd")

    return {
        "total_score": total_score,
        "total_students_me": total_students_me,
        "total_students_phd": total_students_phd,
    }
