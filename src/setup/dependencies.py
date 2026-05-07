from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status, Header
from .database import get_db
from typing import List, Optional, Annotated
import os
from supabase import create_async_client, AsyncClient
from dotenv import load_dotenv

load_dotenv(override=True)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

class User:
    def __init__(self, id: str, email: str, roles: List[str], department: Optional[str] = None, school: Optional[str] = None, division: Optional[str] = None):
        self.id = id
        self.email = email
        self.roles = [r.lower() for r in roles]
        self.department = department
        self.school = school
        self.division = division

    def has_authority_over(self, subordinate_id: str, subordinate_role: str, subordinate_dept: Optional[str] = None, subordinate_school: Optional[str] = None, subordinate_division: Optional[str] = None) -> bool:
        """
        Implements Hierarchical Access Control:
        1. VC: All schools.
        2. Dean: All schools within their division (Engineering/Non-Engineering).
        3. Director: All departments within their school.
        4. HOD: Only their specific department (Horizontal Isolation).
        """
        role_weights = {
            "faculty": 0,
            "non_teaching_staff": 0,
            "staff": 0,
            "hod": 1,
            "reporting_officer": 1.5,
            "section_head": 2,
            "director": 2,
            "center_head": 2.5,
            "dean": 3,
            "registrar": 3.5,
            "vc": 4,
            "admin": 5
        }
        
        if "admin" in self.roles:
            return True

        user_weight = max([role_weights.get(r, 0) for r in self.roles])
        sub_weight = role_weights.get(subordinate_role.lower(), 0)

        # Self-access
        if str(self.id) == str(subordinate_id) or self.email == subordinate_id:
            return True

        # Hierarchy check
        if user_weight > sub_weight:
            # VC or Registrar Access (University-wide for their respective domains)
            if "vc" in self.roles or "registrar" in self.roles:
                return True
            
            # Center Head Access (Specifically for CISR)
            if "center_head" in self.roles:
                return self.division == "CISR" and subordinate_division == "CISR"
            
            # Dean Access (Division Isolation)
            if "dean" in self.roles:
                return self.division == subordinate_division
            
            # Director, Section Head, or Reporting Officer Access (School/Unit Isolation)
            if any(r in self.roles for r in ["director", "section_head", "reporting_officer"]):
                return self.school == subordinate_school
            
            # HOD Access (Departmental/Horizontal Isolation)
            if "hod" in self.roles:
                # Must be in the same school AND same department
                return self.school == subordinate_school and self.department == subordinate_dept
                
        return False

async def get_current_user(authorization: Annotated[Optional[str], Header()] = None) -> User:
    """
    Verifies the JWT from the frontend and returns user data + role.
    If no authorization header is provided, returns a mock user ONLY if ALLOW_MOCK_USER is true.
    """
    if not authorization:
        if os.getenv("ALLOW_MOCK_USER", "false").lower() == "true":
            # Mock user for development/testing
            return User(
                id="00000000-0000-0000-0000-000000000001", 
                email="admin@example.com",
                roles=["admin", "faculty"], 
                department="Computer Science",
                school="SoCSEA",
                division="Engineering"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing. Please log in.",
            )
    
    try:
        token = authorization.split(" ")[1]
        
        # Check if we should use local auth or fallback to Supabase
        if os.getenv("USE_LOCAL_AUTH", "false").lower() == "true":
            from .local_auth import decode_access_token
            payload = decode_access_token(token)
            
            role = payload.get("appraisal_role") or payload.get("role", "faculty")
            dept = payload.get("department")
            school = payload.get("school")
            division = payload.get("division")
            email = payload.get("email")
            
            roles = [role] if isinstance(role, str) else role
            
            return User(
                id=payload.get("sub"), # JWT standard subject claim is 'sub'
                email=email,
                roles=roles, 
                department=dept, 
                school=school, 
                division=division
            )
        else:
            # Fallback to Supabase Auth
            async with create_async_client(SUPABASE_URL, SUPABASE_ANON_KEY) as supabase:
                user_response = await supabase.auth.get_user(token)
                user = user_response.user
                
                # Check both app_metadata and user_metadata for the role
                role = user.app_metadata.get("appraisal_role") or user.app_metadata.get("role") or \
                       user.user_metadata.get("appraisal_role") or user.user_metadata.get("role") or "faculty"
                dept = user.user_metadata.get("department") or user.app_metadata.get("department")
                school = user.user_metadata.get("school") or user.app_metadata.get("school")
                division = user.user_metadata.get("division") or user.app_metadata.get("division")
                
                roles = [role] if isinstance(role, str) else role
                
                return User(
                    id=user.id, 
                    email=user.email,
                    roles=roles, 
                    department=dept, 
                    school=school, 
                    division=division
                )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}",
        )


CurrentUser = Annotated[User, Depends(get_current_user)]
