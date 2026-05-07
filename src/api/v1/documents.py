from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.setup.database import get_db
from src.setup.dependencies import CurrentUser
from src.models.core import AppraisalDocument
from sqlalchemy import select
from typing import List

router = APIRouter(prefix="/appraisal-documents", tags=["Appraisal Documents"])

@router.get("/")
async def get_documents(academic_year: str, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AppraisalDocument).where(
        AppraisalDocument.faculty_email == current_user.email,
        AppraisalDocument.academic_year == academic_year
    ))
    return result.scalars().all()
