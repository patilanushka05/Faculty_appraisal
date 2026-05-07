from sqlalchemy import Column, Integer, String, ForeignKey, Text, Enum, Double, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from src.setup.database import Base

class ConferencePaper(Base):
    __tablename__ = "academic_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculty.id"))
    event_title = Column(Text, name="title", nullable=False)
    event_date = Column(Date, nullable=False)
    activity_type = Column(String(50), name="type", nullable=False) # Lecture / Resource Person / Paper / Proceedings
    hosting_organization = Column(String(255), name="organization", nullable=False)
    event_level = Column(String(50), name="level", nullable=False) # International / National
    api_score_faculty = Column(Double, name="research_score_faculty", default=0.0)
    api_score_hod = Column(Double, name="research_score_hod", default=0.0)
    api_score_director = Column(Double, name="research_score_director", default=0.0)
    api_score_dean = Column(Double, name="dean_score", default=0.0)
    api_score_vc = Column(Double, name="vc_score", default=0.0)
    department = Column(String, nullable=True)
    document = Column(String, nullable=True)

    faculty = relationship("Faculty", back_populates="conference_papers")
