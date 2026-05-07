from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from ...models.Part_A.student_feedback import StudentFeedback
from ...schema.Part_A.student_feedback import (
    StudentFeedbackCreate,
    StudentFeedbackUpdateFaculty,
    StudentFeedbackUpdateHOD,
    StudentFeedbackUpdateDirector,
    StudentFeedbackUpdateDean,
    StudentFeedbackUpdateVC,
)

async def get_student_feedback(db: AsyncSession, id: str) -> Optional[StudentFeedback]:
    result = await db.execute(select(StudentFeedback).where(StudentFeedback.id == id))
    return result.scalars().first()

async def get_student_feedback_by_faculty(db: AsyncSession, faculty_id: str) -> List[StudentFeedback]:
    result = await db.execute(select(StudentFeedback).where(StudentFeedback.faculty_id == faculty_id))
    return result.scalars().all()

async def create_student_feedback(db: AsyncSession, feedback: StudentFeedbackCreate, faculty_id: str) -> StudentFeedback:
    db_feedback = StudentFeedback(**feedback.model_dump(), faculty_id=faculty_id)
    db.add(db_feedback)
    await db.commit()
    await db.refresh(db_feedback)
    return db_feedback

async def update_student_feedback_faculty(
    db: AsyncSession, id: str, feedback_update: StudentFeedbackUpdateFaculty
) -> Optional[StudentFeedback]:
    db_feedback = await get_student_feedback(db, id)
    if db_feedback:
        update_data = feedback_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_feedback, key, value)
        await db.commit()
        await db.refresh(db_feedback)
    return db_feedback

async def update_student_feedback_hod(
    db: AsyncSession, id: str, feedback_update: StudentFeedbackUpdateHOD
) -> Optional[StudentFeedback]:
    db_feedback = await get_student_feedback(db, id)
    if db_feedback:
        db_feedback.api_score_hod = feedback_update.api_score_hod
        await db.commit()
        await db.refresh(db_feedback)
    return db_feedback

async def update_student_feedback_director(
    db: AsyncSession, id: str, feedback_update: StudentFeedbackUpdateDirector
) -> Optional[StudentFeedback]:
    db_feedback = await get_student_feedback(db, id)
    if db_feedback:
        db_feedback.api_score_director = feedback_update.api_score_director
        await db.commit()
        await db.refresh(db_feedback)
    return db_feedback

async def update_student_feedback_dean(
    db: AsyncSession, id: str, update: StudentFeedbackUpdateDean
) -> Optional[StudentFeedback]:
    db_obj = await get_student_feedback(db, id)
    if db_obj:
        db_obj.api_score_dean = update.api_score_dean
        await db.commit()
        await db.refresh(db_obj)
    return db_obj

async def update_student_feedback_vc(
    db: AsyncSession, id: str, update: StudentFeedbackUpdateVC
) -> Optional[StudentFeedback]:
    db_obj = await get_student_feedback(db, id)
    if db_obj:
        db_obj.api_score_vc = update.api_score_vc
        await db.commit()
        await db.refresh(db_obj)
    return db_obj

async def delete_student_feedback(db: AsyncSession, id: str) -> bool:
    db_feedback = await get_student_feedback(db, id)
    if db_feedback:
        await db.delete(db_feedback)
        await db.commit()
        return True
    return False

async def get_student_feedback_total_score(db: AsyncSession, faculty_id: str) -> float:
    entries = await get_student_feedback_by_faculty(db, faculty_id)
    if not entries:
        return 0.0
    
    # Calculate average for each entry and then average of averages
    total_avg = sum([(e.first_feedback + e.second_feedback) / 2 for e in entries])
    return total_avg / len(entries)
