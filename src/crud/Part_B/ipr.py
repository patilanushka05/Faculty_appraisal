from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from src.models.Part_B.ipr import IPR
from src.schema.Part_B.ipr import (
    IPRCreate,
    IPRUpdateFaculty,
    IPRUpdateHOD,
    IPRUpdateDirector,
    IPRUpdateDean,
    IPRUpdateVC,)

async def get_ipr(db: AsyncSession, ipr_id: str) -> Optional[IPR]:
    result = await db.execute(select(IPR).where(IPR.id == ipr_id))
    return result.scalars().first()

async def get_ipr_by_faculty(db: AsyncSession, faculty_id: str, skip: int = 0, limit: int = 100) -> List[IPR]:
    result = await db.execute(select(IPR).where(IPR.faculty_id == faculty_id).offset(skip).limit(limit))
    return result.scalars().all()

async def get_all_ipr(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[IPR]:
    result = await db.execute(select(IPR).offset(skip).limit(limit))
    return result.scalars().all()

async def create_ipr(db: AsyncSession, ipr: IPRCreate, faculty_id: str) -> IPR:
    db_ipr = IPR(**ipr.model_dump(), faculty_id=faculty_id)
    db.add(db_ipr)
    await db.commit()
    await db.refresh(db_ipr)
    return db_ipr

async def update_ipr_faculty(
    db: AsyncSession, ipr_id: str, ipr_update: IPRUpdateFaculty
) -> Optional[IPR]:
    db_ipr = await get_ipr(db, ipr_id)
    if db_ipr:
        update_data = ipr_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_ipr, key, value)
        await db.commit()
        await db.refresh(db_ipr)
    return db_ipr

async def update_ipr_hod(
    db: AsyncSession, ipr_id: str, ipr_update: IPRUpdateHOD
) -> Optional[IPR]:
    db_ipr = await get_ipr(db, ipr_id)
    if db_ipr:
        db_ipr.api_score_hod = ipr_update.api_score_hod
        await db.commit()
        await db.refresh(db_ipr)
    return db_ipr

async def update_ipr_director(
    db: AsyncSession, ipr_id: str, ipr_update: IPRUpdateDirector
) -> Optional[IPR]:
    db_ipr = await get_ipr(db, ipr_id)
    if db_ipr:
        db_ipr.api_score_director = ipr_update.api_score_director
        await db.commit()
        await db.refresh(db_ipr)
    return db_ipr

async def delete_ipr(db: AsyncSession, ipr_id: str) -> Optional[IPR]:
    db_ipr = await get_ipr(db, ipr_id)
    if db_ipr:
        await db.delete(db_ipr)
        await db.commit()
    return db_ipr

async def get_ipr_total_score(db: AsyncSession, faculty_id: str) -> float:
    result = await db.execute(select(IPR).where(IPR.faculty_id == faculty_id))
    iprs = result.scalars().all()
    total_score = sum([entry.research_score_faculty or 0.0 for entry in iprs])
    return total_score

async def update_ipr_dean(
    db: AsyncSession, id: str, update: IPRUpdateDean
) -> Optional[IPR]:
    db_obj = await get_ipr(db, id)
    if db_obj:
        db_obj.api_score_dean = update.api_score_dean
        await db.commit()
        await db.refresh(db_obj)
    return db_obj

async def update_ipr_vc(
    db: AsyncSession, id: str, update: IPRUpdateVC
) -> Optional[IPR]:
    db_obj = await get_ipr(db, id)
    if db_obj:
        db_obj.api_score_vc = update.api_score_vc
        await db.commit()
        await db.refresh(db_obj)
    return db_obj
