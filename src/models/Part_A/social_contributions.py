from sqlalchemy import Column, Integer, String, Text, ForeignKey, Double
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from ...setup.database import Base

class SocialContribution(Base):
    __tablename__ = "contribution_to_society"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculty.id"))
    sr_no = Column(Integer, nullable=True)
    activity_type = Column(String(255), name="activity", nullable=False)
    details_of_activity = Column(Text, nullable=False)
    api_score_faculty = Column(Double, default=0.0)
    api_score_hod = Column(Double, default=0.0)
    api_score_director = Column(Double, default=0.0)
    api_score_dean = Column(Double, default=0.0)
    api_score_vc = Column(Double, default=0.0)
    department = Column(String, nullable=True)
    document = Column(String, nullable=True)

    faculty = relationship("Faculty", back_populates="social_contributions")
