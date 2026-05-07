from ...utils import mask_scores
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Annotated

from ....setup.dependencies import get_db, CurrentUser
from ....setup.storage_utils import upload_file_to_supabase
from ....schema.Part_A.qualification_enhancement import (
    QualificationEnhancementCreate,
    QualificationEnhancementUpdateFaculty,
    QualificationEnhancementUpdateHOD,
    QualificationEnhancementUpdateDirector,
    QualificationEnhancementUpdateDean,
    QualificationEnhancementUpdateVC,
    QualificationEnhancementResponse,
)
from ....crud.Part_A import qualification_enhancement as crud_qualification

router = APIRouter()

@router.post("/qualification-enhancement", response_model=QualificationEnhancementResponse, status_code=status.HTTP_201_CREATED)
async def create_qualification(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    sr_no: Annotated[Optional[int], Form()] = None,
    qualification_type: Annotated[str, Form()] = None,
    department: Annotated[Optional[str], Form()] = None,
    file: Annotated[Optional[UploadFile], File()] = None,
):
    if "faculty" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only faculty can create entries")
    
    document_path = None
    if file:
        document_path = await upload_file_to_supabase(file, current_user.id)
    
    qualification_data = QualificationEnhancementCreate(
        sr_no=sr_no,
        qualification_type=qualification_type,
        department=department,
        document=document_path
    )
    return mask_scores(await crud_qualification.create_qualification_enhancement(db, qualification_data, current_user.id), current_user)

@router.get("/qualification-enhancement/faculty/{faculty_id}", response_model=List[QualificationEnhancementResponse])
async def read_qualifications_by_faculty(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path()],
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return mask_scores(await crud_qualification.get_qualification_enhancements_by_faculty(db, faculty_id), current_user)

@router.get("/qualification-enhancement", response_model=List[QualificationEnhancementResponse])
async def read_all_qualifications(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    allowed_roles = {"admin", "dean", "vc"}
    if not any(role in allowed_roles for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin, dean, or vc can view all data")
    
    result = await db.execute(select(crud_qualification.QualificationEnhancement))
    res = result.scalars().all()
    return mask_scores(list(res), current_user)

@router.put("/qualification-enhancement/{id}", response_model=QualificationEnhancementResponse)
async def update_qualification(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    id: Annotated[str, Path()],
    qualification_update: QualificationEnhancementUpdateFaculty | QualificationEnhancementUpdateHOD | QualificationEnhancementUpdateDirector | QualificationEnhancementUpdateDean | QualificationEnhancementUpdateVC,
):
    db_entry = await crud_qualification.get_qualification_enhancement(db, id)
    if not db_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if not current_user.has_authority_over(db_entry.faculty_id, "faculty", db_entry.department):
        raise HTTPException(status_code=403, detail="Not authorized")

    res = None
    if "vc" in current_user.roles:
        res = await crud_qualification.update_qualification_enhancement_vc(db, id, qualification_update)
    elif "dean" in current_user.roles:
        res = await crud_qualification.update_qualification_enhancement_dean(db, id, qualification_update)
    elif "director" in current_user.roles:
        res = await crud_qualification.update_qualification_enhancement_director(db, id, qualification_update)
    elif "admin" in current_user.roles or "hod" in current_user.roles:
        res = await crud_qualification.update_qualification_enhancement_hod(db, id, qualification_update)
    elif "faculty" in current_user.roles and db_entry.faculty_id == current_user.id:
        res = await crud_qualification.update_qualification_enhancement_faculty(db, id, qualification_update)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    return mask_scores(res, current_user)

@router.delete("/qualification-enhancement/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_qualification(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    id: Annotated[str, Path()],
):
    db_entry = await crud_qualification.get_qualification_enhancement(db, id)
    if not db_entry:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if not current_user.has_authority_over(db_entry.faculty_id, "faculty", db_entry.department):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    await crud_qualification.delete_qualification_enhancement(db, id)
    return None

@router.get("/qualification-enhancement/summary/{faculty_id}")
async def read_qualification_summary(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path()],
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    total_score = await crud_qualification.get_qualification_enhancement_total_score(db, faculty_id)
    return {"totalScore": total_score}
