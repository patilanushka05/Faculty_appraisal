from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from ...models.Part_A.course_file import CourseFile
from ...schema.Part_A.course_file import (
    CourseFileCreate,
    CourseFileUpdateFaculty,
    CourseFileUpdateHOD,
    CourseFileUpdateDirector,
    CourseFileUpdateDean,
    CourseFileUpdateVC,
)

async def get_course_file(db: AsyncSession, id: str) -> Optional[CourseFile]:
    result = await db.execute(select(CourseFile).where(CourseFile.id == id))
    return result.scalars().first()

async def get_course_files_by_faculty(db: AsyncSession, faculty_id: str) -> List[CourseFile]:
    result = await db.execute(select(CourseFile).where(CourseFile.faculty_id == faculty_id))
    return result.scalars().all()

async def create_course_file(db: AsyncSession, course_file: CourseFileCreate, faculty_id: str) -> CourseFile:
    db_course_file = CourseFile(**course_file.model_dump(), faculty_id=faculty_id)
    db.add(db_course_file)
    await db.commit()
    await db.refresh(db_course_file)
    return db_course_file

async def update_course_file_faculty(
    db: AsyncSession, id: str, course_file_update: CourseFileUpdateFaculty
) -> Optional[CourseFile]:
    db_course_file = await get_course_file(db, id)
    if db_course_file:
        update_data = course_file_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_course_file, key, value)
        await db.commit()
        await db.refresh(db_course_file)
    return db_course_file

async def update_course_file_hod(
    db: AsyncSession, id: str, course_file_update: CourseFileUpdateHOD
) -> Optional[CourseFile]:
    db_course_file = await get_course_file(db, id)
    if db_course_file:
        update_data = course_file_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_course_file, key, value)
        await db.commit()
        await db.refresh(db_course_file)
    return db_course_file

async def update_course_file_director(
    db: AsyncSession, id: str, course_file_update: CourseFileUpdateDirector
) -> Optional[CourseFile]:
    db_course_file = await get_course_file(db, id)
    if db_course_file:
        db_course_file.api_score_director = course_file_update.api_score_director
        await db.commit()
        await db.refresh(db_course_file)
    return db_course_file

async def update_course_file_dean(
    db: AsyncSession, id: str, course_file_update: CourseFileUpdateDean
) -> Optional[CourseFile]:
    db_course_file = await get_course_file(db, id)
    if db_course_file:
        db_course_file.api_score_dean = course_file_update.api_score_dean
        await db.commit()
        await db.refresh(db_course_file)
    return db_course_file

async def update_course_file_vc(
    db: AsyncSession, id: str, course_file_update: CourseFileUpdateVC
) -> Optional[CourseFile]:
    db_course_file = await get_course_file(db, id)
    if db_course_file:
        db_course_file.api_score_vc = course_file_update.api_score_vc
        await db.commit()
        await db.refresh(db_course_file)
    return db_course_file

async def delete_course_file(db: AsyncSession, id: str) -> bool:
    db_course_file = await get_course_file(db, id)
    if db_course_file:
        await db.delete(db_course_file)
        await db.commit()
        return True
    return False

async def get_course_file_total_score(db: AsyncSession, faculty_id: str) -> float:
    entries = await get_course_files_by_faculty(db, faculty_id)
    return sum([e.api_score_faculty or 0.0 for e in entries])
