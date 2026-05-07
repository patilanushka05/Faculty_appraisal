from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from src.models.Part_B.research_project import ResearchProject
from src.schema.Part_B.research_project import (
    ResearchProjectCreate,
    ResearchProjectUpdateFaculty,
    ResearchProjectUpdateHOD,
    ResearchProjectUpdateDirector,
    ResearchProjectUpdateDean,
    ResearchProjectUpdateVC,)

async def get_research_project(db: AsyncSession, project_id: str) -> Optional[ResearchProject]:
    result = await db.execute(select(ResearchProject).where(ResearchProject.id == project_id))
    return result.scalars().first()

async def get_research_projects_by_faculty(db: AsyncSession, faculty_id: str, skip: int = 0, limit: int = 100) -> List[ResearchProject]:
    result = await db.execute(select(ResearchProject).where(ResearchProject.faculty_id == faculty_id).offset(skip).limit(limit))
    return result.scalars().all()

async def get_all_research_projects(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ResearchProject]:
    result = await db.execute(select(ResearchProject).offset(skip).limit(limit))
    return result.scalars().all()

async def create_research_project(db: AsyncSession, project: ResearchProjectCreate, faculty_id: str) -> ResearchProject:
    db_project = ResearchProject(**project.model_dump(), faculty_id=faculty_id)
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return db_project

async def update_research_project_faculty(
    db: AsyncSession, project_id: str, project_update: ResearchProjectUpdateFaculty
) -> Optional[ResearchProject]:
    db_project = await get_research_project(db, project_id)
    if db_project:
        update_data = project_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_project, key, value)
        await db.commit()
        await db.refresh(db_project)
    return db_project

async def update_research_project_hod(
    db: AsyncSession, project_id: str, project_update: ResearchProjectUpdateHOD
) -> Optional[ResearchProject]:
    db_project = await get_research_project(db, project_id)
    if db_project:
        db_project.api_score_hod = project_update.api_score_hod
        await db.commit()
        await db.refresh(db_project)
    return db_project

async def update_research_project_director(
    db: AsyncSession, project_id: str, project_update: ResearchProjectUpdateDirector
) -> Optional[ResearchProject]:
    db_project = await get_research_project(db, project_id)
    if db_project:
        db_project.api_score_director = project_update.api_score_director
        await db.commit()
        await db.refresh(db_project)
    return db_project

async def delete_research_project(db: AsyncSession, project_id: str) -> Optional[ResearchProject]:
    db_project = await get_research_project(db, project_id)
    if db_project:
        await db.delete(db_project)
        await db.commit()
    return db_project

async def get_research_projects_total_score(db: AsyncSession, faculty_id: str) -> float:
    result = await db.execute(select(ResearchProject).where(ResearchProject.faculty_id == faculty_id))
    projects = result.scalars().all()
    total_score = sum([p.api_score_faculty or 0.0 for p in projects])
    return total_score

async def update_research_project_dean(
    db: AsyncSession, id: str, update: ResearchProjectUpdateDean
) -> Optional[ResearchProject]:
    db_obj = await get_research_project(db, id)
    if db_obj:
        db_obj.api_score_dean = update.api_score_dean
        await db.commit()
        await db.refresh(db_obj)
    return db_obj

async def update_research_project_vc(
    db: AsyncSession, id: str, update: ResearchProjectUpdateVC
) -> Optional[ResearchProject]:
    db_obj = await get_research_project(db, id)
    if db_obj:
        db_obj.api_score_vc = update.api_score_vc
        await db.commit()
        await db.refresh(db_obj)
    return db_obj
