from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from ...models.Part_A.industry_connect import IndustryConnect
from ...schema.Part_A.industry_connect import (
    IndustryConnectCreate,
    IndustryConnectUpdateFaculty,
    IndustryConnectUpdateHOD,
    IndustryConnectUpdateDirector,
)

async def get_industry_connect(db: AsyncSession, id: str) -> Optional[IndustryConnect]:
    result = await db.execute(select(IndustryConnect).where(IndustryConnect.id == id))
    return result.scalars().first()

async def get_industry_connect_by_faculty(db: AsyncSession, faculty_id: str) -> List[IndustryConnect]:
    result = await db.execute(select(IndustryConnect).where(IndustryConnect.faculty_id == faculty_id))
    return result.scalars().all()

async def create_industry_connect(
    db: AsyncSession, connect: IndustryConnectCreate, faculty_id: str
) -> IndustryConnect:
    db_connect = IndustryConnect(**connect.model_dump(), faculty_id=faculty_id)
    db.add(db_connect)
    await db.commit()
    await db.refresh(db_connect)
    return db_connect

async def update_industry_connect_faculty(
    db: AsyncSession, id: str, connect_update: IndustryConnectUpdateFaculty
) -> Optional[IndustryConnect]:
    db_connect = await get_industry_connect(db, id)
    if db_connect:
        update_data = connect_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_connect, key, value)
        await db.commit()
        await db.refresh(db_connect)
    return db_connect

async def update_industry_connect_hod(
    db: AsyncSession, id: str, connect_update: IndustryConnectUpdateHOD
) -> Optional[IndustryConnect]:
    db_connect = await get_industry_connect(db, id)
    if db_connect:
        db_connect.api_score_hod = connect_update.api_score_hod
        await db.commit()
        await db.refresh(db_connect)
    return db_connect

async def update_industry_connect_director(
    db: AsyncSession, id: str, connect_update: IndustryConnectUpdateDirector
) -> Optional[IndustryConnect]:
    db_connect = await get_industry_connect(db, id)
    if db_connect:
        db_connect.api_score_director = connect_update.api_score_director
        await db.commit()
        await db.refresh(db_connect)
    return db_connect

async def delete_industry_connect(db: AsyncSession, id: str) -> bool:
    db_connect = await get_industry_connect(db, id)
    if db_connect:
        await db.delete(db_connect)
        await db.commit()
        return True
    return False

async def get_industry_connect_total_score(db: AsyncSession, faculty_id: str) -> float:
    entries = await get_industry_connect_by_faculty(db, faculty_id)
    return sum([e.api_score_faculty or 0.0 for e in entries])
