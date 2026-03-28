# JWT 토큰 생성 및 검증 유틸리티

import time
import hmac
import hashlib
import base64
import json
from typing import Optional

# 시크릿 키 (실제 운영에서는 환경변수 사용)
SECRET_KEY = "saju-secret-key-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 3600  # 1시간


def _base64url_encode(data: bytes) -> str:
    """Base64 URL 인코딩 (패딩 제거)"""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _base64url_decode(data: str) -> bytes:
    """Base64 URL 디코딩 (패딩 추가)"""
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data)


def create_access_token(user_id: str, email: str) -> str:
    """JWT 액세스 토큰 생성"""
    header = {"alg": ALGORITHM, "typ": "JWT"}
    payload = {
        "sub": user_id,
        "email": email,
        "iat": int(time.time()),
        "exp": int(time.time()) + ACCESS_TOKEN_EXPIRE_SECONDS,
    }

    # 헤더.페이로드 인코딩
    header_enc = _base64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_enc = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{header_enc}.{payload_enc}"

    # 서명 생성
    signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        signing_input.encode("utf-8"),
        hashlib.sha256
    ).digest()
    sig_enc = _base64url_encode(signature)

    return f"{signing_input}.{sig_enc}"


def verify_token(token: str) -> Optional[dict]:
    """JWT 토큰 검증 후 payload 반환 (실패 시 None)"""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None

        header_enc, payload_enc, sig_enc = parts
        signing_input = f"{header_enc}.{payload_enc}"

        # 서명 검증
        expected_sig = hmac.new(
            SECRET_KEY.encode("utf-8"),
            signing_input.encode("utf-8"),
            hashlib.sha256
        ).digest()
        expected_sig_enc = _base64url_encode(expected_sig)

        if not hmac.compare_digest(sig_enc, expected_sig_enc):
            return None

        # 페이로드 디코딩
        payload = json.loads(_base64url_decode(payload_enc))

        # 만료 시간 확인
        if payload.get("exp", 0) < int(time.time()):
            return None

        return payload

    except Exception:
        return None
