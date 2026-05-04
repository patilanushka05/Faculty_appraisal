from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from src.models.Part_B.journal_publication import JournalPublication
from src.schema.Part_B.journal_publication import (
    JournalPublicationCreate,
    JournalPublicationUpdateFaculty,
    JournalPublicationUpdateHOD,
    JournalPublicationUpdateDirector,
)

async def get_journal_publication(db: AsyncSession, publication_id: str) -> Optional[JournalPublication]:
    result = await db.execute(select(JournalPublication).where(JournalPublication.id == publication_id))
    return result.scalars().first()

async def get_journal_publications_by_faculty(db: AsyncSession, faculty_id: str, skip: int = 0, limit: int = 100) -> List[JournalPublication]:
    result = await db.execute(select(JournalPublication).where(JournalPublication.faculty_id == faculty_id).offset(skip).limit(limit))
    return result.scalars().all()

async def get_all_journal_publications(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[JournalPublication]:
    result = await db.execute(select(JournalPublication).offset(skip).limit(limit))
    return result.scalars().all()

async def create_journal_publication(db: AsyncSession, publication: JournalPublicationCreate, faculty_id: str) -> JournalPublication:
    db_publication = JournalPublication(**publication.model_dump(), faculty_id=faculty_id)
    db.add(db_publication)
    await db.commit()
    await db.refresh(db_publication)
    return db_publication

async def update_journal_publication_faculty(
    db: AsyncSession, publication_id: str, publication_update: JournalPublicationUpdateFaculty
) -> Optional[JournalPublication]:
    db_publication = await get_journal_publication(db, publication_id)
    if db_publication:
        update_data = publication_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_publication, key, value)
        await db.commit()
        await db.refresh(db_publication)
    return db_publication

async def update_journal_publication_hod(
    db: AsyncSession, publication_id: str, publication_update: JournalPublicationUpdateHOD
) -> Optional[JournalPublication]:
    db_publication = await get_journal_publication(db, publication_id)
    if db_publication:
        db_publication.api_score_hod = publication_update.api_score_hod
        await db.commit()
        await db.refresh(db_publication)
    return db_publication

async def update_journal_publication_director(
    db: AsyncSession, publication_id: str, publication_update: JournalPublicationUpdateDirector
) -> Optional[JournalPublication]:
    db_publication = await get_journal_publication(db, publication_id)
    if db_publication:
        db_publication.api_score_director = publication_update.api_score_director
        await db.commit()
        await db.refresh(db_publication)
    return db_publication

async def delete_journal_publication(db: AsyncSession, publication_id: str) -> Optional[JournalPublication]:
    db_publication = await get_journal_publication(db, publication_id)
    if db_publication:
        await db.delete(db_publication)
        await db.commit()
    return db_publication

async def get_journal_publications_total_score(db: AsyncSession, faculty_id: str) -> float:
    publications = await get_journal_publications_by_faculty(db, faculty_id, limit=1000)
    total_score = sum([pub.api_score_faculty or 0.0 for pub in publications]) 
    return total_score
