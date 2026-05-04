from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated
from ....setup.dependencies import get_db, CurrentUser
from ....crud.overall import appraisal_tracking

router = APIRouter()

@router.get("/dashboard/subordinates", response_model=List[dict])
async def get_dashboard_subordinates(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Returns a list of all faculties reporting to the current user 
    along with their appraisal submission status.
    """
    # Identify primary role for hierarchy (highest weight)
    role_weights = {"faculty": 0, "hod": 1, "director": 2, "dean": 3, "vc": 4, "admin": 5}
    if not current_user.roles:
        raise HTTPException(status_code=403, detail="No roles assigned")
        
    primary_role = max(current_user.roles, key=lambda r: role_weights.get(r, 0))
    
    if primary_role == "faculty":
        raise HTTPException(status_code=403, detail="Dashboard only available for HOD, Director, Dean, VC, and Admin")
        
    return await appraisal_tracking.get_subordinates_status(
        db, 
        role=primary_role,
        school_id=current_user.school_id,
        department=current_user.department,
        division=current_user.division
    )
