from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from src.models.Part_B.product_development import ProductDevelopment
from src.schema.Part_B.product_development import (
    ProductDevelopmentCreate,
    ProductDevelopmentUpdateFaculty,
    ProductDevelopmentUpdateHOD,
    ProductDevelopmentUpdateDirector,
)

async def get_product_development(db: AsyncSession, product_id: str) -> Optional[ProductDevelopment]:
    result = await db.execute(select(ProductDevelopment).where(ProductDevelopment.id == product_id))
    return result.scalars().first()

async def get_product_developments_by_faculty(db: AsyncSession, faculty_id: str, skip: int = 0, limit: int = 100) -> List[ProductDevelopment]:
    result = await db.execute(select(ProductDevelopment).where(ProductDevelopment.faculty_id == faculty_id).offset(skip).limit(limit))
    return result.scalars().all()

async def get_all_product_developments(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ProductDevelopment]:
    result = await db.execute(select(ProductDevelopment).offset(skip).limit(limit))
    return result.scalars().all()

async def create_product_development(db: AsyncSession, product: ProductDevelopmentCreate, faculty_id: str) -> ProductDevelopment:
    db_product = ProductDevelopment(**product.model_dump(), faculty_id=faculty_id)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

async def update_product_development_faculty(
    db: AsyncSession, product_id: str, product_update: ProductDevelopmentUpdateFaculty
) -> Optional[ProductDevelopment]:
    db_product = await get_product_development(db, product_id)
    if db_product:
        update_data = product_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)
        await db.commit()
        await db.refresh(db_product)
    return db_product

async def update_product_development_hod(
    db: AsyncSession, product_id: str, product_update: ProductDevelopmentUpdateHOD
) -> Optional[ProductDevelopment]:
    db_product = await get_product_development(db, product_id)
    if db_product:
        db_product.api_score_hod = product_update.api_score_hod
        await db.commit()
        await db.refresh(db_product)
    return db_product

async def update_product_development_director(
    db: AsyncSession, product_id: str, product_update: ProductDevelopmentUpdateDirector
) -> Optional[ProductDevelopment]:
    db_product = await get_product_development(db, product_id)
    if db_product:
        db_product.api_score_director = product_update.api_score_director
        await db.commit()
        await db.refresh(db_product)
    return db_product

async def delete_product_development(db: AsyncSession, product_id: str) -> Optional[ProductDevelopment]:
    db_product = await get_product_development(db, product_id)
    if db_product:
        await db.delete(db_product)
        await db.commit()
    return db_product

async def get_product_developments_total_score(db: AsyncSession, faculty_id: str) -> float:
    result = await db.execute(select(ProductDevelopment).where(ProductDevelopment.faculty_id == faculty_id))
    products = result.scalars().all()
    total_score = sum([p.api_score_faculty or 0.0 for p in products])
    return total_score
