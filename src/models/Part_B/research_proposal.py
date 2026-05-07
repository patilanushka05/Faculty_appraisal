from sqlalchemy import Column, Integer, String, ForeignKey, Text, Double
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from src.setup.database import Base

class ResearchProposal(Base):
    __tablename__ = "research_proposals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculty.id"))
    proposal_title = Column(Text, name="title", nullable=False)
    duration = Column(String(50), nullable=False) # Project duration (e.g., "6 months", "1 year")
    funding_agency = Column(String(255), nullable=False)
    grant_amount = Column(Double, nullable=False)
    api_score_faculty = Column(Double, default=0.0)
    api_score_hod = Column(Double, default=0.0)
    api_score_dean = Column(Double, default=0.0)
    api_score_vc = Column(Double, default=0.0)
    api_score_director = Column(Double, default=0.0)
    department = Column(String, nullable=True)
    document = Column(String, nullable=True)

    faculty = relationship("Faculty", back_populates="research_proposals")
