from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Annotated, Union

from ....setup.dependencies import get_db, CurrentUser
from ....setup.storage_utils import upload_file_to_supabase
from ....schema.Part_A.industry_connect import (
    IndustryConnectCreate,
    IndustryConnectUpdateFaculty,
    IndustryConnectUpdateHOD,
    IndustryConnectUpdateDirector,
    IndustryConnectUpdateDean,
    IndustryConnectUpdateVC,
    IndustryConnectResponse,
)
from ....crud.Part_A import industry_connect as crud_activities
from ...utils import mask_scores

router = APIRouter()

@router.post("/industry-connect", response_model=IndustryConnectResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    sr_no: Annotated[Optional[int], Form()] = None,
    industry_name: Annotated[str, Form()] = None,
    details_of_activity: Annotated[str, Form()] = None,
    department: Annotated[Optional[str], Form()] = None,
    file: Annotated[Optional[UploadFile], File()] = None,
):
    if "faculty" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only faculty can create entries")
    
    document_path = None
    if file:
        document_path = await upload_file_to_supabase(file, current_user.id)
    
    connect_data = IndustryConnectCreate(
        sr_no=sr_no,
        industry_name=industry_name,
        details_of_activity=details_of_activity,
        department=department,
        document=document_path
    )
    return mask_scores(await crud_activities.create_industry_connect(db, connect_data, current_user.id), current_user)

@router.get("/industry-connect/faculty/{faculty_id}", response_model=List[IndustryConnectResponse])
async def read_activities_by_faculty(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path()],
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return mask_scores(await crud_activities.get_industry_connect_by_faculty(db, faculty_id), current_user)

@router.get("/industry-connect", response_model=List[IndustryConnectResponse])
async def read_all_activities(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    allowed_roles = {"admin", "dean", "vc"}
    if not any(role in allowed_roles for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin, dean, or vc can view all data")
    
    result = await db.execute(select(crud_activities.IndustryConnect))
    res = result.scalars().all()
    return mask_scores(list(res), current_user)

@router.put("/industry-connect/{id}", response_model=IndustryConnectResponse)
async def update_activity(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    id: Annotated[str, Path()],
    connect_update: IndustryConnectUpdateFaculty | IndustryConnectUpdateHOD | IndustryConnectUpdateDirector | IndustryConnectUpdateDean | IndustryConnectUpdateVC,
):
    db_entry = await crud_activities.get_industry_connect(db, id)
    if not db_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if not current_user.has_authority_over(db_entry.faculty_id, "faculty", db_entry.department):
        raise HTTPException(status_code=403, detail="Not authorized")

    res = None
    if "admin" in current_user.roles:
        res = await crud_activities.update_industry_connect_faculty(db, id, connect_update)
    elif "vc" in current_user.roles:
        res = await crud_activities.update_industry_connect_vc(db, id, connect_update)
    elif "dean" in current_user.roles:
        res = await crud_activities.update_industry_connect_dean(db, id, connect_update)
    elif "director" in current_user.roles:
        res = await crud_activities.update_industry_connect_director(db, id, connect_update)
    elif "hod" in current_user.roles:
        res = await crud_activities.update_industry_connect_hod(db, id, connect_update)
    elif "faculty" in current_user.roles:
        res = await crud_activities.update_industry_connect_faculty(db, id, connect_update)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access for this role")

    return mask_scores(res, current_user)

@router.delete("/industry-connect/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    id: Annotated[str, Path()],
):
    db_entry = await crud_activities.get_industry_connect(db, id)
    if not db_entry:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    
    if not current_user.has_authority_over(db_entry.faculty_id, "faculty", db_entry.department):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        
    await crud_activities.delete_industry_connect(db, id)
    return None

@router.get("/industry-connect/summary/{faculty_id}")
async def get_activity_summary(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path()],
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    total_score = await crud_activities.get_industry_connect_total_score(db, faculty_id)
    return {"totalScore": min(total_score, 5)}
