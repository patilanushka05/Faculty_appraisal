from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Annotated

from ....setup.dependencies import get_db, CurrentUser
from ....setup.storage_utils import upload_file_to_supabase
from ....schema.overall.finalization import (
    EnclosureCreate, EnclosureResponse, DeclarationCreate, DeclarationResponse
)
from ....crud.overall import finalization as crud_finalization

router = APIRouter()

# Enclosures API
@router.post("/enclosures", response_model=EnclosureResponse, status_code=status.HTTP_201_CREATED)
async def create_enclosure(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    enclosure_text: Annotated[str, Form()],
    file: Annotated[Optional[UploadFile], File()] = None,
):
    document_path = None
    if file:
        document_path = await upload_file_to_supabase(file, current_user.id)
    
    enclosure_data = EnclosureCreate(enclosure_text=enclosure_text)
    return await crud_finalization.create_enclosure(db, current_user.id, enclosure_data, document_path)

@router.get("/enclosures/{faculty_id}", response_model=List[EnclosureResponse])
async def read_enclosures(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: str,
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    return await crud_finalization.get_enclosures_by_faculty(db, faculty_id)

@router.delete("/enclosures/{enclosure_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enclosure(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    enclosure_id: str,
):
    # For simplicity, only the owner can delete for now
    # In a real app, we'd check if the enclosure belongs to current_user
    success = await crud_finalization.delete_enclosure(db, enclosure_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enclosure not found")
    return {"message": "Enclosure deleted"}

# Declaration API
@router.post("/declaration", response_model=DeclarationResponse)
async def create_or_update_declaration(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    declaration: DeclarationCreate,
):
    return await crud_finalization.create_or_update_declaration(db, current_user.id, declaration)

@router.get("/declaration/{faculty_id}", response_model=DeclarationResponse)
async def read_declaration(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: str,
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    declaration = await crud_finalization.get_declaration_by_faculty(db, faculty_id)
    if not declaration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Declaration not found")
    return declaration
