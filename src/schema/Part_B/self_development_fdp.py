from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

# Base schema for common attributes
class SelfDevelopmentFDPBase(BaseModel):
    program_name: str = Field(..., max_length=255)
    duration_days: int
    organizer: str = Field(..., max_length=255)
    department: Optional[str] = Field(None, description="Department of the faculty") # Added as per user request
    document: Optional[str] = Field(None, description="Google Drive link to the document") # Added as per user request

# Schema for creating a new Self Development FDP entry (Faculty input)
class SelfDevelopmentFDPCreate(SelfDevelopmentFDPBase):
    pass

# Schema for faculty to update their own Self Development FDP entry
class SelfDevelopmentFDPUpdateFaculty(SelfDevelopmentFDPBase):
    program_name: Optional[str] = Field(None, max_length=255)
    duration_days: Optional[int] = None
    organizer: Optional[str] = Field(None, max_length=255)

# Schema for HOD to update API score
class SelfDevelopmentFDPUpdateHOD(BaseModel):
    api_score_hod: float

# Schema for Director to update API score
class SelfDevelopmentFDPUpdateDirector(BaseModel):
    api_score_director: float

# Schema for API response
class SelfDevelopmentFDPResponse(SelfDevelopmentFDPBase):
    id: UUID
    faculty_id: UUID
    api_score_faculty: int
    api_score_hod: float
    api_score_director: float

    class Config:
        from_attributes = True

# Schema for total score summary
class SelfDevelopmentFDPSummary(BaseModel):
    total_score: float

class SelfDevelopmentFDPUpdateDean(BaseModel):
    api_score_dean: float

class SelfDevelopmentFDPUpdateVC(BaseModel):
    api_score_vc: float
