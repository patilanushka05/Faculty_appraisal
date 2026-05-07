from sqlalchemy import Column, Integer, String, ForeignKey, Text, Enum, Double
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from src.setup.database import Base

class ICTPedagogy(Base):
    __tablename__ = "ict_teaching_content"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculty.id"))
    title = Column(String(255), name="title_of_development", nullable=False)
    description = Column(Text, name="short_description", nullable=False)
    pedagogy_type = Column(String(100), name="type", nullable=False) # ENUM / String
    quadrants = Column(Integer, name="no_of_quadrants", nullable=False)
    api_score_faculty = Column(Double, default=0.0)
    api_score_hod = Column(Double, default=0.0)
    api_score_dean = Column(Double, default=0.0)
    api_score_vc = Column(Double, default=0.0)
    api_score_director = Column(Double, default=0.0)
    department = Column(String, nullable=True)
    document = Column(String, nullable=True)

    faculty = relationship("Faculty", back_populates="ict_pedagogies")
