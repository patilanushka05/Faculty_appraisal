import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from src.setup.dependencies import User
from unittest.mock import patch

BASE_URL = "http://testserver"

# MOCK DATA FOR HIERARCHY TESTING
SCHOOL_CS_ID = "00000000-0000-0000-0000-000000000001" # Engineering
SCHOOL_MEDIA_ID = "00000000-0000-0000-0000-000000000004" # Non-Engineering

FACULTY_CS_ID = "10000000-0000-0000-0000-000000000001"
FACULTY_MEDIA_ID = "40000000-0000-0000-0000-000000000001"

from src.setup.dependencies import get_current_user

@pytest.mark.asyncio
async def test_vc_global_access():
    """VC should be able to see data from any school"""
    vc_user = User(id="vc_id", roles=["vc"])
    async def get_vc(): return vc_user
    app.dependency_overrides[get_current_user] = get_vc
    
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:
            response = await ac.get(f"/api/v1/part-a/part-a-summary/{FACULTY_CS_ID}")
            assert response.status_code == 200
            
            response = await ac.get(f"/api/v1/part-a/part-a-summary/{FACULTY_MEDIA_ID}")
            assert response.status_code == 200
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_dean_divisional_isolation():
    """Dean of Engineering should NOT see Media (Non-Engineering) data"""
    eng_dean = User(id="dean_eng_id", roles=["dean"], division="Engineering")
    
    # Direct method test
    assert eng_dean.has_authority_over(FACULTY_CS_ID, "faculty", subordinate_division="Engineering") is True
    assert eng_dean.has_authority_over(FACULTY_MEDIA_ID, "faculty", subordinate_division="Non-Engineering") is False

@pytest.mark.asyncio
async def test_hod_horizontal_isolation():
    """HOD of CS should NOT see data from HOD of Mech even in same school"""
    hod_cs = User(id="hod_cs_id", roles=["hod"], department="Computer Science", school_id=SCHOOL_CS_ID)
    
    # Same school, different department
    assert hod_cs.has_authority_over("fac_mech_id", "faculty", subordinate_dept="Mechanical", subordinate_school_id=SCHOOL_CS_ID) is False
    
    # Same school, same department
    assert hod_cs.has_authority_over(FACULTY_CS_ID, "faculty", subordinate_dept="Computer Science", subordinate_school_id=SCHOOL_CS_ID) is True

@pytest.mark.asyncio
async def test_dashboard_filtering():
    """Dashboard should only return subordinates based on hierarchy"""
    director_cs = User(id="dir_cs_id", roles=["director"], school_id=SCHOOL_CS_ID)
    async def get_director(): return director_cs
    app.dependency_overrides[get_current_user] = get_director
    
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:
            response = await ac.get("/api/v1/dashboard/subordinates")
            assert response.status_code == 200
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_faculty_isolation():
    """Faculty should NOT be able to see other faculty's data"""
    fac1 = User(id=FACULTY_CS_ID, roles=["faculty"])
    async def get_fac1(): return fac1
    app.dependency_overrides[get_current_user] = get_fac1
    
    try:
        fac2_id = "20000000-0000-0000-0000-000000000002"
        async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:
            response = await ac.get(f"/api/v1/part-a/part-a-summary/{fac2_id}")
            assert response.status_code == 403
    finally:
        app.dependency_overrides.clear()
