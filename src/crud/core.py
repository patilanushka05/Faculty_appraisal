from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from src.models.core import FacultyProfile, Declaration, AppraisalReview, FormSectionDefinition, AppraisalDocument
from src.schema.core import FacultyProfileCreate, FacultyProfileUpdate, DeclarationBase, AppraisalReviewBase
from typing import List, Optional
from uuid import UUID

# --- Faculty Profile CRUD ---
async def get_faculty_by_email(db: AsyncSession, email: str) -> Optional[FacultyProfile]:
    result = await db.execute(select(FacultyProfile).where(FacultyProfile.email == email))
    return result.scalar_one_or_none()

async def create_faculty_profile(db: AsyncSession, profile_in: FacultyProfileCreate) -> FacultyProfile:
    db_profile = FacultyProfile(
        **profile_in.model_dump(exclude={'password'}),
        password_hash=profile_in.password # In real app, hash it
    )
    db.add(db_profile)
    await db.commit()
    await db.refresh(db_profile)
    return db_profile

# --- Declaration (Appraisal Tracking) CRUD ---
async def get_declaration(db: AsyncSession, email: str, year: str) -> Optional[Declaration]:
    result = await db.execute(select(Declaration).where(
        Declaration.faculty_email == email,
        Declaration.academic_year == year
    ))
    return result.scalar_one_or_none()

async def create_or_update_declaration(db: AsyncSession, data: DeclarationBase) -> Declaration:
    db_decl = await get_declaration(db, data.faculty_email, data.academic_year)
    if db_decl:
        for key, value in data.model_dump().items():
            setattr(db_decl, key, value)
    else:
        db_decl = Declaration(**data.model_dump())
        db.add(db_decl)
    await db.commit()
    await db.refresh(db_decl)
    return db_decl

# --- Appraisal Review CRUD ---
async def get_reviews_by_faculty(db: AsyncSession, email: str, year: str) -> List[AppraisalReview]:
    result = await db.execute(select(AppraisalReview).where(
        AppraisalReview.faculty_email == email,
        AppraisalReview.academic_year == year
    ))
    return result.scalars().all()

async def create_or_update_review(db: AsyncSession, data: AppraisalReviewBase) -> AppraisalReview:
    result = await db.execute(select(AppraisalReview).where(
        AppraisalReview.faculty_email == data.faculty_email,
        AppraisalReview.academic_year == data.academic_year,
        AppraisalReview.reviewer_role == data.reviewer_role
    ))
    db_review = result.scalar_one_or_none()
    if db_review:
        for key, value in data.model_dump().items():
            setattr(db_review, key, value)
    else:
        db_review = AppraisalReview(**data.model_dump())
        db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    return db_review

# --- Form Section Definition ---
async def get_section_definitions(db: AsyncSession, form_family: Optional[str] = None) -> List[FormSectionDefinition]:
    query = select(FormSectionDefinition)
    if form_family:
        query = query.where(FormSectionDefinition.form_family == form_family)
    result = await db.execute(query)
    return result.scalars().all()
