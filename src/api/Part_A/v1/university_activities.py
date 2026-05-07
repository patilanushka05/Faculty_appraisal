from ...utils import mask_scores
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Annotated, Union

from ....setup.dependencies import get_db, CurrentUser
from ....setup.storage_utils import upload_file_to_supabase
from ....schema.Part_A.university_activities import (
    UniversityActivityCreate,
    UniversityActivityUpdateFaculty,
    UniversityActivityUpdateHOD,
    UniversityActivityUpdateDirector,
    UniversityActivityUpdateDean,
    UniversityActivityUpdateVC,
    UniversityActivityResponse,
)
from ....crud.Part_A import university_activities as crud_university_activities

router = APIRouter()

@router.post("/university-activities", response_model=UniversityActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_university_activity(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    activity_name: Annotated[str, Form(description="Name of the university activity")],
    role_responsibility: Annotated[str, Form(description="Role or responsibility held")],
    sr_no: Annotated[Optional[int], Form(description="Serial number")] = None,
    department: Annotated[Optional[str], Form(description="Faculty department")] = None,
    file: Annotated[Optional[UploadFile], File(description="PDF proof of activity")] = None,
):
    if "faculty" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only faculty can create their activities")
    
    document_path = None
    if file:
        document_path = await upload_file_to_supabase(file, current_user.id)
    
    activity_data = UniversityActivityCreate(
        sr_no=sr_no,
        activity_name=activity_name,
        role_responsibility=role_responsibility,
        department=department,
        document=document_path
    )
    res = await crud_university_activities.create_university_activity(db, activity_data, current_user.id)
    return mask_scores(res, current_user)

@router.get("/university-activities/faculty/{faculty_id}", response_model=List[UniversityActivityResponse])
async def read_university_activities_by_faculty(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(description="UUID of the faculty member")],
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=403, detail="Not authorized")
    res = await crud_university_activities.get_university_activities_by_faculty(db, faculty_id)
    return mask_scores(res, current_user)

@router.get("/university-activities", response_model=List[UniversityActivityResponse])
async def read_all_university_activities(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    if "admin" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can view all data")
    
    result = await db.execute(select(crud_university_activities.UniversityActivity))
    res = result.scalars().all()
    return mask_scores(list(res), current_user)

@router.put("/university-activities/{id}", response_model=UniversityActivityResponse)
async def update_university_activity(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    id: Annotated[str, Path()],
    activity_update: Union[UniversityActivityUpdateFaculty, UniversityActivityUpdateHOD, UniversityActivityUpdateDirector, UniversityActivityUpdateDean, UniversityActivityUpdateVC],
):
    db_activity = await crud_university_activities.get_university_activity(db, id)
    if not db_activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if not current_user.has_authority_over(db_activity.faculty_id, "faculty", db_activity.department):
        raise HTTPException(status_code=403, detail="Not authorized")

    res = None
    if "admin" in current_user.roles:
        res = await crud_university_activities.update_university_activity_hod(db, id, activity_update)
    elif "vc" in current_user.roles:
        res = await crud_university_activities.update_university_activity_vc(db, id, activity_update)
    elif "dean" in current_user.roles:
        res = await crud_university_activities.update_university_activity_dean(db, id, activity_update)
    elif "director" in current_user.roles:
        res = await crud_university_activities.update_university_activity_director(db, id, activity_update)
    elif "hod" in current_user.roles:
        res = await crud_university_activities.update_university_activity_hod(db, id, activity_update)
    elif "faculty" in current_user.roles and db_activity.faculty_id == current_user.id:
        res = await crud_university_activities.update_university_activity_faculty(db, id, activity_update)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    return mask_scores(res, current_user)

@router.delete("/university-activities/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_university_activity(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    id: Annotated[str, Path()],
):
    if "admin" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can delete")
    await crud_university_activities.delete_university_activity(db, id)
    return None

@router.get("/university-activities/summary/{faculty_id}")
async def read_university_activities_summary(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path()],
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=403, detail="Not authorized")
    total_score = await crud_university_activities.get_university_activity_total_score(db, faculty_id)
    return {"totalScore": min(total_score, 10)}
