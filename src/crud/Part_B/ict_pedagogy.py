from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from src.models.Part_B.ict_pedagogy import ICTPedagogy
from src.schema.Part_B.ict_pedagogy import (
    ICTPedagogyCreate,
    ICTPedagogyUpdateFaculty,
    ICTPedagogyUpdateHOD,
    ICTPedagogyUpdateDirector,
    ICTPedagogyUpdateDean,
    ICTPedagogyUpdateVC,)

async def get_ict_pedagogy(db: AsyncSession, pedagogy_id: str) -> Optional[ICTPedagogy]:
    result = await db.execute(select(ICTPedagogy).where(ICTPedagogy.id == pedagogy_id))
    return result.scalars().first()

async def get_ict_pedagogies_by_faculty(db: AsyncSession, faculty_id: str, skip: int = 0, limit: int = 100) -> List[ICTPedagogy]:
    result = await db.execute(select(ICTPedagogy).where(ICTPedagogy.faculty_id == faculty_id).offset(skip).limit(limit))
    return result.scalars().all()

async def get_all_ict_pedagogies(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ICTPedagogy]:
    result = await db.execute(select(ICTPedagogy).offset(skip).limit(limit))
    return result.scalars().all()

async def create_ict_pedagogy(db: AsyncSession, pedagogy: ICTPedagogyCreate, faculty_id: str) -> ICTPedagogy:
    db_pedagogy = ICTPedagogy(**pedagogy.model_dump(), faculty_id=faculty_id)
    db.add(db_pedagogy)
    await db.commit()
    await db.refresh(db_pedagogy)
    return db_pedagogy

async def update_ict_pedagogy_faculty(
    db: AsyncSession, pedagogy_id: str, pedagogy_update: ICTPedagogyUpdateFaculty
) -> Optional[ICTPedagogy]:
    db_pedagogy = await get_ict_pedagogy(db, pedagogy_id)
    if db_pedagogy:
        update_data = pedagogy_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_pedagogy, key, value)
        await db.commit()
        await db.refresh(db_pedagogy)
    return db_pedagogy

async def update_ict_pedagogy_hod(
    db: AsyncSession, pedagogy_id: str, pedagogy_update: ICTPedagogyUpdateHOD
) -> Optional[ICTPedagogy]:
    db_pedagogy = await get_ict_pedagogy(db, pedagogy_id)
    if db_pedagogy:
        db_pedagogy.api_score_hod = pedagogy_update.api_score_hod
        await db.commit()
        await db.refresh(db_pedagogy)
    return db_pedagogy

async def update_ict_pedagogy_director(
    db: AsyncSession, pedagogy_id: str, pedagogy_update: ICTPedagogyUpdateDirector
) -> Optional[ICTPedagogy]:
    db_pedagogy = await get_ict_pedagogy(db, pedagogy_id)
    if db_pedagogy:
        db_pedagogy.api_score_director = pedagogy_update.api_score_director
        await db.commit()
        await db.refresh(db_pedagogy)
    return db_pedagogy

async def delete_ict_pedagogy(db: AsyncSession, pedagogy_id: str) -> Optional[ICTPedagogy]:
    db_pedagogy = await get_ict_pedagogy(db, pedagogy_id)
    if db_pedagogy:
        await db.delete(db_pedagogy)
        await db.commit()
    return db_pedagogy

async def get_ict_pedagogies_total_score(db: AsyncSession, faculty_id: str) -> float:
    result = await db.execute(select(ICTPedagogy).where(ICTPedagogy.faculty_id == faculty_id))
    pedagogies = result.scalars().all()
    total_score = sum([p.api_score_faculty or 0.0 for p in pedagogies])
    return total_score

async def update_ict_pedagogy_dean(
    db: AsyncSession, id: str, update: ICTPedagogyUpdateDean
) -> Optional[ICTPedagogy]:
    db_obj = await get_ict_pedagogy(db, id)
    if db_obj:
        db_obj.api_score_dean = update.api_score_dean
        await db.commit()
        await db.refresh(db_obj)
    return db_obj

async def update_ict_pedagogy_vc(
    db: AsyncSession, id: str, update: ICTPedagogyUpdateVC
) -> Optional[ICTPedagogy]:
    db_obj = await get_ict_pedagogy(db, id)
    if db_obj:
        db_obj.api_score_vc = update.api_score_vc
        await db.commit()
        await db.refresh(db_obj)
    return db_obj
