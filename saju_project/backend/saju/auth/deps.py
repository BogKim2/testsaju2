# FastAPI 의존성 - JWT 인증 검사

from fastapi import HTTPException, status, Header
from typing import Optional
from .jwt_utils import verify_token


def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    Authorization 헤더에서 Bearer 토큰 추출 후 검증
    인증 실패 시 401 반환
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.removeprefix("Bearer ").strip()
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 유효하지 않거나 만료되었습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"user_id": payload["sub"], "email": payload["email"]}
