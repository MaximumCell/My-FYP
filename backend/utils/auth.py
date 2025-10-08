"""
Authentication helpers for backend routes.
Provides functions to resolve user identity from request headers (supports Clerk headers)
"""
from flask import Request
from typing import Optional


def resolve_user_id_from_headers(request: Request, user_service) -> str:
    """
    Resolve a current user id from request headers.

    Behavior:
    - If `X-Clerk-User-ID` header is present, try to find the user by clerk id and return internal user id.
    - If `X-User-ID` header is present and matches a clerk id (i.e. user lookup by clerk id succeeds), return internal id.
    - Otherwise, if `X-User-ID` is present, treat it as an internal user id and return it.
    - If none present or lookup fails, raise ValueError.
    """
    clerk_header = request.headers.get('X-Clerk-User-ID')
    alt_header = request.headers.get('X-User-ID')

    # Prefer explicit Clerk header
    clerk_id = clerk_header or alt_header
    if clerk_id:
        # Try to resolve via clerk id lookup
        try:
            user = user_service.get_user_by_clerk_id(clerk_id)
            if user:
                return str(user.id)
        except Exception:
            # ignore and fallback
            pass

    # If X-User-ID exists, treat it as internal user id
    if alt_header:
        return alt_header

    raise ValueError("User authentication required")
