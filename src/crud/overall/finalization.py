from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional
from ...models.overall.finalization import Enclosure, Declaration
from ...schema.overall.finalization import EnclosureCreate, DeclarationCreate

# Enclosures CRUD
async def get_enclosures_by_faculty(db: AsyncSession, faculty_id: str) -> List[Enclosure]:
    result = await db.execute(select(Enclosure).filter(Enclosure.faculty_id == faculty_id))
    return result.scalars().all()

async def create_enclosure(db: AsyncSession, faculty_id: str, enclosure: EnclosureCreate, document_path: Optional[str] = None) -> Enclosure:
    db_enclosure = Enclosure(**enclosure.model_dump(), faculty_id=faculty_id, document=document_path)
    db.add(db_enclosure)
    await db.commit()
    await db.refresh(db_enclosure)
    return db_enclosure

async def delete_enclosure(db: AsyncSession, enclosure_id: str) -> bool:
    result = await db.execute(select(Enclosure).filter(Enclosure.id == enclosure_id))
    db_enclosure = result.scalars().first()
    if db_enclosure:
        await db.delete(db_enclosure)
        await db.commit()
        return True
    return False

# Declaration CRUD
async def get_declaration_by_faculty(db: AsyncSession, faculty_id: str) -> Optional[Declaration]:
    result = await db.execute(select(Declaration).filter(Declaration.faculty_id == faculty_id))
    return result.scalars().first()

async def create_or_update_declaration(db: AsyncSession, faculty_id: str, declaration: DeclarationCreate) -> Declaration:
    db_declaration = await get_declaration_by_faculty(db, faculty_id)
    if db_declaration:
        for key, value in declaration.model_dump().items():
            setattr(db_declaration, key, value)
    else:
        db_declaration = Declaration(**declaration.model_dump(), faculty_id=faculty_id)
        db.add(db_declaration)
    
    await db.commit()
    await db.refresh(db_declaration)
    return db_declaration
