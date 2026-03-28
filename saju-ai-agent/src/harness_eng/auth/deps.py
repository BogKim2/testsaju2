"""FastAPI Depends — Bearer JWT 미들웨어 역할."""

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from harness_eng.auth.jwt_utils import decode_access_token

# auto_error=False → 토큰 없을 때 직접 401 처리
_bearer = HTTPBearer(auto_error=False)


def _unauthorized(message: str) -> None:
    """API.md 공통 에러 JSON 형식."""
    raise HTTPException(
        status_code=401,
        detail={
            "error": "UNAUTHORIZED",
            "message": message,
            "status_code": 401,
        },
    )


async def require_access_token(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(_bearer),
    ],
) -> str:
    """
    Authorization: Bearer <access_token> 검증.
    반환값: JWT sub (보통 이메일).
    """
    if credentials is None:
        _unauthorized("Bearer token missing")
    try:
        payload = decode_access_token(credentials.credentials)
        sub = payload.get("sub")
        if not sub:
            _unauthorized("invalid token payload")
        return str(sub)
    except jwt.PyJWTError:
        _unauthorized("invalid or expired token")

