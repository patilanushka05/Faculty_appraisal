from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from ...models.Part_A.project import ProjectPartA
from ...schema.Part_A.project import (
    ProjectPartACreate,
    ProjectPartAUpdateFaculty,
    ProjectPartAUpdateHOD,
    ProjectPartAUpdateDirector,
    ProjectPartAUpdateDean,
    ProjectPartAUpdateVC,
)

async def get_project(db: AsyncSession, id: str) -> Optional[ProjectPartA]:
    result = await db.execute(select(ProjectPartA).where(ProjectPartA.id == id))
    return result.scalars().first()

async def get_projects_by_faculty(db: AsyncSession, faculty_id: str) -> List[ProjectPartA]:
    result = await db.execute(select(ProjectPartA).where(ProjectPartA.faculty_id == faculty_id))
    return result.scalars().all()

async def create_project(db: AsyncSession, project: ProjectPartACreate, faculty_id: str) -> ProjectPartA:
    db_project = ProjectPartA(**project.model_dump(), faculty_id=faculty_id)
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return db_project

async def update_project_faculty(
    db: AsyncSession, id: str, project_update: ProjectPartAUpdateFaculty
) -> Optional[ProjectPartA]:
    db_project = await get_project(db, id)
    if db_project:
        update_data = project_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_project, key, value)
        await db.commit()
        await db.refresh(db_project)
    return db_project

async def update_project_hod(
    db: AsyncSession, id: str, project_update: ProjectPartAUpdateHOD
) -> Optional[ProjectPartA]:
    db_project = await get_project(db, id)
    if db_project:
        db_project.api_score_hod = project_update.api_score_hod
        await db.commit()
        await db.refresh(db_project)
    return db_project

async def update_project_director(
    db: AsyncSession, id: str, project_update: ProjectPartAUpdateDirector
) -> Optional[ProjectPartA]:
    db_project = await get_project(db, id)
    if db_project:
        db_project.api_score_director = project_update.api_score_director
        await db.commit()
        await db.refresh(db_project)
    return db_project

async def delete_project(db: AsyncSession, id: str) -> bool:
    db_project = await get_project(db, id)
    if db_project:
        await db.delete(db_project)
        await db.commit()
        return True
    return False

async def get_project_total_score(db: AsyncSession, faculty_id: str) -> float:
    entries = await get_projects_by_faculty(db, faculty_id)
    return sum([e.api_score_faculty or 0.0 for e in entries])

async def update_project_dean(
    db: AsyncSession, id: str, update: ProjectPartAUpdateDean
) -> Optional[ProjectPartA]:
    db_obj = await get_project(db, id)
    if db_obj:
        db_obj.api_score_dean = update.api_score_dean
        await db.commit()
        await db.refresh(db_obj)
    return db_obj

async def update_project_vc(
    db: AsyncSession, id: str, update: ProjectPartAUpdateVC
) -> Optional[ProjectPartA]:
    db_obj = await get_project(db, id)
    if db_obj:
        db_obj.api_score_vc = update.api_score_vc
        await db.commit()
        await db.refresh(db_obj)
    return db_obj
