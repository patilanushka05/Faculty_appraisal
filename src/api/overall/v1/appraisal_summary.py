from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated

from ....setup.dependencies import get_db, CurrentUser
from ....schema.overall.appraisal_summary import AppraisalSummaryResponse, AppraisalSubmitRequest, AppraisalSubmitResponse
from ....crud.overall import appraisal_summary as crud_appraisal_summary
from ....crud.overall import appraisal_tracking
from ....models.overall.appraisal_summary import AppraisalStatus

router = APIRouter()

@router.get("/appraisal-summary/{faculty_id}", response_model=AppraisalSummaryResponse)
async def get_appraisal_summary_endpoint(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(...)],
):
    """
    **Get the aggregated appraisal summary for a faculty member.**

    - **URL Path:** `/api/v1/appraisal-summary/{faculty_id}`
    - **Description:** Combines scores from Part A (Teaching) and Part B (Research/Activities) to provide a total score.
    - **Access Control:** Faculty can see their own summary; Higher authorities can see subordinates.
    - **Response:**
        - `part_a_score`: Total from Teaching categories (Max 200).
        - `part_b_score`: Total from Research categories (Max 375).
        - `grand_total_score`: Combined total.
        - `status`: Current status of the appraisal (DRAFT, SUBMITTED, etc.).
    """
    # Hierarchy check
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this faculty's appraisal summary")
    
    summary = await crud_appraisal_summary.get_appraisal_summary(db, faculty_id)
    return summary

@router.post("/appraisal-summary/submit", response_model=AppraisalSubmitResponse)
async def submit_appraisal(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    request: AppraisalSubmitRequest,
):
    """
    **Submit the final appraisal form.**

    - **URL Path:** `/api/v1/appraisal-summary/submit`
    - **Description:** Finalizes the appraisal for the current academic year and changes status to `SUBMITTED`.
    - **Request Body (JSON):**
        - `academic_year` (str): The year of appraisal (e.g., "2025-26").
    - **Response:**
        - Returns the current submission status and final aggregated score.
    """
    # 1. Calculate current final score
    summary = await crud_appraisal_summary.get_appraisal_summary(db, current_user.id)
    
    # 2. Update tracking status to SUBMITTED
    db_summary = await appraisal_tracking.create_or_update_summary_status(
        db, 
        faculty_id=current_user.id,
        status=AppraisalStatus.SUBMITTED,
        academic_year=request.academic_year,
        overall_score=summary.grand_total_score
    )
    
    return AppraisalSubmitResponse(
        faculty_id=db_summary.faculty_id,
        status=db_summary.status,
        overall_score=db_summary.overall_score,
        academic_year=db_summary.academic_year
    )
