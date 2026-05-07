from ...utils import mask_scores
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Annotated

from ....setup.dependencies import get_db, CurrentUser
from ....setup.storage_utils import upload_file_to_supabase
from ....schema.Part_B.book_publication import (
    BookPublicationCreate,
    BookPublicationUpdateFaculty,
    BookPublicationUpdateHOD,
    BookPublicationUpdateDirector,
    BookPublicationResponse,
    BookPublicationSummary,
    BookPublicationUpdateDean,
    BookPublicationUpdateVC,)
from ....crud.Part_B import book_publication as crud_book_publication
from ....models.Part_B.book_publication import BookPublication as DBBookPublication

router = APIRouter()

@router.post("/book-publications", response_model=BookPublicationResponse, status_code=status.HTTP_201_CREATED)
async def create_book_publication(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    title_and_pages: Annotated[str, Form()] = ...,
    book_title_editor: Annotated[str, Form()] = ...,
    issn_isbn: Annotated[str, Form()] = ...,
    publisher_type: Annotated[str, Form()] = ...,
    co_authors_count: Annotated[int, Form()] = ...,
    is_first_author: Annotated[bool, Form()] = False,
    department: Annotated[Optional[str], Form()] = None,
    file: Optional[UploadFile] = File(None)
):
    if "faculty" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create book publications")

    document_path = None
    if file:
        document_path = await upload_file_to_supabase(file, current_user.id)

    publication = BookPublicationCreate(
        title_and_pages=title_and_pages,
        book_title_editor=book_title_editor,
        issn_isbn=issn_isbn,
        publisher_type=publisher_type,
        co_authors_count=co_authors_count,
        is_first_author=is_first_author,
        department=department,
        document=document_path
    )

    return mask_scores(await crud_book_publication.create_book_publication(db=db, publication=publication, faculty_id=current_user.id), current_user)

@router.get("/book-publications/faculty/{faculty_id}", response_model=List[BookPublicationResponse])
async def read_book_publications_by_faculty(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    faculty_id: str = Path(...),
    skip: int = Query(0),
    limit: int = Query(100)
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this faculty's book publications")

    publications = await crud_book_publication.get_book_publications_by_faculty(db, faculty_id=faculty_id, skip=skip, limit=limit)
    return publications

@router.get("/book-publications", response_model=List[BookPublicationResponse])
async def read_all_book_publications(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    skip: int = Query(0),
    limit: int = Query(100)
):
    if not any(role in ["admin", "dean", "vc"] for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view all book publications")

    publications = await crud_book_publication.get_all_book_publications(db, skip=skip, limit=limit)
    return publications

@router.put("/book-publications/{publication_id}", response_model=BookPublicationResponse)
async def update_book_publication(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    publication_id: str = Path(...),
    publication_update: BookPublicationUpdateFaculty = None
):
    db_publication = await crud_book_publication.get_book_publication(db, publication_id)
    if db_publication is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book Publication not found")

    if not current_user.has_authority_over(db_publication.faculty_id, "faculty", getattr(db_publication, "department", None)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this book publication")

    # Role-based update logic
    if "admin" in current_user.roles:
        updated_publication = await crud_book_publication.update_book_publication_faculty(db, publication_id, publication_update)
    elif "hod" in current_user.roles:
        updated_publication = await crud_book_publication.update_book_publication_hod(db, publication_id, publication_update)
    elif "director" in current_user.roles:
        updated_publication = await crud_book_publication.update_book_publication_director(db, publication_id, publication_update)
    elif "faculty" in current_user.roles and db_publication.faculty_id == current_user.id:
        updated_publication = await crud_book_publication.update_book_publication_faculty(db, publication_id, publication_update)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this book publication")

    if updated_publication is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update book publication")
    return updated_publication

@router.delete("/book-publications/{publication_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book_publication(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    publication_id: str = Path(...)
):
    db_publication = await crud_book_publication.get_book_publication(db, publication_id)
    if db_publication is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book Publication not found")

    if not current_user.has_authority_over(db_publication.faculty_id, "faculty", getattr(db_publication, "department", None)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this book publication")

    await crud_book_publication.delete_book_publication(db, publication_id)
    return {"message": "Book Publication deleted successfully"}

@router.get("/book-publications/summary/{faculty_id}", response_model=BookPublicationSummary)
async def get_book_publications_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    faculty_id: str = Path(...)
):
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this faculty's summary")

    total_score = await crud_book_publication.get_book_publications_total_score(db, faculty_id)
    return BookPublicationSummary(total_score=total_score)