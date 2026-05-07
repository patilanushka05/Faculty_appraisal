import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from src.setup.dependencies import get_current_user
import os
from unittest.mock import patch
from uuid import uuid4

BASE_URL = "http://testserver"

from src.setup.database import AsyncSessionLocal
from sqlalchemy import update
from src.models.Part_B.faculty import Faculty

@pytest.mark.asyncio
async def test_local_server_full_workflow():
    # 1. Force Local Auth Mode via Environment Mocking
    with patch.dict(os.environ, {"USE_LOCAL_AUTH": "true", "JWT_SECRET_KEY": "test-secret-key-123", "ALLOW_MOCK_USER": "false"}):
        with patch("src.setup.local_auth.get_password_hash", side_effect=lambda x: x + "_hash"):
            with patch("src.setup.local_auth.verify_password", side_effect=lambda p, h: h == p + "_hash"):
                async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as client:
                    
                    # 2. Register a new user locally
                    unique_email = f"test_{uuid4().hex[:8]}@example.com"
                    register_data = {
                        "email": unique_email,
                        "password": "securepassword123",
                        "name": "Local Test User",
                        "department": "IT Section",
                        "role": "staff"
                    }
                    
                    reg_response = await client.post("/api/v1/auth/register", json=register_data)
                    assert reg_response.status_code == 201
                    
                    # 2.5 Manually verify the user in DB
                    async with AsyncSessionLocal() as db:
                        await db.execute(update(Faculty).where(Faculty.email == unique_email).values(is_verified=True))
                        await db.commit()

                    # 3. Test Login
                    login_data = {
                        "username": unique_email,
                        "password": "securepassword123"
                    }
                    login_response = await client.post("/api/v1/auth/login", data=login_data)
                    assert login_response.status_code == 200
                    token = login_response.json()["access_token"]
                    
                    headers = {"Authorization": f"Bearer {token}"}

                    # 4. Verify Session Management (/auth/session)
                    session_response = await client.get("/api/v1/auth/session", headers=headers)
                    assert session_response.status_code == 200
                    session_data = session_response.json()
                    assert session_data["department"] == "IT Section"

                    # 5. Verify Database Isolation (Profile Access)
                    profile_response = await client.get("/api/v1/profile", headers=headers)
                    assert profile_response.status_code == 200
                    assert profile_response.json()["name"] == "Local Test User"

                    # 6. Verify Session Isolation (Missing Token)
                    no_auth_response = await client.get("/api/v1/auth/session")
                    assert no_auth_response.status_code == 401

@pytest.mark.asyncio
async def test_dual_tab_isolation_simulation():
    """Simulates 2 different users to ensure the backend treats them as isolated sessions."""
    with patch.dict(os.environ, {"USE_LOCAL_AUTH": "true", "JWT_SECRET_KEY": "test-secret-key-123", "ALLOW_MOCK_USER": "false"}):
        with patch("src.setup.local_auth.get_password_hash", side_effect=lambda x: x + "_hash"):
            with patch("src.setup.local_auth.verify_password", side_effect=lambda p, h: h == p + "_hash"):
                async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as client:
                    
                    # Create User 1
                    u1_email = f"user1_{uuid4().hex[:8]}@test.com"
                    await client.post("/api/v1/auth/register", json={"email": u1_email, "password": "pw1", "name": "User One", "department": "A"})
                    
                    async with AsyncSessionLocal() as db:
                        await db.execute(update(Faculty).where(Faculty.email == u1_email).values(is_verified=True))
                        await db.commit()

                    res1 = await client.post("/api/v1/auth/login", data={"username": u1_email, "password": "pw1"})
                    t1 = res1.json()["access_token"]

                    # Create User 2
                    u2_email = f"user2_{uuid4().hex[:8]}@test.com"
                    await client.post("/api/v1/auth/register", json={"email": u2_email, "password": "pw2", "name": "User Two", "department": "B"})
                    
                    async with AsyncSessionLocal() as db:
                        await db.execute(update(Faculty).where(Faculty.email == u2_email).values(is_verified=True))
                        await db.commit()

                    res2 = await client.post("/api/v1/auth/login", data={"username": u2_email, "password": "pw2"})
                    t2 = res2.json()["access_token"]

                    # Request with User 1 token
                    resp1 = await client.get("/api/v1/auth/session", headers={"Authorization": f"Bearer {t1}"})
                    # Request with User 2 token
                    resp2 = await client.get("/api/v1/auth/session", headers={"Authorization": f"Bearer {t2}"})

                    # Assert isolation
                    assert resp1.json()["id"] != resp2.json()["id"]
                    assert resp1.json()["department"] == "A"
                    assert resp2.json()["department"] == "B"
