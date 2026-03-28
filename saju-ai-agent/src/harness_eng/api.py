"""FastAPI gateway — CORS, JWT, 비동기 파이프라인."""

import os
import threading
from pathlib import Path
from typing import Annotated, Any

import httpx
from fastapi import BackgroundTasks, Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from harness_eng.auth.deps import require_access_token
from harness_eng.auth.jwt_utils import create_access_token, create_refresh_token
from harness_eng.orchestrator.orchestrator import Orchestrator

# ── 앱 초기화 ──────────────────────────────────────────────────────────────
app = FastAPI(title="Harness Engineering AI Agent", version="0.1.0")

# ── CORS 설정 (프론트엔드 5173 포트 허용) ──────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 개발 단계 전체 허용 (운영에서는 도메인 지정)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_orch = Orchestrator()
_UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "uploads"))
_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 데모 인증 계정 (프론트엔드 LoginPage 기본값과 동일)
_AUTH_EMAIL = os.environ.get("AUTH_DEMO_EMAIL", "demo@example.com")
_AUTH_PASSWORD = os.environ.get("AUTH_DEMO_PASSWORD", "demo1234")


# ── 공통 에러 핸들러 ───────────────────────────────────────────────────────
@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP_ERROR",
            "message": str(exc.detail),
            "status_code": exc.status_code,
        },
    )


def _not_found(code: str, message: str) -> None:
    raise HTTPException(
        status_code=404,
        detail={"error": code, "message": message, "status_code": 404},
    )


def _llm_status() -> str:
    """LM Studio 연결 여부 간단 확인."""
    base = os.environ.get("LM_STUDIO_BASE", "http://localhost:1234")
    try:
        with httpx.Client(timeout=2.0) as c:
            r = c.get(f"{base.rstrip('/')}/v1/models")
            return "connected" if r.status_code == 200 else "disconnected"
    except httpx.HTTPError:
        return "disconnected"


# ── 헬스체크 ──────────────────────────────────────────────────────────────
@app.get("/health")
def health() -> dict[str, str]:
    return {
        "server": "ok",
        "llm": _llm_status(),
        "db": "connected",
    }


# ── 로그인 ────────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str = Field(..., description="사용자 이메일")
    password: str = Field(..., description="비밀번호")


@app.post("/auth/login")
def auth_login(body: LoginRequest) -> dict[str, Any]:
    """JWT 토큰 발급."""
    if body.email != _AUTH_EMAIL or body.password != _AUTH_PASSWORD:
        raise HTTPException(
            status_code=401,
            detail={"error": "UNAUTHORIZED", "message": "invalid email or password", "status_code": 401},
        )
    return {
        "access_token": create_access_token(body.email),
        "refresh_token": create_refresh_token(body.email),
        "expires_in": 3600,
        "token_type": "Bearer",
    }


# ── 분석 시작 (비동기 백그라운드) ─────────────────────────────────────────
@app.post("/analyze")
async def analyze(
    background_tasks: BackgroundTasks,
    _user: Annotated[str, Depends(require_access_token)],
    file: UploadFile = File(...),
    project_name: str = Form(...),
    version: str = Form("1.0"),
    agents: str | None = Form(None),
) -> JSONResponse:
    """파일 업로드 후 에이전트 파이프라인 백그라운드 실행 — 즉시 session_id 반환."""
    safe_name = Path(file.filename or "upload.bin").name
    dest = _UPLOAD_DIR / safe_name
    content = await file.read()
    dest.write_bytes(content)

    # 세션 생성 (에이전트 상태 pending으로 초기화)
    session_id = _orch.create_session(project_name, version, str(dest), agents)

    # 백그라운드 스레드에서 파이프라인 실행 (블로킹 방지)
    thread = threading.Thread(target=_orch.run_pipeline, args=(session_id,), daemon=True)
    thread.start()

    return JSONResponse(content={
        "session_id": session_id,
        "status": "running",
        "message": "분석을 시작했습니다",
    })


# ── 분석 상태 조회 ────────────────────────────────────────────────────────
@app.get("/analyze/{session_id}/status")
def analyze_status(
    session_id: str,
    _user: Annotated[str, Depends(require_access_token)],
) -> dict[str, Any]:
    """프론트엔드 AnalyzeStatusResponse 형식에 맞춘 응답."""
    st = _orch.memory.get(session_id)
    if st is None:
        _not_found("SESSION_NOT_FOUND", "session not found")

    # AgentProgress[] 형식으로 변환
    agents_list = []
    for name in st.agent_order:
        a = st.agent_states.get(name)
        agents_list.append({
            "name": name,
            "status": a.status if a else "pending",
            "started_at": a.started_at if a else None,
            "completed_at": a.completed_at if a else None,
        })

    return {
        "session_id": session_id,
        "status": st.status,
        "agents": agents_list,
    }


