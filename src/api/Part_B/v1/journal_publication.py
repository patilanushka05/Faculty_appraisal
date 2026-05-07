from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Annotated

from ....setup.dependencies import get_db, CurrentUser
from ....setup.storage_utils import upload_file_to_supabase
from ....schema.Part_B.journal_publication import (
    JournalPublicationCreate,
    JournalPublicationUpdateFaculty,
    JournalPublicationUpdateHOD,
    JournalPublicationUpdateDirector,
    JournalPublicationUpdateDean,
    JournalPublicationUpdateVC,
    JournalPublicationResponse,
    JournalPublicationSummary,)
from ....models.Part_B.journal_publication import IndexingEnum
from ....crud.Part_B import journal_publication as crud_journal_publication
from ...utils import mask_scores

router = APIRouter()

@router.post("/journal-publications", response_model=JournalPublicationResponse, status_code=status.HTTP_201_CREATED)
async def create_journal_publication(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    sr_no: Annotated[Optional[int], Form(description="Serial number of the publication")] = None,
    title_with_page_nos: Annotated[Optional[str], Form(description="Title of the paper with page numbers")] = None,
    journal_details: Annotated[Optional[str], Form(description="Name and details of the journal")] = None,
    issn_isbn_no: Annotated[Optional[str], Form(description="ISSN/ISBN number of the journal")] = None,
    indexing: Annotated[Optional[IndexingEnum], Form(description="Indexing of the journal (SCOPUS, WOS, UGC_CARE, PEER_REVIEWED)")] = None,
    department: Annotated[Optional[str], Form(description="Department of the faculty")] = None,
    file: Annotated[Optional[UploadFile], File(description="PDF proof of the journal publication")] = None,
):
    """
    **Create a new Journal Publication entry.**

    - **URL Path:** `/api/v1/part-b/journal-publications`
    - **Role Required:** `faculty`
    - **Request Body (Form-Data):**
        - `sr_no` (int): Serial number.
        - `title_with_page_nos` (str): Full title of the paper.
        - `journal_details` (str): Journal name, volume, issue, etc.
        - `issn_isbn_no` (str): Unique ISSN or ISBN code.
        - `indexing` (string): One of `SCOPUS`, `WOS`, `UGC_CARE`, or `PEER_REVIEWED`.
        - `department` (str): Faculty's department.
        - `file` (file): PDF document for verification.
    - **Response:**
        - Returns the created `JournalPublicationResponse` object including `id`, `faculty_id`, and calculated `api_score_faculty`.
    """
    if "faculty" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create journal publications")
    
    document_path = None
    if file:
        document_path = await upload_file_to_supabase(file, current_user.id)
    
    publication = JournalPublicationCreate(
        sr_no=sr_no,
        title_with_page_nos=title_with_page_nos,
        journal_details=journal_details,
        issn_isbn=issn_isbn_no,
        indexing=indexing,
        department=department,
        document=document_path
    )

    
    return await crud_journal_publication.create_journal_publication(db=db, publication=publication, faculty_id=current_user.id)

@router.get("/journal-publications/faculty/{faculty_id}", response_model=List[JournalPublicationResponse])
async def read_journal_publications_by_faculty(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(description="UUID of the faculty member")],
    skip: int = 0,
    limit: int = 100
):
    """
    **Retrieve all journal publications for a specific faculty.**

    - **URL Path:** `/api/v1/part-b/journal-publications/faculty/{faculty_id}`
    - **Access Control:** Higher authorities (HOD, Director, etc.) can see their subordinates' data.
    - **Response:** List of journal publication objects.
    """
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this faculty's journal publications")
    
    publications = await crud_journal_publication.get_journal_publications_by_faculty(db, faculty_id=faculty_id, skip=skip, limit=limit)
    return mask_scores(publications, current_user)

