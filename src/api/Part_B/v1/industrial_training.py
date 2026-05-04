from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Annotated

from ....setup.dependencies import get_db, CurrentUser
from ....setup.storage_utils import upload_file_to_supabase
from ....schema.Part_B.industrial_training import (
    IndustrialTrainingCreate,
    IndustrialTrainingUpdateFaculty,
    IndustrialTrainingUpdateHOD,
    IndustrialTrainingUpdateDirector,
    IndustrialTrainingResponse,
    IndustrialTrainingSummary,
)
from ....crud.Part_B import industrial_training as crud_industrial_training
from ....models.Part_B.industrial_training import IndustrialTraining as DBIndustrialTraining

router = APIRouter()

@router.post("/industrial-training", response_model=IndustrialTrainingResponse, status_code=status.HTTP_201_CREATED)
async def create_industrial_training(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    company_industry: Annotated[str, Form()] = ...,
    duration_days: Annotated[int, Form()] = ...,
    nature_of_training: Annotated[str, Form()] = ...,
    department: Annotated[Optional[str], Form()] = None,
    file: Optional[UploadFile] = File(None)
):
    if "faculty" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create industrial training entries")
    
    document_path = None
    if file:
        document_path = await upload_file_to_supabase(file, current_user.id)
    
    training = IndustrialTrainingCreate(
        company_industry=company_industry,
        duration_days=duration_days,
        nature_of_training=nature_of_training,
        department=department,
        document=document_path
    )
    
    return await crud_industrial_training.create_industrial_training(db=db, training=training, faculty_id=current_user.id)

@router.get("/industrial-training/faculty/{faculty_id}", response_model=List[IndustrialTrainingResponse])
async def read_industrial_trainings_by_faculty(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    faculty_id: str = Path(...),
    skip: int = Query(0),
    limit: int = Query(100)
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this faculty's industrial training entries")
    
    trainings = await crud_industrial_training.get_industrial_trainings_by_faculty(db, faculty_id=faculty_id, skip=skip, limit=limit)
    return trainings

@router.get("/industrial-training", response_model=List[IndustrialTrainingResponse])
async def read_all_industrial_trainings(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    skip: int = Query(0),
    limit: int = Query(100)
):
    if not any(role in ["admin", "dean", "vc"] for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view all industrial training entries")
    
    trainings = await crud_industrial_training.get_all_industrial_trainings(db, skip=skip, limit=limit)
    return trainings

@router.put("/industrial-training/{training_id}", response_model=IndustrialTrainingResponse)
async def update_industrial_training(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    training_id: str = Path(...),
    training_update: IndustrialTrainingUpdateFaculty = None
):
    db_training = await crud_industrial_training.get_industrial_training(db, training_id)
    if db_training is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Industrial Training entry not found")

    if not current_user.has_authority_over(db_training.faculty_id, "faculty", getattr(db_training, "department", None)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this industrial training entry")

    # Role-based update logic
    if "admin" in current_user.roles:
        updated_training = await crud_industrial_training.update_industrial_training_faculty(db, training_id, training_update)
    elif "hod" in current_user.roles:
        updated_training = await crud_industrial_training.update_industrial_training_hod(db, training_id, training_update)
    elif "director" in current_user.roles:
        updated_training = await crud_industrial_training.update_industrial_training_director(db, training_id, training_update)
    elif "faculty" in current_user.roles and db_training.faculty_id == current_user.id:
        updated_training = await crud_industrial_training.update_industrial_training_faculty(db, training_id, training_update)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this industrial training entry")

    if updated_training is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update industrial training entry")
    return updated_training

@router.delete("/industrial-training/{training_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_industrial_training(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    training_id: str = Path(...)
):
    db_training = await crud_industrial_training.get_industrial_training(db, training_id)
    if db_training is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Industrial Training entry not found")

    if not current_user.has_authority_over(db_training.faculty_id, "faculty", getattr(db_training, "department", None)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this industrial training entry")
    
    await crud_industrial_training.delete_industrial_training(db, training_id)
    return {"message": "Industrial Training entry deleted successfully"}

@router.get("/industrial-training/summary/{faculty_id}", response_model=IndustrialTrainingSummary)
async def get_industrial_trainings_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    faculty_id: str = Path(...)
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this faculty's summary")
    
    total_score = await crud_industrial_training.get_industrial_trainings_total_score(db, faculty_id)
    return IndustrialTrainingSummary(total_score=total_score)
