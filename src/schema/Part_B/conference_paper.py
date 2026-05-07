from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from uuid import UUID

# Base schema for common attributes
class ConferencePaperBase(BaseModel):
    event_title: str = Field(..., max_length=500)
    event_date: date
    activity_type: str = Field(..., max_length=50) # Lecture / Resource Person / Paper / Proceedings
    hosting_organization: str = Field(..., max_length=255)
    event_level: str = Field(..., max_length=50) # International / National
    department: Optional[str] = Field(None, description="Department of the faculty") # Added as per user request
    document: Optional[str] = Field(None, description="Google Drive link to the document") # Added as per user request

# Schema for creating a new Conference Paper entry (Faculty input)
class ConferencePaperCreate(ConferencePaperBase):
    pass

# Schema for faculty to update their own Conference Paper entry
class ConferencePaperUpdateFaculty(ConferencePaperBase):
    event_title: Optional[str] = Field(None, max_length=500)
    event_date: Optional[date] = None
    activity_type: Optional[str] = Field(None, max_length=50)
    hosting_organization: Optional[str] = Field(None, max_length=255)
    event_level: Optional[str] = Field(None, max_length=50)

# Schema for HOD to update API score
class ConferencePaperUpdateHOD(BaseModel):
    api_score_hod: float

# Schema for Director to update API score
class ConferencePaperUpdateDirector(BaseModel):
    api_score_director: float

# Schema for API response

class ConferencePaperUpdateDean(BaseModel):
    api_score_dean: float

class ConferencePaperUpdateVC(BaseModel):
    api_score_vc: float

class ConferencePaperResponse(ConferencePaperBase):
    id: UUID
    faculty_id: UUID
    api_score_faculty: float
    api_score_hod: float
    api_score_director: float
    api_score_dean: float
    api_score_vc: float

    class Config:
        from_attributes = True

# Schema for total score summary
class ConferencePaperSummary(BaseModel):
    total_score: float
