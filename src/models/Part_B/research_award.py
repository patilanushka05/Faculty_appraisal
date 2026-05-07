from sqlalchemy import Column, Integer, String, ForeignKey, Text, Enum, Double, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from src.setup.database import Base

class ResearchAward(Base):
    __tablename__ = "research_awards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculty.id"))
    award_name = Column(Text, name="title", nullable=False)
    award_date = Column(Date, name="date_of_award", nullable=False)
    awarding_agency = Column(String(255), nullable=False)
    level = Column(String(50), nullable=False) # International / National
    api_score_faculty = Column(Double, name="research_score_faculty", default=0.0)
    api_score_hod = Column(Double, name="research_score_hod", default=0.0)
    api_score_director = Column(Double, name="research_score_director", default=0.0)
    api_score_dean = Column(Double, name="dean_score", default=0.0)
    api_score_vc = Column(Double, name="vc_score", default=0.0)
    department = Column(String, nullable=True)
    document = Column(String, nullable=True)

    faculty = relationship("Faculty", back_populates="research_awards")
