from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Annotated
from datetime import date

from ....setup.dependencies import get_db, CurrentUser
from ....setup.storage_utils import upload_file_to_supabase
from ....schema.Part_B.research_project import (
    ResearchProjectCreate,
    ResearchProjectUpdateFaculty,
    ResearchProjectUpdateHOD,
    ResearchProjectUpdateDirector,
    ResearchProjectResponse,
    ResearchProjectSummary,
)
from ....crud.Part_B import research_project as crud_research_project

router = APIRouter()

@router.post("/research-projects", response_model=ResearchProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_research_project(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    project_name: Annotated[str, Form(...)],
    funding_agency: Annotated[str, Form(...)],
    date_of_sanction: Annotated[date, Form(...)],
    funding_amount: Annotated[float, Form(...)],
    role: Annotated[str, Form(...)],
    project_status: Annotated[str, Form(...)],
    department: Annotated[Optional[str], Form()] = None,
    file: Annotated[Optional[UploadFile], File()] = None,
):
    if "faculty" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create research projects")
    
    document_path = None
    if file:
        document_path = await upload_file_to_supabase(file, current_user.id)
    
    project = ResearchProjectCreate(
        project_name=project_name,
        funding_agency=funding_agency,
        date_of_sanction=date_of_sanction,
        funding_amount=funding_amount,
        role=role,
        project_status=project_status,
        department=department,
        document=document_path
    )
    
    return await crud_research_project.create_research_project(db=db, project=project, faculty_id=current_user.id)

@router.get("/research-projects/faculty/{faculty_id}", response_model=List[ResearchProjectResponse])
async def read_research_projects_by_faculty(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(...)],
    skip: int = 0,
    limit: int = 100,
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this faculty's research projects")
    
    projects = await crud_research_project.get_research_projects_by_faculty(db, faculty_id=faculty_id, skip=skip, limit=limit)
    return projects

@router.get("/research-projects", response_model=List[ResearchProjectResponse])
async def read_all_research_projects(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
):
    if not any(role in ["admin", "dean", "vc"] for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view all research projects")
    
    projects = await crud_research_project.get_all_research_projects(db, skip=skip, limit=limit)
    return projects

@router.put("/research-projects/{project_id}", response_model=ResearchProjectResponse)
async def update_research_project(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    project_id: Annotated[str, Path(...)],
    project_update: ResearchProjectUpdateFaculty | ResearchProjectUpdateHOD | ResearchProjectUpdateDirector,
):
    db_project = await crud_research_project.get_research_project(db, project_id)
    if db_project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research Project not found")

    if not current_user.has_authority_over(db_project.faculty_id, "faculty", getattr(db_project, "department", None)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this research project")

    # Role-based update logic
    if "admin" in current_user.roles:
        updated_project = await crud_research_project.update_research_project_faculty(db, project_id, project_update)
    elif "hod" in current_user.roles:
        if not isinstance(project_update, ResearchProjectUpdateHOD):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="HOD can only update api_score_hod")
        updated_project = await crud_research_project.update_research_project_hod(db, project_id, project_update)
    elif "director" in current_user.roles:
        if not isinstance(project_update, ResearchProjectUpdateDirector):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Director can only update api_score_director")
        updated_project = await crud_research_project.update_research_project_director(db, project_id, project_update)
    elif "faculty" in current_user.roles and db_project.faculty_id == current_user.id:
        updated_project = await crud_research_project.update_research_project_faculty(db, project_id, project_update)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this research project")

    if updated_project is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update research project")
    return updated_project

@router.delete("/research-projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_research_project(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    project_id: Annotated[str, Path(...)],
):
    db_project = await crud_research_project.get_research_project(db, project_id)
    if db_project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research Project not found")

    if not current_user.has_authority_over(db_project.faculty_id, "faculty", getattr(db_project, "department", None)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this research project")
    
    await crud_research_project.delete_research_project(db, project_id)
    return {"message": "Research Project deleted successfully"}

@router.get("/research-projects/summary/{faculty_id}", response_model=ResearchProjectSummary)
async def get_research_projects_summary(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(...)],
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this faculty's summary")
    
    total_score = await crud_research_project.get_research_projects_total_score(db, faculty_id)
    return ResearchProjectSummary(total_score=total_score)
