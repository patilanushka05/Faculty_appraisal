from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from ...models.Part_A.teaching_methods import TeachingMethods
from ...schema.Part_A.teaching_methods import (
    TeachingMethodsCreate,
    TeachingMethodsUpdateFaculty,
    TeachingMethodsUpdateHOD,
    TeachingMethodsUpdateDirector,
    TeachingMethodsUpdateDean,
    TeachingMethodsUpdateVC,
)

async def get_teaching_methods(db: AsyncSession, id: str) -> Optional[TeachingMethods]:
    result = await db.execute(select(TeachingMethods).where(TeachingMethods.id == id))
    return result.scalars().first()

async def get_teaching_methods_by_faculty(db: AsyncSession, faculty_id: str) -> List[TeachingMethods]:
    result = await db.execute(select(TeachingMethods).where(TeachingMethods.faculty_id == faculty_id))
    return result.scalars().all()

async def create_teaching_methods(db: AsyncSession, teaching_methods: TeachingMethodsCreate, faculty_id: str) -> TeachingMethods:
    db_teaching_methods = TeachingMethods(**teaching_methods.model_dump(), faculty_id=faculty_id)
    db.add(db_teaching_methods)
    await db.commit()
    await db.refresh(db_teaching_methods)
    return db_teaching_methods

async def update_teaching_methods_faculty(
    db: AsyncSession, id: str, teaching_methods_update: TeachingMethodsUpdateFaculty
) -> Optional[TeachingMethods]:
    db_teaching_methods = await get_teaching_methods(db, id)
    if db_teaching_methods:
        update_data = teaching_methods_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_teaching_methods, key, value)
        await db.commit()
        await db.refresh(db_teaching_methods)
    return db_teaching_methods

async def update_teaching_methods_hod(
    db: AsyncSession, id: str, teaching_methods_update: TeachingMethodsUpdateHOD
) -> Optional[TeachingMethods]:
    db_teaching_methods = await get_teaching_methods(db, id)
    if db_teaching_methods:
        update_data = teaching_methods_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_teaching_methods, key, value)
        await db.commit()
        await db.refresh(db_teaching_methods)
    return db_teaching_methods

async def update_teaching_methods_director(
    db: AsyncSession, id: str, update: TeachingMethodsUpdateDirector
) -> Optional[TeachingMethods]:
    db_obj = await get_teaching_methods(db, id)
    if db_obj:
        db_obj.api_score_director = update.api_score_director
        await db.commit()
        await db.refresh(db_obj)
    return db_obj

async def update_teaching_methods_dean(
    db: AsyncSession, id: str, update: TeachingMethodsUpdateDean
) -> Optional[TeachingMethods]:
    db_obj = await get_teaching_methods(db, id)
    if db_obj:
        db_obj.api_score_dean = update.api_score_dean
        await db.commit()
        await db.refresh(db_obj)
    return db_obj

async def update_teaching_methods_vc(
    db: AsyncSession, id: str, update: TeachingMethodsUpdateVC
) -> Optional[TeachingMethods]:
    db_obj = await get_teaching_methods(db, id)
    if db_obj:
        db_obj.api_score_vc = update.api_score_vc
        await db.commit()
        await db.refresh(db_obj)
    return db_obj

async def delete_teaching_methods(db: AsyncSession, id: str) -> bool:
    db_teaching_methods = await get_teaching_methods(db, id)
    if db_teaching_methods:
        await db.delete(db_teaching_methods)
        await db.commit()
        return True
    return False

async def get_teaching_methods_total_score(db: AsyncSession, faculty_id: str) -> float:
    entries = await get_teaching_methods_by_faculty(db, faculty_id)
    return sum([e.api_score_faculty or 0.0 for e in entries])
