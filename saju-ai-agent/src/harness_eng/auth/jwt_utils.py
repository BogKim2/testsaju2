"""JWT 생성·검증 (Access 1h / Refresh 7d — ARCHITECTURE.md)."""

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

# 환경변수로 비밀키 설정 (운영에서는 반드시 강한 값)
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-only-change-me")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(subject: str) -> str:
    """Access 토큰 발급 — sub = 사용자 식별자(이메일 등)."""
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "typ": "access",
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": now,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """Refresh 토큰 발급."""
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "typ": "refresh",
        "exp": now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "iat": now,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Access 토큰만 검증 — typ이 access인지 확인."""
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    if payload.get("typ") != "access":
        raise jwt.InvalidTokenError("not an access token")
    return payload
