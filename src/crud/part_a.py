from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from src.models.part_a import (
    TeachingProcess, CourseFile, InnovativeTeaching, ProjectGuided,
    QualificationEnhancement, StudentFeedback, DepartmentActivity,
    UniversityActivity, SocialContribution, IndustryConnect, ACRScore
)
from typing import List, Type, Any, Optional

async def get_items_by_faculty(db: AsyncSession, model: Type[Any], email: str, year: str) -> List[Any]:
    result = await db.execute(select(model).where(
        model.faculty_email == email,
        model.academic_year == year
    ).order_by(getattr(model, 'row_no', model.id)))
    return result.scalars().all()

async def create_item(db: AsyncSession, model: Type[Any], data: dict) -> Any:
    db_item = model(**data)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

async def update_item(db: AsyncSession, model: Type[Any], item_id: str, data: dict) -> Any:
    result = await db.execute(select(model).where(model.id == item_id))
    db_item = result.scalar_one_or_none()
    if db_item:
        for key, value in data.items():
            setattr(db_item, key, value)
        await db.commit()
        await db.refresh(db_item)
    return db_item

async def delete_item(db: AsyncSession, model: Type[Any], item_id: str) -> bool:
    result = await db.execute(delete(model).where(model.id == item_id))
    await db.commit()
    return result.rowcount > 0

# Special case for tables without row_no (like InnovativeTeaching which has a unique constraint in SQL)
async def get_innovative_teaching(db: AsyncSession, email: str, year: str) -> Optional[InnovativeTeaching]:
    result = await db.execute(select(InnovativeTeaching).where(
        InnovativeTeaching.faculty_email == email,
        InnovativeTeaching.academic_year == year
    ))
    return result.scalar_one_or_none()
