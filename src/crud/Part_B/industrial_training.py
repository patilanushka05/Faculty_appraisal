from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from src.models.Part_B.industrial_training import IndustrialTraining
from src.schema.Part_B.industrial_training import (
    IndustrialTrainingCreate,
    IndustrialTrainingUpdateFaculty,
    IndustrialTrainingUpdateHOD,
    IndustrialTrainingUpdateDirector,
    IndustrialTrainingUpdateDean,
    IndustrialTrainingUpdateVC,)

async def get_industrial_training(db: AsyncSession, training_id: str) -> Optional[IndustrialTraining]:
    result = await db.execute(select(IndustrialTraining).where(IndustrialTraining.id == training_id))
    return result.scalars().first()

async def get_industrial_trainings_by_faculty(db: AsyncSession, faculty_id: str, skip: int = 0, limit: int = 100) -> List[IndustrialTraining]:
    result = await db.execute(select(IndustrialTraining).where(IndustrialTraining.faculty_id == faculty_id).offset(skip).limit(limit))
    return result.scalars().all()

async def get_all_industrial_trainings(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[IndustrialTraining]:
    result = await db.execute(select(IndustrialTraining).offset(skip).limit(limit))
    return result.scalars().all()

async def create_industrial_training(db: AsyncSession, training: IndustrialTrainingCreate, faculty_id: str) -> IndustrialTraining:
    db_training = IndustrialTraining(**training.model_dump(), faculty_id=faculty_id)
    db.add(db_training)
    await db.commit()
    await db.refresh(db_training)
    return db_training

async def update_industrial_training_faculty(
    db: AsyncSession, training_id: str, training_update: IndustrialTrainingUpdateFaculty
) -> Optional[IndustrialTraining]:
    db_training = await get_industrial_training(db, training_id)
    if db_training:
        update_data = training_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_training, key, value)
        await db.commit()
        await db.refresh(db_training)
    return db_training

async def update_industrial_training_hod(
    db: AsyncSession, training_id: str, training_update: IndustrialTrainingUpdateHOD
) -> Optional[IndustrialTraining]:
    db_training = await get_industrial_training(db, training_id)
    if db_training:
        db_training.api_score_hod = training_update.api_score_hod
        await db.commit()
        await db.refresh(db_training)
    return db_training

async def update_industrial_training_director(
    db: AsyncSession, training_id: str, training_update: IndustrialTrainingUpdateDirector
) -> Optional[IndustrialTraining]:
    db_training = await get_industrial_training(db, training_id)
    if db_training:
        db_training.api_score_director = training_update.api_score_director
        await db.commit()
        await db.refresh(db_training)
    return db_training

async def delete_industrial_training(db: AsyncSession, training_id: str) -> Optional[IndustrialTraining]:
    db_training = await get_industrial_training(db, training_id)
    if db_training:
        await db.delete(db_training)
        await db.commit()
    return db_training

async def get_industrial_trainings_total_score(db: AsyncSession, faculty_id: str) -> float:
    result = await db.execute(select(IndustrialTraining).where(IndustrialTraining.faculty_id == faculty_id))
    trainings = result.scalars().all()
    total_score = sum([t.api_score_faculty or 0.0 for t in trainings])
    return total_score

async def update_industrial_training_dean(
    db: AsyncSession, id: str, update: IndustrialTrainingUpdateDean
) -> Optional[IndustrialTraining]:
    db_obj = await get_industrial_training(db, id)
    if db_obj:
        db_obj.api_score_dean = update.api_score_dean
        await db.commit()
        await db.refresh(db_obj)
    return db_obj

async def update_industrial_training_vc(
    db: AsyncSession, id: str, update: IndustrialTrainingUpdateVC
) -> Optional[IndustrialTraining]:
    db_obj = await get_industrial_training(db, id)
    if db_obj:
        db_obj.api_score_vc = update.api_score_vc
        await db.commit()
        await db.refresh(db_obj)
    return db_obj
