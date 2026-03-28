"""pytest 공통 설정 — JWT/데모 계정 환경변수를 import 전에 고정."""

import os

# harness_eng import 전에 설정 (jwt_utils가 모듈 로드 시 읽음)
os.environ["JWT_SECRET_KEY"] = "pytest-jwt-secret-key-do-not-use-prod"
os.environ["AUTH_DEMO_EMAIL"] = "tester@example.com"
os.environ["AUTH_DEMO_PASSWORD"] = "pytest-password"
os.environ["HARNESS_SKIP_LLM"] = "1"

import pytest
from fastapi.testclient import TestClient

from harness_eng.api import app


@pytest.fixture
def client() -> TestClient:
    """FastAPI TestClient."""
    return TestClient(app)


@pytest.fixture
def access_token(client: TestClient) -> str:
    """로그인하여 Access JWT."""
    res = client.post(
        "/auth/login",
        json={"email": "tester@example.com", "password": "pytest-password"},
    )
    assert res.status_code == 200
    return str(res.json()["access_token"])


@pytest.fixture
def auth_headers(access_token: str) -> dict[str, str]:
    """Authorization Bearer 헤더."""
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def dummy_upload_file() -> tuple[str, bytes, str]:
    """multipart 업로드용 더미 파일."""
    return ("test.txt", b"dummy harness file content", "text/plain")
