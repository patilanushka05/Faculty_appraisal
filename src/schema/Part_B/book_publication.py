from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class BookPublicationBase(BaseModel):
    title_and_pages: str = Field(..., description="Title of the chapter/book and page numbers")
    book_title_editor: str = Field(..., description="Title of the book and editor's name")
    issn_isbn: str = Field(..., description="ISSN/ISBN number")
    publisher_type: str = Field(..., description="Type of publisher (e.g., National, International)")
    co_authors_count: int = Field(..., description="Number of co-authors")
    is_first_author: bool = Field(False, description="True if the faculty is the first author")
    department: Optional[str] = Field(None, description="Department of the faculty") # Added as per user request
    document: Optional[str] = Field(None, description="Google Drive link to the document") # Added as per user request

class BookPublicationCreate(BookPublicationBase):
    pass

class BookPublicationUpdateFaculty(BookPublicationBase):
    title_and_pages: Optional[str] = Field(None, description="Title of the chapter/book and page numbers")
    book_title_editor: Optional[str] = Field(None, description="Title of the book and editor's name")
    issn_isbn: Optional[str] = Field(None, description="ISSN/ISBN number")
    publisher_type: Optional[str] = Field(None, description="Type of publisher (e.g., National, International)")
    co_authors_count: Optional[int] = Field(None, description="Number of co-authors")
    is_first_author: Optional[bool] = Field(None, description="True if the faculty is the first author")
    department: Optional[str] = Field(None, description="Department of the faculty")
    document: Optional[str] = Field(None, description="Google Drive link to the document")

class BookPublicationUpdateHOD(BaseModel):
    api_score_hod: int = Field(..., description="API score given by HOD")

class BookPublicationUpdateDirector(BaseModel):
    api_score_director: int = Field(..., description="API score given by Director")


class BookPublicationUpdateDean(BaseModel):
    api_score_dean: float

class BookPublicationUpdateVC(BaseModel):
    api_score_vc: float

class BookPublicationResponse(BookPublicationBase):
    id: UUID
    faculty_id: UUID
    api_score_faculty: int
    api_score_hod: int
    api_score_director: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BookPublicationSummary(BaseModel):
    total_score: float
