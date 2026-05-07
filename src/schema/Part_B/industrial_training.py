from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

# Base schema for common attributes
class IndustrialTrainingBase(BaseModel):
    company_industry: str = Field(..., max_length=255)
    duration_days: int
    nature_of_training: str = Field(..., max_length=500)
    department: Optional[str] = Field(None, description="Department of the faculty") # Added as per user request
    document: Optional[str] = Field(None, description="Google Drive link to the document") # Added as per user request

# Schema for creating a new Industrial Training entry (Faculty input)
class IndustrialTrainingCreate(IndustrialTrainingBase):
    pass

# Schema for faculty to update their own Industrial Training entry
class IndustrialTrainingUpdateFaculty(IndustrialTrainingBase):
    company_industry: Optional[str] = Field(None, max_length=255)
    duration_days: Optional[int] = None
    nature_of_training: Optional[str] = Field(None, max_length=500)

# Schema for HOD to update API score
class IndustrialTrainingUpdateHOD(BaseModel):
    api_score_hod: float

# Schema for Director to update API score
class IndustrialTrainingUpdateDirector(BaseModel):
    api_score_director: float

# Schema for API response

class IndustrialTrainingUpdateDean(BaseModel):
    api_score_dean: float

class IndustrialTrainingUpdateVC(BaseModel):
    api_score_vc: float

class IndustrialTrainingResponse(IndustrialTrainingBase):
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
class IndustrialTrainingSummary(BaseModel):
    total_score: float
