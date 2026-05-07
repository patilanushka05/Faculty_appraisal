from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from src.models.non_teaching import NonTeachingAppraisal, NonTeachingPartAItem, NonTeachingPartBRating
from typing import List, Optional, Any
from uuid import UUID

async def get_non_teaching_appraisal(db: AsyncSession, email: str, year: str) -> Optional[NonTeachingAppraisal]:
    result = await db.execute(select(NonTeachingAppraisal).where(
        NonTeachingAppraisal.staff_email == email,
        NonTeachingAppraisal.academic_year == year
    ))
    return result.scalar_one_or_none()

async def create_or_update_non_teaching_appraisal(db: AsyncSession, data: dict) -> NonTeachingAppraisal:
    db_appr = await get_non_teaching_appraisal(db, data['staff_email'], data['academic_year'])
    if db_appr:
        for key, value in data.items():
            setattr(db_appr, key, value)
    else:
        db_appr = NonTeachingAppraisal(**data)
        db.add(db_appr)
    await db.commit()
    await db.refresh(db_appr)
    return db_appr

async def get_part_a_items(db: AsyncSession, email: str, year: str) -> List[NonTeachingPartAItem]:
    result = await db.execute(select(NonTeachingPartAItem).where(
        NonTeachingPartAItem.staff_email == email,
        NonTeachingPartAItem.academic_year == year
    ))
    return result.scalars().all()

async def get_part_b_ratings(db: AsyncSession, email: str, year: str) -> List[NonTeachingPartBRating]:
    result = await db.execute(select(NonTeachingPartBRating).where(
        NonTeachingPartBRating.staff_email == email,
        NonTeachingPartBRating.academic_year == year
    ).order_by(NonTeachingPartBRating.section_key, NonTeachingPartBRating.parameter_no))
    return result.scalars().all()