# ── 전체 결과 조회 ────────────────────────────────────────────────────────
@app.get("/analyze/{session_id}/result")
def analyze_result(
    session_id: str,
    _user: Annotated[str, Depends(require_access_token)],
) -> dict[str, Any]:
    """프론트엔드 FullResultResponse 형식에 맞춘 응답."""
    st = _orch.memory.get(session_id)
    if st is None:
        _not_found("SESSION_NOT_FOUND", "session not found")

    # 각 에이전트 결과를 프론트엔드 타입에 맞게 추출
    def _result(key: str) -> Any:
        out = st.agent_outputs.get(key)
        return out.get("result") if out else None

    q_result = _result("quality") or {}
    verdict = q_result.get("overall_verdict", "UNKNOWN")

    # 품질 결과를 프론트엔드 QualityResult 형식으로 변환
    quality_out = None
    if q_result:
        checklist = q_result.get("checklist", [])
        issues = [
            {
                "id": c.get("id", f"Q-{i}"),
                "severity": c.get("verdict", "INFO"),
                "item": c.get("item", ""),
                "detail": c.get("detail", ""),
                "action": c.get("action", ""),
            }
            for i, c in enumerate(checklist)
        ]
        pass_count = sum(1 for c in checklist if c.get("verdict") == "PASS")
        pass_rate = round(pass_count / max(len(checklist), 1) * 100, 1)
        quality_out = {
            "overallResult": verdict,
            "passRate": pass_rate,
            "issues": issues,
        }

    # BOM 결과를 프론트엔드 BomResult 형식으로 변환
    bom_out = None
    b_result = _result("bom") or {}
    if b_result:
        bom_list = b_result.get("bom", [])
        bom_items = [
            {
                "partNumber": b.get("part_no", ""),
                "description": b.get("name", ""),
                "quantity": b.get("qty", 0),
                "unit": "EA",
                "standard": str(b.get("spec", "")),
                "status": "OK" if not b.get("error") else "ERROR",
            }
            for b in bom_list
        ]
        bom_summary = b_result.get("summary", {})
        bom_out = {
            "totalItems": bom_summary.get("total_items", len(bom_items)),
            "passItems": bom_summary.get("total_items", len(bom_items)) - bom_summary.get("errors", 0),
            "items": bom_items,
        }

    # Spec 결과를 프론트엔드 SpecResult 형식으로 변환
    spec_out = None
    s_result = _result("spec") or {}
    if s_result:
        circuits = s_result.get("circuits", [])
        spec_items = [
            {
                "wireName": c.get("circuit_id", ""),
                "current": float(c.get("current", 0)),
                "voltage": float(c.get("voltage", 12.0)),
                "voltageDrop": float(c.get("voltage_drop", 0)),
                "isAcceptable": bool(c.get("acceptable", True)),
            }
            for c in circuits
        ]
        spec_out = {
            "items": spec_items,
            "summary": s_result.get("summary", "전기 스펙 검증 완료"),
        }

    return {
        "session_id": session_id,
        "project_name": st.project_name,
        "status": st.status,
        "summary": st.summary_text or f"{st.project_name} 분석 완료 — 종합 판정: {verdict}",
        "agents": {
            "design": _result("design"),
            "bom": bom_out,
            "spec": spec_out,
            "quality": quality_out,
            "routing": _result("routing"),
        },
    }


# ── 에이전트별 결과 ───────────────────────────────────────────────────────
@app.get("/analyze/{session_id}/result/{agent_name}")
def analyze_result_one(
    session_id: str,
    agent_name: str,
    _user: Annotated[str, Depends(require_access_token)],
) -> dict[str, Any]:
    """단일 에이전트 결과."""
    st = _orch.memory.get(session_id)
    if st is None:
        _not_found("SESSION_NOT_FOUND", "session not found")
    out = st.agent_outputs.get(agent_name)
    if out is None:
        _not_found("AGENT_NOT_FOUND", "agent output not found")
    return {"agent": agent_name, **out}


# ── 이력 조회 ─────────────────────────────────────────────────────────────
@app.get("/history")
def history(
    _user: Annotated[str, Depends(require_access_token)],
) -> list[dict[str, Any]]:
    """프론트엔드 HistoryItem[] 형식으로 반환."""
    rows = _orch.memory.list_sessions()
    result = []
    for st in rows:
        q = st.agent_outputs.get("quality", {})
        verdict = "UNKNOWN"
        if q and q.get("result"):
            verdict = str(q["result"].get("overall_verdict", "UNKNOWN"))
        result.append({
            "session_id": st.session_id,
            "project_name": st.project_name,
            "status": st.status,
            "created_at": st.created_at,
            "summary": st.summary_text or f"종합 판정: {verdict}",
        })
    return result
