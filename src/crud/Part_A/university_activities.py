from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from ...models.Part_A.university_activities import UniversityActivity
from ...schema.Part_A.university_activities import (
    UniversityActivityCreate,
    UniversityActivityUpdateFaculty,
    UniversityActivityUpdateHOD,
    UniversityActivityUpdateDirector,
)

async def get_university_activity(db: AsyncSession, id: str) -> Optional[UniversityActivity]:
    result = await db.execute(select(UniversityActivity).where(UniversityActivity.id == id))
    return result.scalars().first()

async def get_university_activities_by_faculty(db: AsyncSession, faculty_id: str) -> List[UniversityActivity]:
    result = await db.execute(select(UniversityActivity).where(UniversityActivity.faculty_id == faculty_id))
    return result.scalars().all()

async def create_university_activity(
    db: AsyncSession, activity: UniversityActivityCreate, faculty_id: str
) -> UniversityActivity:
    db_activity = UniversityActivity(**activity.model_dump(), faculty_id=faculty_id)
    db.add(db_activity)
    await db.commit()
    await db.refresh(db_activity)
    return db_activity

async def update_university_activity_faculty(
    db: AsyncSession, id: str, activity_update: UniversityActivityUpdateFaculty
) -> Optional[UniversityActivity]:
    db_activity = await get_university_activity(db, id)
    if db_activity:
        update_data = activity_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_activity, key, value)
        await db.commit()
        await db.refresh(db_activity)
    return db_activity

async def update_university_activity_hod(
    db: AsyncSession, id: str, activity_update: UniversityActivityUpdateHOD
) -> Optional[UniversityActivity]:
    db_activity = await get_university_activity(db, id)
    if db_activity:
        db_activity.api_score_hod = activity_update.api_score_hod
        await db.commit()
        await db.refresh(db_activity)
    return db_activity

async def update_university_activity_director(
    db: AsyncSession, id: str, activity_update: UniversityActivityUpdateDirector
) -> Optional[UniversityActivity]:
    db_activity = await get_university_activity(db, id)
    if db_activity:
        db_activity.api_score_director = activity_update.api_score_director
        await db.commit()
        await db.refresh(db_activity)
    return db_activity

async def delete_university_activity(db: AsyncSession, id: str) -> bool:
    db_activity = await get_university_activity(db, id)
    if db_activity:
        await db.delete(db_activity)
        await db.commit()
        return True
    return False

async def get_university_activity_total_score(db: AsyncSession, faculty_id: str) -> float:
    entries = await get_university_activities_by_faculty(db, faculty_id)
    return sum([e.api_score_faculty or 0.0 for e in entries])
