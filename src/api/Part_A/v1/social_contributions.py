from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Annotated

from ....setup.dependencies import get_db, get_current_user, CurrentUser
from ....setup.storage_utils import upload_file_to_supabase
from ....schema.Part_A.social_contributions import (
    SocialContributionCreate,
    SocialContributionUpdateFaculty,
    SocialContributionUpdateHOD,
    SocialContributionUpdateDirector,
    SocialContributionResponse,
)
from ....crud.Part_A import social_contributions as crud_activities

router = APIRouter()

@router.post("/social-contributions", response_model=SocialContributionResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    sr_no: Annotated[Optional[int], Form()] = None,
    activity_type: Annotated[str, Form()] = ...,
    details_of_activity: Annotated[str, Form()] = ...,
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
    return await crud_activities.create_social_contribution(db, contribution_data, current_user.id)

@router.get("/social-contributions/faculty/{faculty_id}", response_model=List[SocialContributionResponse])
async def read_activities_by_faculty(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    faculty_id: str = Path(...)
):
    if "admin" not in current_user.roles and current_user.id != faculty_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return await crud_activities.get_social_contributions_by_faculty(db, faculty_id)

@router.get("/social-contributions", response_model=List[SocialContributionResponse])
async def read_all_activities(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser
):
    if "admin" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can view all data")
    from sqlalchemy import select
    result = await db.execute(select(crud_activities.SocialContribution))
    return result.scalars().all()

@router.put("/social-contributions/{id}", response_model=SocialContributionResponse)
async def update_activity(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    id: str = Path(...),
    contribution_update: SocialContributionUpdateFaculty = None
):
    db_entry = await crud_activities.get_social_contribution(db, id)
    if not db_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if "admin" in current_user.roles or "hod" in current_user.roles:
        return await crud_activities.update_social_contribution_hod(db, id, contribution_update)
    elif "director" in current_user.roles:
        return await crud_activities.update_social_contribution_director(db, id, contribution_update)
    elif "faculty" in current_user.roles and db_entry.faculty_id == current_user.id:
        return await crud_activities.update_social_contribution_faculty(db, id, contribution_update)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

@router.delete("/social-contributions/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    id: str = Path(...)
):
    if "admin" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can delete entries")
    await crud_activities.delete_social_contribution(db, id)
    return None

@router.get("/social-contributions/summary/{faculty_id}")
async def get_activity_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    faculty_id: str = Path(...)
):
    if "admin" not in current_user.roles and current_user.id != faculty_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    activities = await crud_activities.get_social_contributions_by_faculty(db, faculty_id)
    total_score = sum([a.api_score_faculty for a in activities])
    return {"totalScore": min(total_score, 10)} # Max 10 as per PDF
