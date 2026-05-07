from ...utils import mask_scores
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Annotated

from ....setup.dependencies import get_db, CurrentUser
from ....setup.storage_utils import upload_file_to_supabase
from ....schema.Part_B.product_development import (
    ProductDevelopmentCreate,
    ProductDevelopmentUpdateFaculty,
    ProductDevelopmentUpdateHOD,
    ProductDevelopmentUpdateDirector,
    ProductDevelopmentResponse,
    ProductDevelopmentSummary,
    ProductDevelopmentUpdateDean,
    ProductDevelopmentUpdateVC,)
from ....crud.Part_B import product_development as crud_product_development
from ....models.Part_B.product_development import ProductDevelopment as DBProductDevelopment

router = APIRouter()

@router.post("/products", response_model=ProductDevelopmentResponse, status_code=status.HTTP_201_CREATED)
async def create_product_development(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    product_description: Annotated[str, Form(...)],
    usage_type: Annotated[str, Form(...)],
    department: Annotated[Optional[str], Form()] = None,
    file: Annotated[Optional[UploadFile], File()] = None,
):
    if "faculty" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create product developments")
    
    document_path = None
    if file:
        document_path = await upload_file_to_supabase(file, current_user.id)
    
    product = ProductDevelopmentCreate(
        product_description=product_description,
        usage_type=usage_type,
        department=department,
        document=document_path
    )
    
    return mask_scores(await crud_product_development.create_product_development(db=db, product=product, faculty_id=current_user.id), current_user)

@router.get("/products/faculty/{faculty_id}", response_model=List[ProductDevelopmentResponse])
async def read_product_developments_by_faculty(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(...)],
    skip: int = 0,
    limit: int = 100,
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this faculty's product developments")
    
    products = await crud_product_development.get_product_developments_by_faculty(db, faculty_id=faculty_id, skip=skip, limit=limit)
    return products

@router.get("/products", response_model=List[ProductDevelopmentResponse])
async def read_all_product_developments(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
):
    if not any(role in ["admin", "dean", "vc"] for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view all product developments")
    
    products = await crud_product_development.get_all_product_developments(db, skip=skip, limit=limit)
    return products

@router.put("/products/{product_id}", response_model=ProductDevelopmentResponse)
async def update_product_development(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    product_id: Annotated[str, Path(...)],
    product_update: ProductDevelopmentUpdateFaculty | ProductDevelopmentUpdateHOD | ProductDevelopmentUpdateDirector,
):
    db_product = await crud_product_development.get_product_development(db, product_id)
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product Development entry not found")

    if not current_user.has_authority_over(db_product.faculty_id, "faculty", getattr(db_product, "department", None)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this product development entry")

    # Role-based update logic
    if "admin" in current_user.roles:
        updated_product = await crud_product_development.update_product_development_faculty(db, product_id, product_update)
    elif "hod" in current_user.roles:
        if not isinstance(product_update, ProductDevelopmentUpdateHOD):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="HOD can only update api_score_hod")
        updated_product = await crud_product_development.update_product_development_hod(db, product_id, product_update)
    elif "director" in current_user.roles:
        if not isinstance(product_update, ProductDevelopmentUpdateDirector):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Director can only update api_score_director")
        updated_product = await crud_product_development.update_product_development_director(db, product_id, product_update)
    elif "faculty" in current_user.roles and db_product.faculty_id == current_user.id:
        updated_product = await crud_product_development.update_product_development_faculty(db, product_id, product_update)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this product development entry")

    if updated_product is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update product development entry")
    return updated_product

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_development(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    product_id: Annotated[str, Path(...)],
):
    db_product = await crud_product_development.get_product_development(db, product_id)
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product Development entry not found")

    if not current_user.has_authority_over(db_product.faculty_id, "faculty", getattr(db_product, "department", None)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this product development entry")
    
    await crud_product_development.delete_product_development(db, product_id)
    return {"message": "Product Development entry deleted successfully"}

@router.get("/products/summary/{faculty_id}", response_model=ProductDevelopmentSummary)
async def get_product_developments_summary(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(...)],
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this faculty's summary")
    
    total_score = await crud_product_development.get_product_developments_total_score(db, faculty_id)
    return ProductDevelopmentSummary(total_score=total_score)
