from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

# Base schema for common attributes
class ResearchProposalBase(BaseModel):
    proposal_title: str = Field(..., max_length=500)
    duration: str = Field(..., max_length=50)
    funding_agency: str = Field(..., max_length=255)
    grant_amount: float
    department: Optional[str] = Field(None, description="Department of the faculty") # Added as per user request
    document: Optional[str] = Field(None, description="Google Drive link to the document") # Added as per user request

# Schema for creating a new Research Proposal entry (Faculty input)
class ResearchProposalCreate(ResearchProposalBase):
    pass

# Schema for faculty to update their own Research Proposal entry
class ResearchProposalUpdateFaculty(ResearchProposalBase):
    proposal_title: Optional[str] = Field(None, max_length=500)
    duration: Optional[str] = Field(None, max_length=50)
    funding_agency: Optional[str] = Field(None, max_length=255)
    grant_amount: Optional[float] = None

# Schema for HOD to update API score
class ResearchProposalUpdateHOD(BaseModel):
    api_score_hod: float

# Schema for Director to update API score
class ResearchProposalUpdateDirector(BaseModel):
    api_score_director: float

# Schema for API response

class ResearchProposalUpdateDean(BaseModel):
    api_score_dean: float

class ResearchProposalUpdateVC(BaseModel):
    api_score_vc: float

class ResearchProposalResponse(ResearchProposalBase):
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
class ResearchProposalSummary(BaseModel):
    total_score: float
