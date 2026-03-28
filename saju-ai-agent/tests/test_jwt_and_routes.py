"""JWT 미들웨어 및 보호 라우트 테스트 (CONSTITUTION T-01)."""

import io


def test_health_does_not_require_auth(client) -> None:
    """헬스는 인증 없이 접근 가능."""
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["server"] == "ok"


def test_analyze_without_token_returns_401(client) -> None:
    """Bearer 없으면 UNAUTHORIZED."""
    res = client.post(
        "/analyze",
        data={"project_name": "p", "version": "1.0"},
        files={"file": ("a.txt", io.BytesIO(b"x"), "text/plain")},
    )
    assert res.status_code == 401
    body = res.json()
    assert body["error"] == "UNAUTHORIZED"
    assert body["status_code"] == 401


def test_login_invalid_password_returns_401(client) -> None:
    """잘못된 비밀번호."""
    res = client.post(
        "/auth/login",
        json={"email": "tester@example.com", "password": "wrong"},
    )
    assert res.status_code == 401
    assert res.json()["error"] == "UNAUTHORIZED"


def test_login_returns_bearer_tokens(client) -> None:
    """로그인 시 access_token, refresh_token, expires_in."""
    res = client.post(
        "/auth/login",
        json={"email": "tester@example.com", "password": "pytest-password"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data.get("expires_in") == 3600


def test_analyze_with_valid_token_returns_session(client, auth_headers: dict[str, str]) -> None:
    """유효한 Bearer로 분석 시작."""
    res = client.post(
        "/analyze",
        headers=auth_headers,
        data={"project_name": "demo", "version": "1.0"},
        files={"file": ("demo.txt", io.BytesIO(b"stub"), "text/plain")},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "started"
    assert "session_id" in data
    assert "agents" in data


def test_history_requires_auth(client) -> None:
    """GET /history 는 인증 필수."""
    res = client.get("/history")
    assert res.status_code == 401


def test_history_with_token_ok(client, auth_headers: dict[str, str]) -> None:
    """인증 후 이력 조회."""
    res = client.get("/history", headers=auth_headers)
    assert res.status_code == 200
    assert "total" in res.json()
    assert "items" in res.json()
