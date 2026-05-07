from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from uuid import UUID

# Base schema for common attributes
class ResearchProjectBase(BaseModel):
    project_name: str = Field(..., max_length=500)
    funding_agency: str = Field(..., max_length=255)
    date_of_sanction: date
    funding_amount: float
    role: str = Field(..., max_length=50)
    project_status: str = Field(..., max_length=50)
    department: Optional[str] = Field(None, description="Department of the faculty") # Added as per user request
    document: Optional[str] = Field(None, description="Google Drive link to the document") # Added as per user request

# Schema for creating a new Research Project entry (Faculty input)
class ResearchProjectCreate(ResearchProjectBase):
    pass

# Schema for faculty to update their own Research Project entry
class ResearchProjectUpdateFaculty(ResearchProjectBase):
    project_name: Optional[str] = Field(None, max_length=500)
    funding_agency: Optional[str] = Field(None, max_length=255)
    date_of_sanction: Optional[date] = None
    funding_amount: Optional[float] = None
    role: Optional[str] = Field(None, max_length=50)
    project_status: Optional[str] = Field(None, max_length=50)

# Schema for HOD to update API score
class ResearchProjectUpdateHOD(BaseModel):
    api_score_hod: float

# Schema for Director to update API score
class ResearchProjectUpdateDirector(BaseModel):
    api_score_director: float

# Schema for API response

class ResearchProjectUpdateDean(BaseModel):
    api_score_dean: float

class ResearchProjectUpdateVC(BaseModel):
    api_score_vc: float

class ResearchProjectResponse(ResearchProjectBase):
    id: UUID
    faculty_id: UUID
    api_score_faculty: int
    api_score_hod: float
    api_score_vc: float
    api_score_dean: float
    api_score_director: float

    class Config:
        from_attributes = True

# Schema for total score summary
class ResearchProjectSummary(BaseModel):
    total_score: float
