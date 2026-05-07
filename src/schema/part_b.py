from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional
from datetime import datetime, date

class BasePartBSchema(BaseModel):
    faculty_email: str
    academic_year: str
    form_family: Optional[str] = None
    section_title: Optional[str] = None
    max_marks: Optional[float] = None
    row_no: Optional[int] = None
    score: float = 0
    hod_score: Optional[float] = None
    director_score: Optional[float] = None
    dean_score: Optional[float] = None
    vc_score: Optional[float] = None

class JournalPublicationBase(BasePartBSchema):
    title: Optional[str] = None
    journal: Optional[str] = None
    issn: Optional[str] = None
    indexing: Optional[str] = None

class JournalPublicationResponse(JournalPublicationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PopularWritingBase(BasePartBSchema):
    media: Optional[str] = None
    film: Optional[str] = None

class PopularWritingResponse(PopularWritingBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class BookPublicationBase(BasePartBSchema):
    title: Optional[str] = None
    book: Optional[str] = None
    issn: Optional[str] = None
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    coauthor: Optional[str] = None
    first_author: Optional[str] = None

class BookPublicationResponse(BookPublicationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ICTPedagogyBase(BasePartBSchema):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    quadrant: Optional[str] = None

class ICTPedagogyResponse(ICTPedagogyBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ResearchGuidanceBase(BasePartBSchema):
    degree: Optional[str] = None
    student_name: Optional[str] = None
    thesis: Optional[str] = None

class ResearchGuidanceResponse(ResearchGuidanceBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ResearchProjectBase(BasePartBSchema):
    title: Optional[str] = None
    agency: Optional[str] = None
    sanction_date: Optional[date] = None
    amount: Optional[float] = None
    role: Optional[str] = None
    project_status: Optional[str] = None

class ResearchProjectResponse(ResearchProjectBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ExternalResearchProjectBase(BasePartBSchema):
    title: Optional[str] = None
    agency: Optional[str] = None
    sanction_date: Optional[date] = None
    amount: Optional[float] = None
    role: Optional[str] = None
    project_status: Optional[str] = None

class ExternalResearchProjectResponse(ExternalResearchProjectBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class IPRRecordBase(BasePartBSchema):
    title: Optional[str] = None
    scope: Optional[str] = None
    ipr_date: Optional[date] = None
    ipr_status: Optional[str] = None
    file_no: Optional[str] = None

class IPRRecordResponse(IPRRecordBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PatentBase(BasePartBSchema):
    title: Optional[str] = None
    type: Optional[str] = None
    patent_date: Optional[date] = None
    patent_status: Optional[str] = None
    file_no: Optional[str] = None

class PatentResponse(PatentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AwardBase(BasePartBSchema):
    title: Optional[str] = None
    award_date: Optional[date] = None
    agency: Optional[str] = None
    level: Optional[str] = None

class AwardResponse(AwardBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ConferenceBase(BasePartBSchema):
    title: Optional[str] = None
    type: Optional[str] = None
    organization: Optional[str] = None
    level: Optional[str] = None

class ConferenceResponse(ConferenceBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ResearchProposalBase(BasePartBSchema):
    title: Optional[str] = None
    duration: Optional[str] = None
    agency: Optional[str] = None
    amount: Optional[float] = None

class ResearchProposalResponse(ResearchProposalBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ProductDevelopedBase(BasePartBSchema):
    details: Optional[str] = None
    usage: Optional[str] = None

class ProductDevelopedResponse(ProductDevelopedBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class SelfDevelopmentBase(BasePartBSchema):
    program: Optional[str] = None
    duration: Optional[str] = None
    organization: Optional[str] = None

class SelfDevelopmentResponse(SelfDevelopmentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class IndustrialTrainingBase(BasePartBSchema):
    company: Optional[str] = None
    duration: Optional[str] = None
    nature: Optional[str] = None

class IndustrialTrainingResponse(IndustrialTrainingBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
