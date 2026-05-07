from ...utils import mask_scores
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Annotated

from ....setup.dependencies import get_db, CurrentUser
from ....setup.storage_utils import upload_file_to_supabase
from ....schema.Part_A.social_contributions import (
    SocialContributionCreate,
    SocialContributionUpdateFaculty,
    SocialContributionUpdateHOD,
    SocialContributionUpdateDirector,
    SocialContributionUpdateDean,
    SocialContributionUpdateVC,
    SocialContributionResponse,
)
from ....crud.Part_A import social_contributions as crud_activities

router = APIRouter()

@router.post("/social-contributions", response_model=SocialContributionResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    sr_no: Annotated[Optional[int], Form()] = None,
    activity_type: Annotated[str, Form()] = None,
    details_of_activity: Annotated[str, Form()] = None,
    department: Annotated[Optional[str], Form()] = None,
    file: Optional[UploadFile] = File(None)
):
    if "faculty" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only faculty can create entries")
    
    document_path = None
    if file:
        document_path = await upload_file_to_supabase(file, current_user.id)
    
    contribution_data = SocialContributionCreate(
        sr_no=sr_no,
        activity_type=activity_type,
        details_of_activity=details_of_activity,
        department=department,
        document=document_path
    )
    return mask_scores(await crud_activities.create_social_contribution(db, contribution_data, current_user.id), current_user)

@router.get("/social-contributions/faculty/{faculty_id}", response_model=List[SocialContributionResponse])
async def read_activities_by_faculty(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    faculty_id: str = Path(...)
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return mask_scores(await crud_activities.get_social_contributions_by_faculty(db, faculty_id), current_user)

@router.get("/social-contributions", response_model=List[SocialContributionResponse])
async def read_all_activities(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser
):
    allowed_roles = {"admin", "dean", "vc"}
    if not any(role in allowed_roles for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin, dean, or vc can view all data")
    
    result = await db.execute(select(crud_activities.SocialContribution))
    res = result.scalars().all()
    return mask_scores(list(res), current_user)

@router.put("/social-contributions/{id}", response_model=SocialContributionResponse)
async def update_activity(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    id: str = Path(...),
    contribution_update: SocialContributionUpdateFaculty | SocialContributionUpdateHOD | SocialContributionUpdateDirector | SocialContributionUpdateDean | SocialContributionUpdateVC = None
):
    db_entry = await crud_activities.get_social_contribution(db, id)
    if not db_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if not current_user.has_authority_over(db_entry.faculty_id, "faculty", db_entry.department):
        raise HTTPException(status_code=403, detail="Not authorized")

    res = None
    if "vc" in current_user.roles:
        res = await crud_activities.update_social_contribution_vc(db, id, contribution_update)
    elif "dean" in current_user.roles:
        res = await crud_activities.update_social_contribution_dean(db, id, contribution_update)
    elif "director" in current_user.roles:
        res = await crud_activities.update_social_contribution_director(db, id, contribution_update)
    elif "admin" in current_user.roles or "hod" in current_user.roles:
        res = await crud_activities.update_social_contribution_hod(db, id, contribution_update)
    elif "faculty" in current_user.roles and db_entry.faculty_id == current_user.id:
        res = await crud_activities.update_social_contribution_faculty(db, id, contribution_update)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    return mask_scores(res, current_user)

@router.delete("/social-contributions/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    id: str = Path(...)
):
    db_entry = await crud_activities.get_social_contribution(db, id)
    if not db_entry:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if not current_user.has_authority_over(db_entry.faculty_id, "faculty", db_entry.department):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    await crud_activities.delete_social_contribution(db, id)
    return None

@router.get("/social-contributions/summary/{faculty_id}")
async def get_activity_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    faculty_id: str = Path(...)
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    total_score = await crud_activities.get_social_contribution_total_score(db, faculty_id)
    return {"totalScore": min(total_score, 10)} # Max 10 as per PDF
