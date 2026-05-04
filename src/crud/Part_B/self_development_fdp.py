from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from src.models.Part_B.self_development_fdp import SelfDevelopmentFDP
from src.schema.Part_B.self_development_fdp import (
    SelfDevelopmentFDPCreate,
    SelfDevelopmentFDPUpdateFaculty,
    SelfDevelopmentFDPUpdateHOD,
    SelfDevelopmentFDPUpdateDirector,
)

async def get_self_development_fdp(db: AsyncSession, fdp_id: str) -> Optional[SelfDevelopmentFDP]:
    result = await db.execute(select(SelfDevelopmentFDP).where(SelfDevelopmentFDP.id == fdp_id))
    return result.scalars().first()

async def get_self_development_fdp_by_faculty(db: AsyncSession, faculty_id: str, skip: int = 0, limit: int = 100) -> List[SelfDevelopmentFDP]:
    result = await db.execute(select(SelfDevelopmentFDP).where(SelfDevelopmentFDP.faculty_id == faculty_id).offset(skip).limit(limit))
    return result.scalars().all()

async def get_all_self_development_fdp(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[SelfDevelopmentFDP]:
    result = await db.execute(select(SelfDevelopmentFDP).offset(skip).limit(limit))
    return result.scalars().all()

async def create_self_development_fdp(db: AsyncSession, fdp: SelfDevelopmentFDPCreate, faculty_id: str) -> SelfDevelopmentFDP:
    db_fdp = SelfDevelopmentFDP(**fdp.model_dump(), faculty_id=faculty_id)
    db.add(db_fdp)
    await db.commit()
    await db.refresh(db_fdp)
    return db_fdp

async def update_self_development_fdp_faculty(
    db: AsyncSession, fdp_id: str, fdp_update: SelfDevelopmentFDPUpdateFaculty
) -> Optional[SelfDevelopmentFDP]:
    db_fdp = await get_self_development_fdp(db, fdp_id)
    if db_fdp:
        update_data = fdp_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_fdp, key, value)
        await db.commit()
        await db.refresh(db_fdp)
    return db_fdp

async def update_self_development_fdp_hod(
    db: AsyncSession, fdp_id: str, fdp_update: SelfDevelopmentFDPUpdateHOD
) -> Optional[SelfDevelopmentFDP]:
    db_fdp = await get_self_development_fdp(db, fdp_id)
    if db_fdp:
        db_fdp.api_score_hod = fdp_update.api_score_hod
        await db.commit()
        await db.refresh(db_fdp)
    return db_fdp

async def update_self_development_fdp_director(
    db: AsyncSession, fdp_id: str, fdp_update: SelfDevelopmentFDPUpdateDirector
) -> Optional[SelfDevelopmentFDP]:
    db_fdp = await get_self_development_fdp(db, fdp_id)
    if db_fdp:
        db_fdp.api_score_director = fdp_update.api_score_director
        await db.commit()
        await db.refresh(db_fdp)
    return db_fdp

async def delete_self_development_fdp(db: AsyncSession, fdp_id: str) -> Optional[SelfDevelopmentFDP]:
    db_fdp = await get_self_development_fdp(db, fdp_id)
    if db_fdp:
        await db.delete(db_fdp)
        await db.commit()
    return db_fdp

async def get_self_development_fdp_total_score(db: AsyncSession, faculty_id: str) -> float:
    fdp_entries = await get_self_development_fdp_by_faculty(db, faculty_id, limit=1000)
    total_score = sum([fdp.api_score_faculty or 0.0 for fdp in fdp_entries])
    return total_score
