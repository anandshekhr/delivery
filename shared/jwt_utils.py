from django.conf import settings
import jwt
from datetime import datetime, timedelta
from pathlib import Path

def issue_jwt(payload: dict, expires_minutes: int = 60):
    """
    payload: dictionary of data to encode (e.g., {"client_id": str(client.id)})
    returns: JWT string
    """
    token = jwt.encode(
        payload | {"exp": datetime.utcnow() + timedelta(minutes=expires_minutes)},
        settings.JWT_SECRET_KEY,
        algorithm="HS256"
    )
    return token

def verify_jwt(token: str) -> dict:
    """Verify a JWT token signed with HS256 and return the decoded payload."""
    try:
        decoded = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,  # use HS256 secret key
            algorithms=['HS256']
        )
        return decoded
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")