from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Annotated

from ....setup.dependencies import get_db, CurrentUser
from ....setup.storage_utils import upload_file_to_supabase
from ....schema.Part_A.project import (
    ProjectPartACreate,
    ProjectPartAUpdateFaculty,
    ProjectPartAUpdateHOD,
    ProjectPartAUpdateDirector,
    ProjectPartAResponse,
)
from ....crud.Part_A import project as crud_project

router = APIRouter()

@router.post("/projects", response_model=ProjectPartAResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    sr_no: Annotated[Optional[int], Form()] = None,
    project_type: Annotated[str, Form()] = None,
    department: Annotated[Optional[str], Form()] = None,
    file: Annotated[Optional[UploadFile], File()] = None,
):
    if "faculty" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only faculty can create entries")
    
    document_path = None
    if file:
        document_path = await upload_file_to_supabase(file, current_user.id)
    
    project_data = ProjectPartACreate(
        sr_no=sr_no,
        project_type=project_type,
        department=department,
        document=document_path
    )
    return await crud_project.create_project(db, project_data, current_user.id)

@router.get("/projects/faculty/{faculty_id}", response_model=List[ProjectPartAResponse])
async def read_projects_by_faculty(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path()],
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return await crud_project.get_projects_by_faculty(db, faculty_id)

@router.get("/projects", response_model=List[ProjectPartAResponse])
async def read_all_projects(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    allowed_roles = {"admin", "dean", "vc"}
    if not any(role in allowed_roles for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin, dean, or vc can view all data")
    
    result = await db.execute(select(crud_project.ProjectPartA))
    return result.scalars().all()

@router.put("/projects/{id}", response_model=ProjectPartAResponse)
async def update_project(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    id: Annotated[str, Path()],
    project_update: ProjectPartAUpdateFaculty,
):
    db_entry = await crud_project.get_project(db, id)
    if not db_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if not current_user.has_authority_over(db_entry.faculty_id, "faculty", db_entry.department):
        raise HTTPException(status_code=403, detail="Not authorized")

    if "admin" in current_user.roles or "hod" in current_user.roles:
        return await crud_project.update_project_hod(db, id, project_update)
    elif "director" in current_user.roles:
        return await crud_project.update_project_director(db, id, project_update)
    elif "faculty" in current_user.roles and db_entry.faculty_id == current_user.id:
        return await crud_project.update_project_faculty(db, id, project_update)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

@router.delete("/projects/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    id: Annotated[str, Path()],
):
    db_entry = await crud_project.get_project(db, id)
    if not db_entry:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if not current_user.has_authority_over(db_entry.faculty_id, "faculty", db_entry.department):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    await crud_project.delete_project(db, id)
    return None

@router.get("/projects/summary/{faculty_id}")
async def read_project_summary(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path()],
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    total_score = await crud_project.get_project_total_score(db, faculty_id)
    return {"totalScore": total_score}
