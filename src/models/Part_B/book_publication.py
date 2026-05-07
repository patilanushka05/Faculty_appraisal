from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Double
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from src.setup.database import Base

class BookPublication(Base):
    __tablename__ = "book_publications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("faculty.id"))
    title_and_pages = Column(String, name="title", index=True)
    book_title_editor = Column(String, name="book")
    issn_isbn = Column(String, name="issn")
    publisher_type = Column(String, name="publisher")
    co_authors_count = Column(Integer, name="coauthor")
    is_first_author = Column(Boolean, name="first_author", default=False)
    department = Column(String, nullable=True) 
    document = Column(String, nullable=True) 

    api_score_faculty = Column(Double, name="score", default=0.0)
    api_score_hod = Column(Double, name="hod_score", default=0.0)
    api_score_director = Column(Double, name="director_score", default=0.0)
    api_score_dean = Column(Double, name="dean_score", default=0.0)
    api_score_vc = Column(Double, name="vc_score", default=0.0)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), server_default=func.now())

    faculty = relationship("Faculty", back_populates="book_publications")