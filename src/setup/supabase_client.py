import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv(override=True)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def get_supabase(use_service_role: bool = False) -> Client:
    """
    Returns a Supabase client.
    If use_service_role is True, it uses the SERVICE_ROLE_KEY to bypass RLS.
    """
    key = SUPABASE_SERVICE_ROLE_KEY if use_service_role and SUPABASE_SERVICE_ROLE_KEY else SUPABASE_ANON_KEY
    if not SUPABASE_URL or not key:
        raise ValueError("SUPABASE_URL and required keys must be set in .env")
    return create_client(SUPABASE_URL, key)
