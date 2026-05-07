from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from uuid import UUID

# Base schema for common attributes
class IPRBase(BaseModel):
    title: str = Field(..., max_length=500)
    scope: str = Field(..., max_length=20) # National / International
    filing_date: date
    status: str = Field(..., max_length=50) # Published / Granted
    patent_file_no: str = Field(..., max_length=100)
    department: Optional[str] = Field(None, description="Department of the faculty") # Added as per user request
    document: Optional[str] = Field(None, description="Google Drive link to the document") # Added as per user request

# Schema for creating a new IPR entry (Faculty input)
class IPRCreate(IPRBase):
    pass

# Schema for faculty to update their own IPR entry
class IPRUpdateFaculty(IPRBase):
    title: Optional[str] = Field(None, max_length=500)
    scope: Optional[str] = Field(None, max_length=20)
    filing_date: Optional[date] = None
    status: Optional[str] = Field(None, max_length=50)
    patent_file_no: Optional[str] = Field(None, max_length=100)

# Schema for HOD to update API score
class IPRUpdateHOD(BaseModel):
    api_score_hod: float

# Schema for Director to update API score
class IPRUpdateDirector(BaseModel):
    api_score_director: float

class IPRUpdateDean(BaseModel):
    api_score_dean: float

class IPRUpdateVC(BaseModel):
    api_score_vc: float

# Schema for API response
class IPRResponse(IPRBase):
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
class IPRSummary(BaseModel):
    total_score: float
