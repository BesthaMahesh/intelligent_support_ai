import pytest
from backend.auth.password import hash_password, verify_password
from backend.auth.session import create_access_token, decode_access_token

def test_password_hashing():
    pwd = "EnterpriseSupportSecure2026"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_session():
    data = {"sub": "agent@support.ai", "role": "agent", "user_id": "USR-123"}
    token = create_access_token(data)
    assert token is not None
    assert isinstance(token, str)

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded.email == "agent@support.ai"
    assert decoded.role == "agent"
    assert decoded.user_id == "USR-123"
