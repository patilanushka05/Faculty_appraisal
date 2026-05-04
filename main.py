from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
import logging
import time
from src.setup.database import engine, Base
from src.setup.dependencies import CurrentUser

# Import all models to ensure they are registered with Base
from src.models.Part_A import (
    TeachingProcess, CourseFile, TeachingMethods, ProjectPartA,
    QualificationEnhancement, StudentFeedback, DepartmentalActivity,
    UniversityActivity, SocialContribution, IndustryConnect, ACR
)
from src.models.Part_B import (
    Faculty, JournalPublication, BookPublication, ICTPedagogy,
    ResearchGuidance, ResearchProject, IPR, ResearchAward,
    ConferencePaper, ResearchProposal, ProductDevelopment,
    SelfDevelopmentFDP, IndustrialTraining, PopularWriting
)
from src.models.overall.remarks import (
    AppraisalRemarks, HODRemarks, DirectorRemarks, DeanRemarks, FinalApproval
)
from src.models.overall.finalization import Enclosure, Declaration
from src.models.overall.school import School
from src.models.overall.appraisal_summary import AppraisalSummary

# Import API routers
from src.api.Part_B.v1 import (
    journal_publication, book_publication, ict_pedagogy,
    research_guidance, research_project, ipr, research_award,
    conference_paper, research_proposal, product_development,
    self_development_fdp, industrial_training, popular_writings
)
from src.api.Part_A.v1 import (
    teaching_process, course_file, teaching_methods,
    student_feedback, departmental_activities, university_activities,
    social_contributions, industry_connect, qualification_enhancement,
    project, acr, part_a_summary
)
from src.api.overall.v1 import appraisal_summary, remarks, finalization, dashboard, faculty

app = FastAPI(
    title="Faculty Appraisal API",
    description="API for managing faculty appraisal data.",
    version="1.0.0",
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Request: {request.method} {request.url.path} processed in {process_time:.4f}s")
    return response

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Database error occurred. This might be due to a schema mismatch or missing data.",
            "error": str(exc.__dict__.get('orig', str(exc)))
        },
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred.",
            "error": str(exc)
        },
    )

origins = [
    "http://localhost:8080",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:5500",
    "http://localhost:4200",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Part B Endpoints
app.include_router(journal_publication.router, prefix="/api/v1/part-b", tags=["Journal Publications"])
app.include_router(book_publication.router, prefix="/api/v1/part-b", tags=["Book Publications"])
app.include_router(ict_pedagogy.router, prefix="/api/v1/part-b", tags=["ICT Pedagogies"])
app.include_router(research_guidance.router, prefix="/api/v1/part-b", tags=["Research Guidance"])
app.include_router(research_project.router, prefix="/api/v1/part-b", tags=["Research Projects"])
app.include_router(ipr.router, prefix="/api/v1/part-b", tags=["IPR Entries"])
app.include_router(research_award.router, prefix="/api/v1/part-b", tags=["Research Awards"])
app.include_router(conference_paper.router, prefix="/api/v1/part-b", tags=["Conference Papers"])
app.include_router(research_proposal.router, prefix="/api/v1/part-b", tags=["Research Proposals"])
app.include_router(product_development.router, prefix="/api/v1/part-b", tags=["Product Developments"])
app.include_router(self_development_fdp.router, prefix="/api/v1/part-b", tags=["Self-Development FDP"])
app.include_router(industrial_training.router, prefix="/api/v1/part-b", tags=["Industrial Trainings"])
app.include_router(popular_writings.router, prefix="/api/v1/part-b", tags=["Popular Writings"])

# Register Part A Endpoints
app.include_router(teaching_process.router, prefix="/api/v1/part-a", tags=["Part A - Teaching Process"])
app.include_router(course_file.router, prefix="/api/v1/part-a", tags=["Part A - Course File"])
app.include_router(teaching_methods.router, prefix="/api/v1/part-a", tags=["Part A - Teaching Methods"])
app.include_router(student_feedback.router, prefix="/api/v1/part-a", tags=["Part A - Student Feedback"])
app.include_router(departmental_activities.router, prefix="/api/v1/part-a", tags=["Part A - Departmental Activities"])
app.include_router(university_activities.router, prefix="/api/v1/part-a", tags=["Part A - University Activities"])
app.include_router(social_contributions.router, prefix="/api/v1/part-a", tags=["Part A - Social Contributions"])
app.include_router(industry_connect.router, prefix="/api/v1/part-a", tags=["Part A - Industry Connect"])
app.include_router(qualification_enhancement.router, prefix="/api/v1/part-a", tags=["Part A - Qualification Enhancement"])
app.include_router(project.router, prefix="/api/v1/part-a", tags=["Part A - Project"])
app.include_router(acr.router, prefix="/api/v1/part-a", tags=["Part A - ACR"])
app.include_router(part_a_summary.router, prefix="/api/v1/part-a", tags=["Part A - Summary"])

# Register Overall Endpoints
app.include_router(appraisal_summary.router, prefix="/api/v1", tags=["Appraisal Summary"])
app.include_router(remarks.router, prefix="/api/v1", tags=["Appraisal Remarks"])
app.include_router(finalization.router, prefix="/api/v1", tags=["Finalization (Enclosures & Declaration)"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard (Higher Authorities)"])
app.include_router(faculty.router, prefix="/api/v1", tags=["Faculty Profile"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Faculty Appraisal API"}

@app.get("/protected")
def protected_route(user: CurrentUser):
    """
    Test endpoint for frontend to verify authentication and role extraction.
    """
    return {
        "message": "Authentication successful",
        "user": {
            "id": user.id,
            "roles": user.roles,
            "department": user.department,
            "school_id": user.school_id,
            "division": user.division
        }
    }
