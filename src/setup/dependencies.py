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
    def __init__(self, id: str, email: str, roles: List[str], department: Optional[str] = None, school: Optional[str] = None):
        self.id = id
        self.email = email
        self.roles = [r.lower() for r in roles]
        self.department = department
        self.school = school

    def has_authority_over(self, subordinate_id: str, subordinate_role: str, subordinate_dept: Optional[str] = None, subordinate_school: Optional[str] = None) -> bool:
        """
        Implements Hierarchical Access Control:
        1. VC: All schools.
        2. Dean: All departments within their domain.
        3. Director: All departments within their school.
        4. HOD: Only their specific department.
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
            if "vc" in self.roles or "registrar" in self.roles:
                return True
            
            if "dean" in self.roles:
                return True

            if any(r in self.roles for r in ["director", "section_head", "reporting_officer", "center_head"]):
                return self.school == subordinate_school
            
            if "hod" in self.roles:
                return self.school == subordinate_school and self.department == subordinate_dept
                
        return False

def get_form_family(school: str) -> str:
    """
    Maps a school code to a form family (standard, media, design).
    """
    if not school:
        return "standard"
        
    s = school.strip()
    school_map = {
        "SoCSEA": "standard", "SoBB": "standard", "SoCE": "standard", 
        "SoEMR": "standard", "SoC": "standard", "CISR": "standard",
        "SoMCS": "media",
        "CioD": "design", "SoAA": "design"
    }
    return school_map.get(s, "standard")

async def get_current_user(authorization: Annotated[Optional[str], Header()] = None) -> User:
    """
    Verifies the JWT from the frontend and returns user data + role.
    """
    if not authorization:
        if os.getenv("ALLOW_MOCK_USER", "false").lower() == "true":
            return User(
                id="00000000-0000-0000-0000-000000000001", 
                email="admin@example.com",
                roles=["admin", "faculty"], 
                department="Computer Science",
                school="SoCSEA"
            )
        else:
            raise HTTPException(status_code=401, detail="Authorization header missing.")
    
    try:
        token = authorization.split(" ")[1]
        
        if os.getenv("USE_LOCAL_AUTH", "false").lower() == "true":
            from .local_auth import decode_access_token
            payload = decode_access_token(token)
            
            role = payload.get("appraisal_role") or payload.get("role", "faculty")
            dept = payload.get("department")
            school = payload.get("school")
            email = payload.get("email")
            
            roles = [role] if isinstance(role, str) else role
            
            return User(
                id=payload.get("sub"), 
                email=email,
                roles=roles, 
                department=dept, 
                school=school
            )
        else:
            async with create_async_client(SUPABASE_URL, SUPABASE_ANON_KEY) as supabase:
                user_response = await supabase.auth.get_user(token)
                user = user_response.user
                
                role = user.app_metadata.get("appraisal_role") or user.app_metadata.get("role") or \
                       user.user_metadata.get("appraisal_role") or user.user_metadata.get("role") or "faculty"
                dept = user.user_metadata.get("department")
                school = user.user_metadata.get("school")
                
                roles = [role] if isinstance(role, str) else role
                
                return User(
                    id=user.id, 
                    email=user.email,
                    roles=roles, 
                    department=dept, 
                    school=school
                )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


CurrentUser = Annotated[User, Depends(get_current_user)]
