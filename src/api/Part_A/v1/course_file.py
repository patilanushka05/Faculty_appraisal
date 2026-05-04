from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Annotated, Union

from ....setup.dependencies import get_db, CurrentUser
from ....setup.storage_utils import upload_file_to_supabase
from ....schema.Part_A.course_file import (
    CourseFileCreate,
    CourseFileUpdateFaculty,
    CourseFileUpdateHOD,
    CourseFileResponse,
)
from ....crud.Part_A import course_file as crud_course_file

router = APIRouter()

@router.post("/course-files", response_model=CourseFileResponse, status_code=status.HTTP_201_CREATED)
async def create_course_file(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    course_paper: Annotated[str, Form()],
    title: Annotated[str, Form()],
    sr_no: Annotated[Optional[int], Form()] = None,
    details_proof: Annotated[bool, Form()] = False,
    department: Annotated[Optional[str], Form()] = None,
    file: Annotated[Optional[UploadFile], File()] = None,
):
    if "faculty" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only faculty can create entries")
    
    document_path = None
    if file:
        document_path = await upload_file_to_supabase(file, current_user.id)
    
    course_file_data = CourseFileCreate(
        sr_no=sr_no,
        course_paper=course_paper,
        title=title,
        details_proof=details_proof,
        department=department,
        document=document_path
    )
    return await crud_course_file.create_course_file(db, course_file_data, current_user.id)

@router.get("/course-files/faculty/{faculty_id}", response_model=List[CourseFileResponse])
async def read_course_files_by_faculty(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path()],
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=403, detail="Not authorized")
    return await crud_course_file.get_course_files_by_faculty(db, faculty_id)

@router.get("/course-files", response_model=List[CourseFileResponse])
async def read_all_course_files(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    allowed_roles = {"admin", "dean", "vc"}
    if not any(role in allowed_roles for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin, dean, or vc can view all data")
    
    result = await db.execute(select(crud_course_file.CourseFile))
    return result.scalars().all()

@router.put("/course-files/{id}", response_model=CourseFileResponse)
async def update_course_file(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    id: Annotated[str, Path()],
    course_file_update: Union[CourseFileUpdateFaculty, CourseFileUpdateHOD],
):
    db_entry = await crud_course_file.get_course_file(db, id)
    if not db_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if not current_user.has_authority_over(db_entry.faculty_id, "faculty", db_entry.department):
        raise HTTPException(status_code=403, detail="Not authorized")

    if current_user.id == db_entry.faculty_id and "faculty" in current_user.roles:
        if isinstance(course_file_update, CourseFileUpdateFaculty):
            return await crud_course_file.update_course_file_faculty(db, id, course_file_update)
        else:
             raise HTTPException(status_code=400, detail="Invalid update data for faculty")
    
    # Authority confirmed (HOD or higher)
    if any(role in ["hod", "director", "dean", "vc", "admin"] for role in current_user.roles):
        if isinstance(course_file_update, CourseFileUpdateHOD):
            return await crud_course_file.update_course_file_hod(db, id, course_file_update)
        else:
             # Fallback if update data was sent as Faculty schema but user is HOD
             # This might happen if frontend doesn't distinguish.
             return await crud_course_file.update_course_file_hod(db, id, course_file_update)

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

@router.delete("/course-files/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course_file(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    id: Annotated[str, Path()],
):
    db_entry = await crud_course_file.get_course_file(db, id)
    if not db_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if not current_user.has_authority_over(db_entry.faculty_id, "faculty", db_entry.department):
        raise HTTPException(status_code=403, detail="Not authorized")

    await crud_course_file.delete_course_file(db, id)
    return None

@router.get("/course-files/summary/{faculty_id}")
async def read_course_file_summary(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path()],
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    total_score = await crud_course_file.get_course_file_total_score(db, faculty_id)
    return {"totalScore": total_score}
