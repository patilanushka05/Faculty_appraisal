import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    # 1. Register a new user
    register_data = {
        "email": "test_faculty@test.com",
        "password": "testpassword123",
        "full_name": "Test Faculty",
        "appraisal_role": "faculty",
        "school": "SoCSEA",
        "department": "Computer Science",
        "designation": "Assistant Professor",
        "employee_id": "TEST001",
        "phone": "1234567890",
        "qualification": "PhD",
        "teaching_experience": "5 years"
    }
    
    response = await client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["email"] == "test_faculty@test.com"
    assert res_json["full_name"] == "Test Faculty"
    assert res_json["form_family"] == "standard" # Auto-assigned based on school

    # 2. Login with the new user
    login_data = {
        "email": "test_faculty@test.com",
        "password": "testpassword123"
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    login_res = response.json()
    assert "token" in login_res
    assert login_res["profile"]["email"] == "test_faculty@test.com"
    
    token = login_res["token"]

    # 3. Get Me
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    me_res = response.json()
    assert me_res["email"] == "test_faculty@test.com"
    assert me_res["appraisal_role"] == "faculty"

@pytest.mark.asyncio
async def test_update_profile(client: AsyncClient):
    # Setup: Register
    register_data = {
        "email": "update_test@test.com",
        "password": "password",
        "full_name": "Before Update",
        "appraisal_role": "faculty",
        "school": "SoCSEA"
    }
    await client.post("/api/v1/auth/register", json=register_data)
    
    # Login to get token
    login_res = await client.post("/api/v1/auth/login", json={"email": "update_test@test.com", "password": "password"})
    token = login_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Update
    update_data = {
        "full_name": "After Update",
        "phone": "9999999999"
    }
    response = await client.put("/api/v1/auth/me", json=update_data, headers=headers)
    assert response.status_code == 200
    updated_res = response.json()
    assert updated_res["full_name"] == "After Update"
    assert updated_res["phone"] == "9999999999"
