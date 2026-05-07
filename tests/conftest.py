import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.setup.database import engine, Base, AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, delete
from src.models.core import FacultyProfile, Declaration, AppraisalSnapshot, AppraisalReview

# Fix for event loop scope in pytest-asyncio
@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture(scope="function")
async def db():
    async with AsyncSessionLocal() as session:
        yield session
        # Cleanup is handled by specific test teardowns or global reset if safe

@pytest.fixture(scope="function", autouse=True)
async def cleanup_db():
    """
    Cleans up test data after each test.
    We identify test data by the '@test.com' domain.
    """
    yield
    async with AsyncSessionLocal() as db:
        # Delete test declarations
        await db.execute(delete(Declaration).where(Declaration.faculty_email.like("%@test.com")))
        # Delete test snapshots
        await db.execute(delete(AppraisalSnapshot).where(AppraisalSnapshot.faculty_email.like("%@test.com")))
        # Delete test reviews
        await db.execute(delete(AppraisalReview).where(AppraisalReview.faculty_email.like("%@test.com")))
        # Delete test profiles
        await db.execute(delete(FacultyProfile).where(FacultyProfile.email.like("%@test.com")))
        
        await db.commit()
