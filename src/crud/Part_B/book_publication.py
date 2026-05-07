from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from src.models.Part_B.book_publication import BookPublication
from src.schema.Part_B.book_publication import (
    BookPublicationCreate,
    BookPublicationUpdateFaculty,
    BookPublicationUpdateHOD,
    BookPublicationUpdateDirector,
    BookPublicationUpdateDean,
    BookPublicationUpdateVC,)

async def get_book_publication(db: AsyncSession, publication_id: str) -> Optional[BookPublication]:
    result = await db.execute(select(BookPublication).where(BookPublication.id == publication_id))
    return result.scalars().first()

async def get_book_publications_by_faculty(db: AsyncSession, faculty_id: str, skip: int = 0, limit: int = 100) -> List[BookPublication]:
    result = await db.execute(select(BookPublication).where(BookPublication.faculty_id == faculty_id).offset(skip).limit(limit))
    return result.scalars().all()

async def get_all_book_publications(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[BookPublication]:
    result = await db.execute(select(BookPublication).offset(skip).limit(limit))
    return result.scalars().all()

async def create_book_publication(db: AsyncSession, publication: BookPublicationCreate, faculty_id: str) -> BookPublication:
    db_publication = BookPublication(**publication.model_dump(), faculty_id=faculty_id)
    db.add(db_publication)
    await db.commit()
    await db.refresh(db_publication)
    return db_publication

async def update_book_publication_faculty(
    db: AsyncSession, publication_id: str, publication_update: BookPublicationUpdateFaculty
) -> Optional[BookPublication]:
    db_publication = await get_book_publication(db, publication_id)
    if db_publication:
        update_data = publication_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_publication, key, value)
        await db.commit()
        await db.refresh(db_publication)
    return db_publication

async def update_book_publication_hod(
    db: AsyncSession, publication_id: str, publication_update: BookPublicationUpdateHOD
) -> Optional[BookPublication]:
    db_publication = await get_book_publication(db, publication_id)
    if db_publication:
        db_publication.api_score_hod = publication_update.api_score_hod
        await db.commit()
        await db.refresh(db_publication)
    return db_publication

async def update_book_publication_director(
    db: AsyncSession, publication_id: str, publication_update: BookPublicationUpdateDirector
) -> Optional[BookPublication]:
    db_publication = await get_book_publication(db, publication_id)
    if db_publication:
        db_publication.api_score_director = publication_update.api_score_director
        await db.commit()
        await db.refresh(db_publication)
    return db_publication

async def delete_book_publication(db: AsyncSession, publication_id: str) -> Optional[BookPublication]:
    db_publication = await get_book_publication(db, publication_id)
    if db_publication:
        await db.delete(db_publication)
        await db.commit()
    return db_publication

async def get_book_publications_total_score(db: AsyncSession, faculty_id: str) -> float:
    publications = await get_book_publications_by_faculty(db, faculty_id, limit=1000)
    total_score = sum([pub.api_score_faculty or 0.0 for pub in publications]) 
    return total_score

async def update_book_publication_dean(
    db: AsyncSession, id: str, update: BookPublicationUpdateDean
) -> Optional[BookPublication]:
    db_obj = await get_book_publication(db, id)
    if db_obj:
        db_obj.api_score_dean = update.api_score_dean
        await db.commit()
        await db.refresh(db_obj)
    return db_obj

async def update_book_publication_vc(
    db: AsyncSession, id: str, update: BookPublicationUpdateVC
) -> Optional[BookPublication]:
    db_obj = await get_book_publication(db, id)
    if db_obj:
        db_obj.api_score_vc = update.api_score_vc
        await db.commit()
        await db.refresh(db_obj)
    return db_obj
