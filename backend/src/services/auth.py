import base64
import hashlib
import hmac
import json
import os
import time

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

# Users configured via env vars
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
MEMBER_PASSWORD = os.getenv("MEMBER_PASSWORD", "member")
TOKEN_SECRET = os.getenv("TOKEN_SECRET", "change-me-in-production")
TOKEN_EXPIRY_SECONDS = int(os.getenv("TOKEN_EXPIRY_SECONDS", "86400"))  # 24h default


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    role: str


class TokenPayload(BaseModel):
    username: str
    role: str
    exp: int


def _sign_token(payload: dict) -> str:
    data = json.dumps(payload, separators=(',', ':'), sort_keys=True)
    sig = hmac.HMAC(TOKEN_SECRET.encode(), data.encode(), hashlib.sha256).hexdigest()
    token_data = base64.urlsafe_b64encode(data.encode()).decode()
    return f"{token_data}.{sig}"


def _verify_token(token: str) -> TokenPayload | None:
    parts = token.split('.')
    if len(parts) != 2:
        return None
    try:
        data = base64.urlsafe_b64decode(parts[0]).decode()
        expected_sig = hmac.HMAC(TOKEN_SECRET.encode(), data.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected_sig, parts[1]):
            return None
        payload = json.loads(data)
        if payload.get("exp", 0) < time.time():
            return None
        return TokenPayload(**payload)
    except Exception:
        return None


def _get_token_from_request(request: Request) -> str | None:
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        return auth[7:]
    return None


def get_current_user(request: Request) -> TokenPayload:
    token = _get_token_from_request(request)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = _verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload


def require_admin(user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.post("/login")
def login(request: LoginRequest) -> LoginResponse:
    if request.username == "admin" and request.password == ADMIN_PASSWORD:
        role = "admin"
    elif request.username == "member" and request.password == MEMBER_PASSWORD:
        role = "member"
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {
        "username": request.username,
        "role": role,
        "exp": int(time.time()) + TOKEN_EXPIRY_SECONDS
    }
    token = _sign_token(payload)
    return LoginResponse(token=token, role=role)


@router.get("/me")
def get_me(user: TokenPayload = Depends(get_current_user)) -> dict:
    return {"username": user.username, "role": user.role}
