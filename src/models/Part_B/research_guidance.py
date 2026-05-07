from sqlalchemy import Column, Integer, String, ForeignKey, Text, Enum, Double, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from src.setup.database import Base

class ResearchGuidance(Base):
    __tablename__ = "research_guidance"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculty.id"))
    degree = Column(String(20), nullable=False) # ME / PhD
    student_name = Column(String(255), nullable=False)
    submission_status = Column(String, name="thesis_status", nullable=False) # e.g., "Submitted", "Awarded"
    award_date = Column(Date, name="thesis_date", nullable=True) # Date of award, if applicable
    api_score_faculty = Column(Double, default=0.0)
    api_score_hod = Column(Double, default=0.0)
    api_score_dean = Column(Double, default=0.0)
    api_score_vc = Column(Double, default=0.0)
    api_score_director = Column(Double, default=0.0)
    department = Column(String, nullable=True)
    document = Column(String, nullable=True)

    faculty = relationship("Faculty", back_populates="research_guidance_entries")
