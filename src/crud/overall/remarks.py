from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import Optional, List
from ...models.overall.remarks import AppraisalRemarks, HODRemarks, DirectorRemarks, DeanRemarks, FinalApproval
from ...schema.overall.remarks import (
    AppraisalRemarksCreate, HODRemarksCreate, DirectorRemarksCreate, 
    DeanRemarksCreate, FinalApprovalCreate
)

# Appraisal Remarks (General)
async def get_appraisal_remarks_by_faculty(db: AsyncSession, faculty_id: str) -> List[AppraisalRemarks]:
    result = await db.execute(select(AppraisalRemarks).filter(AppraisalRemarks.faculty_id == faculty_id))
    return result.scalars().all()

async def create_appraisal_remarks(db: AsyncSession, faculty_id: str, data: AppraisalRemarksCreate) -> AppraisalRemarks:
    db_remarks = AppraisalRemarks(**data.model_dump(), faculty_id=faculty_id)
    db.add(db_remarks)
    await db.commit()
    await db.refresh(db_remarks)
    return db_remarks

# HOD Remarks
async def get_hod_remarks_by_faculty(db: AsyncSession, faculty_id: str) -> Optional[HODRemarks]:
    result = await db.execute(select(HODRemarks).filter(HODRemarks.faculty_id == faculty_id))
    return result.scalars().first()

async def create_or_update_hod_remarks(db: AsyncSession, faculty_id: str, data: HODRemarksCreate) -> HODRemarks:
    db_remarks = await get_hod_remarks_by_faculty(db, faculty_id)
    if db_remarks:
        for key, value in data.model_dump().items():
            setattr(db_remarks, key, value)
    else:
        db_remarks = HODRemarks(**data.model_dump(), faculty_id=faculty_id)
        db.add(db_remarks)
    await db.commit()
    await db.refresh(db_remarks)
    return db_remarks

# Director Remarks
async def get_director_remarks_by_faculty(db: AsyncSession, faculty_id: str) -> Optional[DirectorRemarks]:
    result = await db.execute(select(DirectorRemarks).filter(DirectorRemarks.faculty_id == faculty_id))
    return result.scalars().first()

async def create_or_update_director_remarks(db: AsyncSession, faculty_id: str, data: DirectorRemarksCreate) -> DirectorRemarks:
    db_remarks = await get_director_remarks_by_faculty(db, faculty_id)
    if db_remarks:
        for key, value in data.model_dump().items():
            setattr(db_remarks, key, value)
    else:
        db_remarks = DirectorRemarks(**data.model_dump(), faculty_id=faculty_id)
        db.add(db_remarks)
    await db.commit()
    await db.refresh(db_remarks)
    return db_remarks

# Dean Remarks
async def get_dean_remarks_by_faculty(db: AsyncSession, faculty_id: str) -> Optional[DeanRemarks]:
    result = await db.execute(select(DeanRemarks).filter(DeanRemarks.faculty_id == faculty_id))
    return result.scalars().first()

async def create_or_update_dean_remarks(db: AsyncSession, faculty_id: str, data: DeanRemarksCreate) -> DeanRemarks:
    db_remarks = await get_dean_remarks_by_faculty(db, faculty_id)
    if db_remarks:
        for key, value in data.model_dump().items():
            setattr(db_remarks, key, value)
    else:
        db_remarks = DeanRemarks(**data.model_dump(), faculty_id=faculty_id)
        db.add(db_remarks)
    await db.commit()
    await db.refresh(db_remarks)
    return db_remarks

# Final Approval (VC)
async def get_final_approval_by_faculty(db: AsyncSession, faculty_id: str) -> Optional[FinalApproval]:
    result = await db.execute(select(FinalApproval).filter(FinalApproval.faculty_id == faculty_id))
    return result.scalars().first()

async def create_or_update_final_approval(db: AsyncSession, faculty_id: str, data: FinalApprovalCreate) -> FinalApproval:
    db_approval = await get_final_approval_by_faculty(db, faculty_id)
    if db_approval:
        for key, value in data.model_dump().items():
            setattr(db_approval, key, value)
    else:
        db_approval = FinalApproval(**data.model_dump(), faculty_id=faculty_id)
        db.add(db_approval)
    await db.commit()
    await db.refresh(db_approval)
    return db_approval
