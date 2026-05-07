from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from ...models.Part_A.acr import ACR
from ...schema.Part_A.acr import (
    ACRCreate,
    ACRUpdateHOD,
    ACRUpdateDirector,
    ACRUpdateDean,
    ACRUpdateVC,
)

async def get_acr(db: AsyncSession, id: str) -> Optional[ACR]:
    result = await db.execute(select(ACR).where(ACR.id == id))
    return result.scalars().first()

async def get_acr_by_faculty(db: AsyncSession, faculty_id: str) -> List[ACR]:
    result = await db.execute(select(ACR).where(ACR.faculty_id == faculty_id))
    return result.scalars().all()

async def create_acr(db: AsyncSession, acr: ACRCreate) -> ACR:
    db_acr = ACR(**acr.model_dump())
    db.add(db_acr)
    await db.commit()
    await db.refresh(db_acr)
    return db_acr

async def update_acr_hod(
    db: AsyncSession, id: str, acr_update: ACRUpdateHOD
) -> Optional[ACR]:
    db_acr = await get_acr(db, id)
    if db_acr:
        db_acr.api_score_hod = acr_update.api_score_hod
        await db.commit()
        await db.refresh(db_acr)
    return db_acr

async def update_acr_director(
    db: AsyncSession, id: str, acr_update: ACRUpdateDirector
) -> Optional[ACR]:
    db_acr = await get_acr(db, id)
    if db_acr:
        update_data = acr_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_acr, key, value)
        await db.commit()
        await db.refresh(db_acr)
    return db_acr

async def update_acr_dean(
    db: AsyncSession, id: str, acr_update: ACRUpdateDean
) -> Optional[ACR]:
    db_acr = await get_acr(db, id)
    if db_acr:
        db_acr.api_score_dean = acr_update.api_score_dean
        await db.commit()
        await db.refresh(db_acr)
    return db_acr

async def update_acr_vc(
    db: AsyncSession, id: str, acr_update: ACRUpdateVC
) -> Optional[ACR]:
    db_acr = await get_acr(db, id)
    if db_acr:
        db_acr.api_score_vc = acr_update.api_score_vc
        await db.commit()
        await db.refresh(db_acr)
    return db_acr

async def delete_acr(db: AsyncSession, id: str) -> bool:
    db_acr = await get_acr(db, id)
    if db_acr:
        await db.delete(db_acr)
        await db.commit()
        return True
    return False

async def get_acr_total_score(db: AsyncSession, faculty_id: str) -> float:
    entries = await get_acr_by_faculty(db, faculty_id)
    # Note: ACR usually has score from HOD/Director. 
    # Summary requirement for ACR might need clarification, but I'll return a sum for now.
    return sum([e.api_score_hod or 0.0 for e in entries])
