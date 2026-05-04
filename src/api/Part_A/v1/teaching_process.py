from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Annotated

from ....setup.dependencies import get_db, CurrentUser
from ....setup.storage_utils import upload_file_to_supabase
from ....schema.Part_A.teaching_process import (
    TeachingProcessCreate,
    TeachingProcessUpdateFaculty,
    TeachingProcessUpdateHOD,
    TeachingProcessResponse,
)
from ....crud.Part_A import teaching_process as crud_teaching_process

router = APIRouter()

@router.post("/teaching-process", response_model=TeachingProcessResponse, status_code=status.HTTP_201_CREATED)
async def create_teaching_process(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    sr_no: Annotated[Optional[int], Form(description="Serial number of the record")] = None,
    semester: Annotated[str, Form(description="Academic semester (e.g., Autumn 2025)")] = None,
    course_code_name: Annotated[str, Form(description="Code and name of the course")] = None,
    planned_classes: Annotated[int, Form(description="Number of classes planned")] = 0,
    conducted_classes: Annotated[int, Form(description="Number of classes actually conducted")] = 0,
    department: Annotated[Optional[str], Form(description="Faculty department")] = None,
    file: Annotated[Optional[UploadFile], File(description="PDF proof of teaching activities")] = None,
):
    if "faculty" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only faculty can fill their own teaching data")
    
    document_path = None
    if file:
        document_path = await upload_file_to_supabase(file, current_user.id)
    
    teaching_data = TeachingProcessCreate(
        sr_no=sr_no,
        semester=semester,
        course_code_name=course_code_name,
        planned_classes=planned_classes,
        conducted_classes=conducted_classes,
        department=department,
        document=document_path
    )
    return await crud_teaching_process.create_teaching_process(db, teaching_data, current_user.id)

@router.get("/teaching-process/faculty/{faculty_id}", response_model=List[TeachingProcessResponse])
async def read_teaching_process_by_faculty(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(description="UUID of the faculty member")],
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this data")
    return await crud_teaching_process.get_teaching_process_by_faculty(db, faculty_id)

@router.get("/teaching-process", response_model=List[TeachingProcessResponse])
async def read_all_teaching_process(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    if "admin" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can view all teaching data")
    
    result = await db.execute(select(crud_teaching_process.TeachingProcess))
    return result.scalars().all()

@router.put("/teaching-process/{id}", response_model=TeachingProcessResponse)
async def update_teaching_process(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    id: Annotated[str, Path(description="UUID of the teaching process record")],
    teaching_update: TeachingProcessUpdateFaculty,
):
    db_teaching = await crud_teaching_process.get_teaching_process(db, id)
    if not db_teaching:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if not current_user.has_authority_over(db_teaching.faculty_id, "faculty", db_teaching.department):
        raise HTTPException(status_code=403, detail="Not authorized")

    if "admin" in current_user.roles or "hod" in current_user.roles:
        return await crud_teaching_process.update_teaching_process_hod(db, id, teaching_update)
    elif "faculty" in current_user.roles and db_teaching.faculty_id == current_user.id:
        return await crud_teaching_process.update_teaching_process_faculty(db, id, teaching_update)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

@router.delete("/teaching-process/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teaching_process(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    id: Annotated[str, Path(description="UUID of the teaching process record")],
):
    if "admin" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can delete entries")
    await crud_teaching_process.delete_teaching_process(db, id)
    return None

@router.get("/teaching-process/summary/{faculty_id}")
async def read_teaching_process_summary(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(description="UUID of the faculty member")],
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    total_score = await crud_teaching_process.get_teaching_process_total_score(db, faculty_id)
    return {
        "totalMarksOutOf100": total_score,
        "scaledMarksOutOf25": total_score * 0.25
    }
