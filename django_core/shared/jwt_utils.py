import jwt
from datetime import datetime, timedelta
from pathlib import Path

PRIVATE_KEY = Path("keys/private.pem").read_text()
PUBLIC_KEY = Path("keys/public.pem").read_text()

def issue_jwt(payload: dict, expires_in: int = 3600, client_id: str=None) -> str:
    """Issue a JWT token with the given payload and expiration time."""
    payload_copy = payload.copy()
    payload_copy['exp'] = datetime.utcnow() + timedelta(seconds=expires_in)
    if client_id:
        payload_copy['client_id'] = client_id
    payload_copy['iat'] = datetime.utcnow()
    token = jwt.encode(payload_copy, PRIVATE_KEY, algorithm='RS256')
    return token

def verify_jwt(token: str) -> dict:
    """Verify a JWT token and return the decoded payload."""
    try:
        decoded = jwt.decode(token, PUBLIC_KEY, algorithms=['RS256'])
        return decoded
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")