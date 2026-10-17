"""Demo-only staff auth: the Kita code returns a fixed bearer token.

This is NOT real security. It exists so the staff screens have a login step in the demo.
"""

import secrets

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings
from app.errors import Unauthorized

_bearer = HTTPBearer(auto_error=False)


def require_staff(creds: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> None:
    """Dependency for every /staff/* route except login."""
    expected = get_settings().staff_token
    if creds is None or not secrets.compare_digest(creds.credentials, expected):
        raise Unauthorized("Please log in again.")
