# API — FastAPI 엔드포인트 명세

## 서버 기본 정보

| 항목 | 값 |
|------|-----|
| Base URL (개발) | `http://localhost:8000` |
| Base URL (운영) | `https://api.harness-eng.com` |
| 인증 방식 | JWT Bearer Token |
| 응답 형식 | JSON |
| API 문서 (자동) | `{BASE_URL}/docs` (Swagger UI) |

---

## 엔드포인트 목록

### 상태 확인

```
GET  /health
```

응답:
```json
{
  "server": "ok",
  "llm": "connected",
  "db": "connected"
}
```

---

### 분석 세션

#### 분석 시작 (파일 업로드)

```
POST /analyze
Content-Type: multipart/form-data
Authorization: Bearer {token}
```

요청:
```
file         : DXF 또는 Excel 파일 (필수)
project_name : 프로젝트 이름 (필수)
version      : 설계 버전 (선택, 기본값: "1.0")
agents       : 실행할 에이전트 목록 (선택, 기본값: 전체)
               예) "design,bom,spec,quality,routing"
```

응답:
```json
{
  "session_id": "sess-20260328-abc123",
  "status": "started",
  "estimated_seconds": 180,
  "agents": ["design", "bom", "spec", "quality", "routing"]
}
```

---

#### 분석 진행 상태 조회

```
GET /analyze/{session_id}/status
Authorization: Bearer {token}
```

응답:
```json
{
  "session_id": "sess-20260328-abc123",
  "overall_status": "running",
  "progress_pct": 60,
  "agents": {
    "design":  {"status": "done",    "duration_ms": 8200},
    "bom":     {"status": "done",    "duration_ms": 5100},
    "spec":    {"status": "running", "duration_ms": null},
    "quality": {"status": "pending", "duration_ms": null},
    "routing": {"status": "pending", "duration_ms": null}
  }
}
```

---

#### 분석 결과 조회

```
GET /analyze/{session_id}/result
Authorization: Bearer {token}
```

응답:
```json
{
  "session_id": "sess-20260328-abc123",
  "project_name": "엔진 하네스",
  "version": "v3.1",
  "created_at": "2026-03-28T10:00:00Z",
  "overall_verdict": "CONDITIONAL_PASS",
  "summary": {
    "total_issues": 5,
    "fail": 1,
    "warning": 3,
    "info": 1
  },
  "agents": {
    "design":  { "status": "done", "result": { ... } },
    "bom":     { "status": "done", "result": { ... } },
    "spec":    { "status": "done", "result": { ... } },
    "quality": { "status": "done", "result": { ... } },
    "routing": { "status": "done", "result": { ... } }
  }
}
```

---

### 개별 에이전트 결과

```
GET /analyze/{session_id}/result/{agent_name}
Authorization: Bearer {token}
```

`agent_name`: `design` | `bom` | `spec` | `quality` | `routing`

예시 — BOM Agent 결과:
```json
{
  "agent": "bom",
  "status": "done",
  "duration_ms": 5100,
  "result": {
    "total_items": 24,
    "errors": 1,
    "warnings": 2,
    "total_cost": 125400,
    "bom": [ ... ]
  }
}
```

---

### 이력 조회

```
GET /history
Authorization: Bearer {token}
Query: page=1&limit=20&project_name=엔진
```

응답:
```json
{
  "total": 42,
  "page": 1,
  "items": [
    {
      "session_id": "sess-20260328-abc123",
      "project_name": "엔진 하네스",
      "version": "v3.1",
      "verdict": "CONDITIONAL_PASS",
      "created_at": "2026-03-28T10:00:00Z"
    }
  ]
}
```

---

### 인증

#### 로그인

```
POST /auth/login
Content-Type: application/json
```

요청:
```json
{ "email": "user@example.com", "password": "..." }
```

응답:
```json
{
  "access_token":  "eyJ...",
  "refresh_token": "eyJ...",
  "expires_in":    3600
}
```

---

## 공통 에러 응답 형식

```json
{
  "error": "INVALID_FILE_FORMAT",
  "message": "지원하지 않는 파일 형식입니다. DXF 또는 Excel 파일을 업로드하세요.",
  "status_code": 400
}
```

| 에러 코드 | HTTP | 의미 |
|-----------|------|------|
| `INVALID_FILE_FORMAT` | 400 | 지원 안 하는 파일 형식 |
| `FILE_TOO_LARGE` | 400 | 파일 크기 초과 (최대 50MB) |
| `UNAUTHORIZED` | 401 | 인증 토큰 없음/만료 |
| `SESSION_NOT_FOUND` | 404 | 세션 ID 없음 |
| `AGENT_FAILED` | 500 | 에이전트 실행 실패 |
| `LLM_UNAVAILABLE` | 503 | LLM 서버 연결 불가 |
