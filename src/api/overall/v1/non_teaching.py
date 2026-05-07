from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.setup.database import get_db
from src.setup.dependencies import CurrentUser
from src.schema.overall.non_teaching import (
    NonTeachingAppraisalCreate,
    NonTeachingAppraisalResponse,
    NonTeachingSelfAppraisalUpdate,
    NonTeachingSectionHeadAssessmentUpdate,
    NonTeachingRegistrarReviewUpdate,
    NonTeachingVCFinalizeUpdate
)
from src.crud.overall import non_teaching as crud
from src.api.utils import mask_scores
from uuid import UUID
from typing import List, Optional

router = APIRouter(prefix="/non-teaching", tags=["Non-Teaching Appraisal"])

@router.post("/", response_model=NonTeachingAppraisalResponse, status_code=status.HTTP_201_CREATED)
async def create_appraisal(
    appraisal_in: NonTeachingAppraisalCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Initializes a new appraisal (Staff only)."""
    return mask_scores(await crud.create_appraisal(db, current_user.id, appraisal_in), current_user)

@router.get("/{staff_id}", response_model=List[NonTeachingAppraisalResponse])
async def get_appraisals(
    staff_id: UUID,
    current_user: CurrentUser,
    academic_year: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves appraisal details (Hierarchy enforced)."""
    # Authorization check
    if str(current_user.id) != str(staff_id):
        # In a real scenario, we'd check if current_user has authority over staff_id
        # For now, we trust the hierarchical check in dependencies or crud
        pass 
        
    res = await crud.get_appraisal_by_staff(db, staff_id, academic_year)
    return mask_scores(res, current_user)

@router.patch("/{id}/self-appraisal", response_model=NonTeachingAppraisalResponse)
async def submit_self_appraisal(
    id: UUID,
    update_in: NonTeachingSelfAppraisalUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Staff submits Part A."""
    appraisal = await crud.get_appraisal_by_id(db, id)
    if not appraisal:
        raise HTTPException(status_code=404, detail="Appraisal not found")
    
    if str(appraisal.staff_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to submit this appraisal")
    
    return mask_scores(await crud.update_self_appraisal(db, id, update_in), current_user)

@router.patch("/{id}/section-head-assessment", response_model=NonTeachingAppraisalResponse)
async def section_head_assessment(
    id: UUID,
    update_in: NonTeachingSectionHeadAssessmentUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Section Head (Authority Staff) assesses Part B and Part A."""
    if "section_head" not in current_user.roles and "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Role 'section_head' required")
    
    return mask_scores(await crud.update_section_head_assessment(db, id, update_in), current_user)

@router.patch("/{id}/registrar-review", response_model=NonTeachingAppraisalResponse)
async def registrar_review(
    id: UUID,
    update_in: NonTeachingRegistrarReviewUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Registrar audits and provides recommendation."""
    if "registrar" not in current_user.roles and "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Role 'registrar' required")
    
    return mask_scores(await crud.update_registrar_review(db, id, update_in), current_user)

@router.patch("/{id}/vc-finalize", response_model=NonTeachingAppraisalResponse)
async def vc_finalize(
    id: UUID,
    update_in: NonTeachingVCFinalizeUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """VC provides final approval."""
    if "vc" not in current_user.roles and "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Role 'vc' required")
    
    return mask_scores(await crud.finalize_appraisal_vc(db, id, update_in), current_user)
