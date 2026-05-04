from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from ...models.Part_A.social_contributions import SocialContribution
from ...schema.Part_A.social_contributions import (
    SocialContributionCreate,
    SocialContributionUpdateFaculty,
    SocialContributionUpdateHOD,
    SocialContributionUpdateDirector,
)

async def get_social_contribution(db: AsyncSession, id: str) -> Optional[SocialContribution]:
    result = await db.execute(select(SocialContribution).where(SocialContribution.id == id))
    return result.scalars().first()

async def get_social_contributions_by_faculty(db: AsyncSession, faculty_id: str) -> List[SocialContribution]:
    result = await db.execute(select(SocialContribution).where(SocialContribution.faculty_id == faculty_id))
    return result.scalars().all()

async def create_social_contribution(
    db: AsyncSession, contribution: SocialContributionCreate, faculty_id: str
) -> SocialContribution:
    db_contribution = SocialContribution(**contribution.model_dump(), faculty_id=faculty_id)
    db.add(db_contribution)
    await db.commit()
    await db.refresh(db_contribution)
    return db_contribution

async def update_social_contribution_faculty(
    db: AsyncSession, id: str, contribution_update: SocialContributionUpdateFaculty
) -> Optional[SocialContribution]:
    db_contribution = await get_social_contribution(db, id)
    if db_contribution:
        update_data = contribution_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_contribution, key, value)
        await db.commit()
        await db.refresh(db_contribution)
    return db_contribution

async def update_social_contribution_hod(
    db: AsyncSession, id: str, contribution_update: SocialContributionUpdateHOD
) -> Optional[SocialContribution]:
    db_contribution = await get_social_contribution(db, id)
    if db_contribution:
        db_contribution.api_score_hod = contribution_update.api_score_hod
        await db.commit()
        await db.refresh(db_contribution)
    return db_contribution

async def update_social_contribution_director(
    db: AsyncSession, id: str, contribution_update: SocialContributionUpdateDirector
) -> Optional[SocialContribution]:
    db_contribution = await get_social_contribution(db, id)
    if db_contribution:
        db_contribution.api_score_director = contribution_update.api_score_director
        await db.commit()
        await db.refresh(db_contribution)
    return db_contribution

async def delete_social_contribution(db: AsyncSession, id: str) -> bool:
    db_contribution = await get_social_contribution(db, id)
    if db_contribution:
        await db.delete(db_contribution)
        await db.commit()
        return True
    return False

async def get_social_contribution_total_score(db: AsyncSession, faculty_id: str) -> float:
    entries = await get_social_contributions_by_faculty(db, faculty_id)
    return sum([e.api_score_faculty or 0.0 for e in entries])
