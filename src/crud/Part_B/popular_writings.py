from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional
from uuid import UUID

from src.models.Part_B.popular_writings import PopularWriting
from src.schema.Part_B.popular_writings import PopularWritingCreate, PopularWritingUpdate

async def get_popular_writing(db: AsyncSession, writing_id: UUID) -> Optional[PopularWriting]:
    result = await db.execute(select(PopularWriting).where(PopularWriting.id == writing_id))
    return result.scalars().first()

async def get_popular_writings_by_faculty(db: AsyncSession, faculty_id: UUID, skip: int = 0, limit: int = 100) -> List[PopularWriting]:
    result = await db.execute(select(PopularWriting).where(PopularWriting.faculty_id == faculty_id).offset(skip).limit(limit))
    return result.scalars().all()

async def get_all_popular_writings(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[PopularWriting]:
    result = await db.execute(select(PopularWriting).offset(skip).limit(limit))
    return result.scalars().all()

async def create_popular_writing(db: AsyncSession, writing: PopularWritingCreate, faculty_id: UUID) -> PopularWriting:
    db_writing = PopularWriting(**writing.model_dump(), faculty_id=faculty_id)
    db.add(db_writing)
    await db.commit()
    await db.refresh(db_writing)
    return db_writing

async def update_popular_writing(db: AsyncSession, writing_id: UUID, writing_update: PopularWritingUpdate) -> Optional[PopularWriting]:
    db_writing = await get_popular_writing(db, writing_id)
    if db_writing:
        update_data = writing_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_writing, key, value)
        await db.commit()
        await db.refresh(db_writing)
    return db_writing

async def delete_popular_writing(db: AsyncSession, writing_id: UUID) -> Optional[PopularWriting]:
    db_writing = await get_popular_writing(db, writing_id)
    if db_writing:
        await db.delete(db_writing)
        await db.commit()
    return db_writing

async def get_popular_writings_total_score(db: AsyncSession, faculty_id: UUID) -> float:
    result = await db.execute(select(PopularWriting).where(PopularWriting.faculty_id == faculty_id))
    writings = result.scalars().all()
    return sum([w.api_score_faculty or 0.0 for w in writings])
