from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from ...models.Part_A.qualification_enhancement import QualificationEnhancement
from ...schema.Part_A.qualification_enhancement import (
    QualificationEnhancementCreate,
    QualificationEnhancementUpdateFaculty,
    QualificationEnhancementUpdateHOD,
    QualificationEnhancementUpdateDirector,
    QualificationEnhancementUpdateDean,
    QualificationEnhancementUpdateVC,
)

async def get_qualification_enhancement(db: AsyncSession, id: str) -> Optional[QualificationEnhancement]:
    result = await db.execute(select(QualificationEnhancement).where(QualificationEnhancement.id == id))
    return result.scalars().first()

async def get_qualification_enhancements_by_faculty(db: AsyncSession, faculty_id: str) -> List[QualificationEnhancement]:
    result = await db.execute(select(QualificationEnhancement).where(QualificationEnhancement.faculty_id == faculty_id))
    return result.scalars().all()

async def create_qualification_enhancement(
    db: AsyncSession, qualification: QualificationEnhancementCreate, faculty_id: str
) -> QualificationEnhancement:
    db_qualification = QualificationEnhancement(**qualification.model_dump(), faculty_id=faculty_id)
    db.add(db_qualification)
    await db.commit()
    await db.refresh(db_qualification)
    return db_qualification

async def update_qualification_enhancement_faculty(
    db: AsyncSession, id: str, qualification_update: QualificationEnhancementUpdateFaculty
) -> Optional[QualificationEnhancement]:
    db_qualification = await get_qualification_enhancement(db, id)
    if db_qualification:
        update_data = qualification_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_qualification, key, value)
        await db.commit()
        await db.refresh(db_qualification)
    return db_qualification

async def update_qualification_enhancement_hod(
    db: AsyncSession, id: str, qualification_update: QualificationEnhancementUpdateHOD
) -> Optional[QualificationEnhancement]:
    db_qualification = await get_qualification_enhancement(db, id)
    if db_qualification:
        db_qualification.api_score_hod = qualification_update.api_score_hod
        await db.commit()
        await db.refresh(db_qualification)
    return db_qualification

async def update_qualification_enhancement_director(
    db: AsyncSession, id: str, qualification_update: QualificationEnhancementUpdateDirector
) -> Optional[QualificationEnhancement]:
    db_qualification = await get_qualification_enhancement(db, id)
    if db_qualification:
        db_qualification.api_score_director = qualification_update.api_score_director
        await db.commit()
        await db.refresh(db_qualification)
    return db_qualification

async def delete_qualification_enhancement(db: AsyncSession, id: str) -> bool:
    db_qualification = await get_qualification_enhancement(db, id)
    if db_qualification:
        await db.delete(db_qualification)
        await db.commit()
        return True
    return False

async def get_qualification_enhancement_total_score(db: AsyncSession, faculty_id: str) -> float:
    entries = await get_qualification_enhancements_by_faculty(db, faculty_id)
    return sum([e.api_score_faculty or 0.0 for e in entries])

async def update_qualification_enhancement_dean(
    db: AsyncSession, id: str, update: QualificationEnhancementUpdateDean
) -> Optional[QualificationEnhancement]:
    db_obj = await get_qualification_enhancement(db, id)
    if db_obj:
        db_obj.api_score_dean = update.api_score_dean
        await db.commit()
        await db.refresh(db_obj)
    return db_obj

async def update_qualification_enhancement_vc(
    db: AsyncSession, id: str, update: QualificationEnhancementUpdateVC
) -> Optional[QualificationEnhancement]:
    db_obj = await get_qualification_enhancement(db, id)
    if db_obj:
        db_obj.api_score_vc = update.api_score_vc
        await db.commit()
        await db.refresh(db_obj)
    return db_obj
