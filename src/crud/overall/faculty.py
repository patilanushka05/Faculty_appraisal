from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from ...models.Part_B.faculty import Faculty
from ...schema.overall.faculty import FacultyUpdate

async def get_faculty(db: AsyncSession, faculty_id: str) -> Optional[Faculty]:
    result = await db.execute(select(Faculty).filter(Faculty.id == faculty_id))
    return result.scalars().first()

async def update_faculty(db: AsyncSession, faculty_id: str, faculty_data: FacultyUpdate) -> Optional[Faculty]:
    db_faculty = await get_faculty(db, faculty_id)
    if not db_faculty:
        return None
    
    update_dict = faculty_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(db_faculty, key, value)
    
    await db.commit()
    await db.refresh(db_faculty)
    return db_faculty
