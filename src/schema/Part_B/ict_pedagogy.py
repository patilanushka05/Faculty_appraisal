from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

# Base schema for common attributes
class ICTPedagogyBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str = Field(..., max_length=500)
    pedagogy_type: str = Field(..., max_length=100)
    quadrants: int
    department: Optional[str] = Field(None, description="Department of the faculty") # Added as per user request
    document: Optional[str] = Field(None, description="Google Drive link to the document") # Added as per user request

# Schema for creating a new ICT Pedagogy entry (Faculty input)
class ICTPedagogyCreate(ICTPedagogyBase):
    pass

# Schema for faculty to update their own ICT Pedagogy entry
class ICTPedagogyUpdateFaculty(ICTPedagogyBase):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    pedagogy_type: Optional[str] = Field(None, max_length=100)
    quadrants: Optional[int] = None

# Schema for HOD to update API score
class ICTPedagogyUpdateHOD(BaseModel):
    api_score_hod: float

# Schema for Director to update API score
class ICTPedagogyUpdateDirector(BaseModel):
    api_score_director: float

class ICTPedagogyUpdateDean(BaseModel):
    api_score_dean: float

class ICTPedagogyUpdateVC(BaseModel):
    api_score_vc: float

# Schema for API response
class ICTPedagogyResponse(ICTPedagogyBase):
    id: UUID
    faculty_id: UUID
    api_score_faculty: int
    api_score_hod: float
    api_score_director: float

    class Config:
        from_attributes = True

# Schema for total score summary
class ICTPedagogySummary(BaseModel):
    total_score: float
