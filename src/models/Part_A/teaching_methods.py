from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Double
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from ...setup.database import Base

class TeachingMethods(Base):
    __tablename__ = "innovative_teaching_methods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculty.id"))
    sr_no = Column(Integer, nullable=True)
    short_description = Column(String(255), nullable=False)
    details_proof = Column(Boolean, name="details", default=False)
    api_score_faculty = Column(Double, default=0.0)
    api_score_hod = Column(Double, default=0.0)
    api_score_director = Column(Double, default=0.0)
    api_score_dean = Column(Double, default=0.0)
    api_score_vc = Column(Double, default=0.0)
    signature = Column(Boolean, default=False)
    department = Column(String, nullable=True)
    document = Column(String, nullable=True)

    faculty = relationship("Faculty", back_populates="teaching_methods")
