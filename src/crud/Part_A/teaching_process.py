from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from ...models.Part_A.teaching_process import TeachingProcess
from ...schema.Part_A.teaching_process import (
    TeachingProcessCreate,
    TeachingProcessUpdateFaculty,
    TeachingProcessUpdateHOD,
    TeachingProcessUpdateDirector,
    TeachingProcessUpdateDean,
    TeachingProcessUpdateVC,
)

async def get_teaching_process(db: AsyncSession, id: str) -> Optional[TeachingProcess]:
    result = await db.execute(select(TeachingProcess).where(TeachingProcess.id == id))
    return result.scalars().first()

async def get_teaching_process_by_faculty(db: AsyncSession, faculty_id: str) -> List[TeachingProcess]:
    result = await db.execute(select(TeachingProcess).where(TeachingProcess.faculty_id == faculty_id))
    return result.scalars().all()

async def create_teaching_process(db: AsyncSession, teaching: TeachingProcessCreate, faculty_id: str) -> TeachingProcess:
    db_teaching = TeachingProcess(**teaching.model_dump(), faculty_id=faculty_id)
    db.add(db_teaching)
    await db.commit()
    await db.refresh(db_teaching)
    return db_teaching

async def update_teaching_process_faculty(
    db: AsyncSession, id: str, teaching_update: TeachingProcessUpdateFaculty
) -> Optional[TeachingProcess]:
    db_teaching = await get_teaching_process(db, id)
    if db_teaching:
        update_data = teaching_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_teaching, key, value)
        await db.commit()
        await db.refresh(db_teaching)
    return db_teaching

async def update_teaching_process_hod(
    db: AsyncSession, id: str, teaching_update: TeachingProcessUpdateHOD
) -> Optional[TeachingProcess]:
    db_teaching = await get_teaching_process(db, id)
    if db_teaching:
        update_data = teaching_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_teaching, key, value)
        await db.commit()
        await db.refresh(db_teaching)
    return db_teaching

async def delete_teaching_process(db: AsyncSession, id: str) -> bool:
    db_teaching = await get_teaching_process(db, id)
    if db_teaching:
        await db.delete(db_teaching)
        await db.commit()
        return True
    return False

async def get_teaching_process_total_score(db: AsyncSession, faculty_id: str) -> float:
    entries = await get_teaching_process_by_faculty(db, faculty_id)
    return sum([e.api_score_faculty or 0.0 for e in entries])

async def update_teaching_process_director(
    db: AsyncSession, id: str, update: TeachingProcessUpdateDirector
) -> Optional[TeachingProcess]:
    db_obj = await get_teaching_process(db, id)
    if db_obj:
        db_obj.api_score_director = update.api_score_director
        await db.commit()
        await db.refresh(db_obj)
    return db_obj

async def update_teaching_process_dean(
    db: AsyncSession, id: str, update: TeachingProcessUpdateDean
) -> Optional[TeachingProcess]:
    db_obj = await get_teaching_process(db, id)
    if db_obj:
        db_obj.api_score_dean = update.api_score_dean
        await db.commit()
        await db.refresh(db_obj)
    return db_obj

async def update_teaching_process_vc(
    db: AsyncSession, id: str, update: TeachingProcessUpdateVC
) -> Optional[TeachingProcess]:
    db_obj = await get_teaching_process(db, id)
    if db_obj:
        db_obj.api_score_vc = update.api_score_vc
        await db.commit()
        await db.refresh(db_obj)
    return db_obj