@router.get("/journal-publications", response_model=List[JournalPublicationResponse])
async def read_all_journal_publications(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100
):
    """
    **Retrieve all journal publications (Admin/Dean/VC only).**

    - **URL Path:** `/api/v1/part-b/journal-publications`
    - **Response:** List of all journal publication objects in the system.
    """
    if not any(role in ["admin", "dean", "vc"] for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view all journal publications")
    
    publications = await crud_journal_publication.get_all_journal_publications(db, skip=skip, limit=limit)
    return mask_scores(publications, current_user)

@router.put("/journal-publications/{publication_id}", response_model=JournalPublicationResponse)
async def update_journal_publication(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    publication_id: Annotated[str, Path(description="UUID of the publication record")],
    publication_update: JournalPublicationUpdateFaculty | JournalPublicationUpdateHOD | JournalPublicationUpdateDirector | JournalPublicationUpdateDean | JournalPublicationUpdateVC,
):
    """
    **Update an existing journal publication.**

    - **URL Path:** `/api/v1/part-b/journal-publications/{publication_id}`
    - **Update Logic:**
        - **Faculty:** Can update fields like title, journal details, etc.
        - **HOD:** Can only update `api_score_hod`.
        - **Director:** Can only update `api_score_director`.
        - **Dean:** Can only update `api_score_dean`.
        - **VC:** Can only update `api_score_vc`.
    - **Response:** The updated journal publication object.
    """
    db_publication = await crud_journal_publication.get_journal_publication(db, publication_id)
    if db_publication is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal Publication not found")

    if not current_user.has_authority_over(db_publication.faculty_id, "faculty", getattr(db_publication, "department", None)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this journal publication")

    # Role-based update logic
    if "admin" in current_user.roles:
        updated_publication = await crud_journal_publication.update_journal_publication_faculty(db, publication_id, publication_update)
    elif "vc" in current_user.roles:
        if not isinstance(publication_update, JournalPublicationUpdateVC):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="VC can only update api_score_vc")
        updated_publication = await crud_journal_publication.update_journal_publication_vc(db, publication_id, publication_update)
    elif "dean" in current_user.roles:
        if not isinstance(publication_update, JournalPublicationUpdateDean):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dean can only update api_score_dean")
        updated_publication = await crud_journal_publication.update_journal_publication_dean(db, publication_id, publication_update)
    elif "director" in current_user.roles:
        if not isinstance(publication_update, JournalPublicationUpdateDirector):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Director can only update api_score_director")
        updated_publication = await crud_journal_publication.update_journal_publication_director(db, publication_id, publication_update)
    elif "hod" in current_user.roles:
        if not isinstance(publication_update, JournalPublicationUpdateHOD):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="HOD can only update api_score_hod")
        updated_publication = await crud_journal_publication.update_journal_publication_hod(db, publication_id, publication_update)
    elif "faculty" in current_user.roles and db_publication.faculty_id == current_user.id:
        updated_publication = await crud_journal_publication.update_journal_publication_faculty(db, publication_id, publication_update)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this journal publication")

    if updated_publication is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update journal publication")
    return mask_scores(updated_publication, current_user)

@router.delete("/journal-publications/{publication_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_journal_publication(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    publication_id: Annotated[str, Path(description="UUID of the publication record")],
):
    """
    **Delete a journal publication record.**

    - **URL Path:** `/api/v1/part-b/journal-publications/{publication_id}`
    - **Response:** 204 No Content on success.
    """
    db_publication = await crud_journal_publication.get_journal_publication(db, publication_id)
    if db_publication is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal Publication not found")

    if not current_user.has_authority_over(db_publication.faculty_id, "faculty", getattr(db_publication, "department", None)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this journal publication")
    
    await crud_journal_publication.delete_journal_publication(db, publication_id)
    return {"message": "Journal Publication deleted successfully"}

@router.get("/journal-publications/summary/{faculty_id}", response_model=JournalPublicationSummary)
async def get_journal_publications_summary(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    faculty_id: Annotated[str, Path(description="UUID of the faculty member")],
):
    """
    **Get the total API score summary for journal publications.**

    - **URL Path:** `/api/v1/part-b/journal-publications/summary/{faculty_id}`
    - **Response:** Total score (sum of all verified journal publications).
    """
    if not current_user.has_authority_over(faculty_id, "faculty"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this faculty's summary")
    
    total_score = await crud_journal_publication.get_journal_publications_total_score(db, faculty_id)
    return JournalPublicationSummary(total_score=total_score)
