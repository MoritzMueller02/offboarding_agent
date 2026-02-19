"""
Shared dependencies for dependency injection.
These are used across multiple routers.
"""

from functools import lru_cache
from typing import Annotated
from supabase import create_client, Client
from config import get_settings

# Get settings
try:
    from config import get_settings
    settings = get_settings()
    print("Import erfolgreich")
except ImportError as e:
    print("{e}")
    

# Supabase Client (Singleton)
@lru_cache()
def get_supabase_client() -> Client:
    """
    Get Supabase client instance.
    Cached to avoid creating multiple connections.
    """
    return create_client(
        settings.supabase_url,
        settings.supabase_service_key 
    )


@lru_cache()
def get_supabase_anon_client() -> Client:
    """
    Get Supabase client with anon key (for RLS-protected operations).
    """
    return create_client(
        settings.supabase_url,
        settings.supabase_anon_key
    )


# Dependency Functions (für FastAPI Depends)
def get_db() -> Client:
    """Dependency for Supabase database access"""
    return get_supabase_client()


def get_db_anon() -> Client:
    """Dependency for RLS-protected database access"""
    return get_supabase_anon_client()