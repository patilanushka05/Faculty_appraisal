import pytest
from httpx import AsyncClient

@pytest.fixture
async def reviewer_headers(client: AsyncClient):
    # Register an HOD
    email = "hod@test.com"
    await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "password",
        "full_name": "Test HOD",
        "appraisal_role": "hod",
        "school": "SoCSEA",
        "department": "Computer Science"
    })
    login_res = await client.post("/api/v1/auth/login", json={"email": email, "password": "password"})
    return {"Authorization": f"Bearer {login_res.json()['token']}"}

@pytest.fixture
async def faculty_user(client: AsyncClient):
    email = "faculty_sub@test.com"
    await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "password",
        "full_name": "Subordinate Faculty",
        "appraisal_role": "faculty",
        "school": "SoCSEA",
        "department": "Computer Science"
    })
    return email

@pytest.mark.asyncio
async def test_hod_dashboard_visibility(client: AsyncClient, reviewer_headers: dict, faculty_user: str):
    academic_year = "2025-26"
    
    # Faculty submits form
    login_res = await client.post("/api/v1/auth/login", json={"email": faculty_user, "password": "password"})
    faculty_headers = {"Authorization": f"Bearer {login_res.json()['token']}"}
    
    await client.post("/api/v1/appraisal/submit", json={
        "academic_year": academic_year,
        "form": {},
        "totals": {"grandTotal": 50}
    }, headers=faculty_headers)

    # HOD checks subordinates
    response = await client.get(f"/api/v1/dashboard/subordinates?academic_year={academic_year}", headers=reviewer_headers)
    assert response.status_code == 200
    subs = response.json()
    
    # HOD should see the faculty in their department
    assert any(s["email"] == faculty_user for s in subs)

@pytest.mark.asyncio
async def test_authority_review_workflow(client: AsyncClient, reviewer_headers: dict, faculty_user: str):
    academic_year = "2025-26"
    
    # HOD submits review for faculty
    review_data = {
        "academic_year": academic_year,
        "remarks": "Excellent work",
        "part_a_score": 45,
        "part_b_score": 40,
        "total_score": 85
    }
    
    response = await client.put(f"/api/v1/appraisal-remarks/hod/{faculty_user}", json=review_data, headers=reviewer_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "pending_director"

    # Verify status changed for faculty
    login_res = await client.post("/api/v1/auth/login", json={"email": faculty_user, "password": "password"})
    faculty_headers = {"Authorization": f"Bearer {login_res.json()['token']}"}
    
    status_res = await client.get(f"/api/v1/appraisal/status?academic_year={academic_year}", headers=faculty_headers)
    assert status_res.json()["declaration"]["status"] == "pending_director"
