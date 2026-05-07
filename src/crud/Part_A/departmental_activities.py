from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from ...models.Part_A.departmental_activities import DepartmentalActivity
from ...schema.Part_A.departmental_activities import (
    DepartmentalActivityCreate,
    DepartmentalActivityUpdateFaculty,
    DepartmentalActivityUpdateHOD,
    DepartmentalActivityUpdateDirector,
    DepartmentalActivityUpdateDean,
    DepartmentalActivityUpdateVC,
)

async def get_departmental_activity(db: AsyncSession, id: str) -> Optional[DepartmentalActivity]:
    result = await db.execute(select(DepartmentalActivity).where(DepartmentalActivity.id == id))
    return result.scalars().first()

async def get_departmental_activities_by_faculty(db: AsyncSession, faculty_id: str) -> List[DepartmentalActivity]:
    result = await db.execute(select(DepartmentalActivity).where(DepartmentalActivity.faculty_id == faculty_id))
    return result.scalars().all()

async def create_departmental_activity(
    db: AsyncSession, activity: DepartmentalActivityCreate, faculty_id: str
) -> DepartmentalActivity:
    db_activity = DepartmentalActivity(**activity.model_dump(), faculty_id=faculty_id)
    db.add(db_activity)
    await db.commit()
    await db.refresh(db_activity)
    return db_activity

async def update_departmental_activity_faculty(
    db: AsyncSession, id: str, activity_update: DepartmentalActivityUpdateFaculty
) -> Optional[DepartmentalActivity]:
    db_activity = await get_departmental_activity(db, id)
    if db_activity:
        update_data = activity_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_activity, key, value)
        await db.commit()
        await db.refresh(db_activity)
    return db_activity

async def update_departmental_activity_hod(
    db: AsyncSession, id: str, activity_update: DepartmentalActivityUpdateHOD
) -> Optional[DepartmentalActivity]:
    db_activity = await get_departmental_activity(db, id)
    if db_activity:
        db_activity.api_score_hod = activity_update.api_score_hod
        await db.commit()
        await db.refresh(db_activity)
    return db_activity

async def update_departmental_activity_director(
    db: AsyncSession, id: str, activity_update: DepartmentalActivityUpdateDirector
) -> Optional[DepartmentalActivity]:
    db_activity = await get_departmental_activity(db, id)
    if db_activity:
        db_activity.api_score_director = activity_update.api_score_director
        await db.commit()
        await db.refresh(db_activity)
    return db_activity

async def update_departmental_activity_dean(
    db: AsyncSession, id: str, activity_update: DepartmentalActivityUpdateDean
) -> Optional[DepartmentalActivity]:
    db_activity = await get_departmental_activity(db, id)
    if db_activity:
        db_activity.api_score_dean = activity_update.api_score_dean
        await db.commit()
        await db.refresh(db_activity)
    return db_activity

async def update_departmental_activity_vc(
    db: AsyncSession, id: str, activity_update: DepartmentalActivityUpdateVC
) -> Optional[DepartmentalActivity]:
    db_activity = await get_departmental_activity(db, id)
    if db_activity:
        db_activity.api_score_vc = activity_update.api_score_vc
        await db.commit()
        await db.refresh(db_activity)
    return db_activity

async def delete_departmental_activity(db: AsyncSession, id: str) -> bool:
    db_activity = await get_departmental_activity(db, id)
    if db_activity:
        await db.delete(db_activity)
        await db.commit()
        return True
    return False

async def get_departmental_activity_total_score(db: AsyncSession, faculty_id: str) -> float:
    entries = await get_departmental_activities_by_faculty(db, faculty_id)
    return sum([e.api_score_faculty or 0.0 for e in entries])
