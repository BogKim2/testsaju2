"""
mock_server.py — Harness Eng AI Agent 목(Mock) 백엔드
실제 FastAPI 백엔드가 완성되기 전까지 프론트엔드 테스트용으로 사용합니다.
포트: 8010
"""

import time
import uuid
import random
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Harness Eng AI - Mock Server", version="0.1.0")

# CORS 설정 (프론트엔드 http://localhost:5173 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 메모리 저장소 ──────────────────────────────────
sessions: dict[str, dict[str, Any]] = {}

# ── 로그인 ────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/auth/login")
def login(req: LoginRequest):
    # 데모 계정 검증
    if req.email == "demo@example.com" and req.password == "demo1234":
        return {
            "access_token": "mock-jwt-token-" + str(uuid.uuid4()),
            "refresh_token": "mock-refresh-token",
            "token_type": "bearer",
            "expires_in": 3600,
        }
    raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다")

# ── 분석 시작 ─────────────────────────────────────
@app.post("/analyze")
async def analyze_start(authorization: str = Header(default="")):
    session_id = str(uuid.uuid4())[:8]

    # 목 에이전트 데이터 저장
    sessions[session_id] = {
        "session_id": session_id,
        "project_name": f"HRN-MOCK-{session_id}",
        "status": "running",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "agents": [
            {"name": "design",  "status": "pending", "started_at": None, "completed_at": None},
            {"name": "bom",     "status": "pending", "started_at": None, "completed_at": None},
            {"name": "spec",    "status": "pending", "started_at": None, "completed_at": None},
            {"name": "quality", "status": "pending", "started_at": None, "completed_at": None},
            {"name": "routing", "status": "pending", "started_at": None, "completed_at": None},
        ],
        "start_time": time.time(),
    }
    return {"session_id": session_id, "status": "running", "message": "분석을 시작했습니다"}

# ── 분석 상태 조회 ────────────────────────────────
@app.get("/analyze/{session_id}/status")
def analyze_status(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")

    s = sessions[session_id]
    elapsed = time.time() - s["start_time"]

    # 2초마다 에이전트 하나씩 완료
    agent_names = ["design", "bom", "spec", "quality", "routing"]
    for i, agent in enumerate(s["agents"]):
        threshold = (i + 1) * 2.5
        if elapsed >= threshold and agent["status"] == "pending":
            agent["status"] = "running"
        if elapsed >= threshold + 1.5 and agent["status"] == "running":
            agent["status"] = "done"
            agent["completed_at"] = datetime.now(timezone.utc).isoformat()

    # 모두 완료되면 세션 상태 done
    all_done = all(a["status"] == "done" for a in s["agents"])
    if all_done:
        s["status"] = "done"

    return {
        "session_id": session_id,
        "status": s["status"],
        "agents": s["agents"],
    }

# ── 전체 결과 조회 ────────────────────────────────
@app.get("/analyze/{session_id}/result")
def analyze_result(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")

    s = sessions[session_id]
    return {
        "session_id": session_id,
        "project_name": s["project_name"],
        "status": s["status"],
        "summary": (
            "하네스 도면 분석이 완료되었습니다.\n"
            "- 설계 분석: 커넥터 12개, 와이어 47개 확인\n"
            "- BOM 검증: 총 38개 항목 중 36개 통과 (94.7%)\n"
            "- 전기 스펙: 전압강하 기준 내 정상\n"
            "- 품질 검사: 2건의 WARNING 이슈 발견\n"
            "- 경로 최적화: 총 배선 길이 12.4m → 11.8m 단축 가능"
        ),
        "agents": {
            "design": _mock_design(),
            "bom": _mock_bom(),
            "spec": _mock_spec(),
            "quality": _mock_quality(),
            "routing": _mock_routing(),
        },
    }

# ── 에이전트별 결과 ───────────────────────────────
@app.get("/analyze/{session_id}/result/{agent_name}")
def agent_result(session_id: str, agent_name: str):
    results = {
        "design": _mock_design(),
        "bom": _mock_bom(),
        "spec": _mock_spec(),
        "quality": _mock_quality(),
        "routing": _mock_routing(),
    }
    if agent_name not in results:
        raise HTTPException(status_code=404, detail="에이전트를 찾을 수 없습니다")
    return results[agent_name]

# ── 이력 조회 ─────────────────────────────────────
@app.get("/history")
def history():
    verdicts = ["PASS", "CONDITIONAL_PASS", "FAIL"]
    return [
        {
            "session_id": f"mock-{i:03d}",
            "project_name": f"HRN-2024-{100 + i}",
            "status": "done",
            "created_at": f"2026-03-{20 + i % 8:02d}T09:00:00Z",
            "summary": f"분석 완료 — {random.choice(verdicts)}",
        }
        for i in range(1, 8)
    ]

# ── 목 데이터 함수 ────────────────────────────────
def _mock_design():
    return {
        "connectors": [
            {"id": "CN1", "type": "MIL-DTL-38999", "pins": 24, "status": "OK"},
            {"id": "CN2", "type": "D-Sub 9", "pins": 9, "status": "OK"},
            {"id": "CN3", "type": "JST-XH 4P", "pins": 4, "status": "WARNING"},
        ],
        "wires": 47,
        "total_length_m": 12.4,
    }

def _mock_bom():
    items = [
        ("W-RED-1.25", "적색 전선 1.25sq", 12, "m", "JISC3306", "OK"),
        ("W-BLK-0.5",  "흑색 전선 0.5sq",   8, "m", "JISC3306", "OK"),
        ("W-WHT-2.0",  "백색 전선 2.0sq",   5, "m", "JISC3306", "WARNING"),
        ("CN-JST-XH4", "JST XH 4핀 커넥터",  3, "EA", "JST B4B-XH", "OK"),
        ("CN-DSUB9M",  "D-Sub 9핀 수",       2, "EA", "MIL-DTL-24308", "OK"),
        ("TM-FORK-M4", "포크 단자 M4",       16, "EA", "JIS C2805", "ERROR"),
    ]
    return {
        "totalItems": len(items),
        "passItems": sum(1 for i in items if i[5] == "OK"),
        "items": [
            {
                "partNumber": i[0], "description": i[1],
                "quantity": i[2], "unit": i[3],
                "standard": i[4], "status": i[5],
            }
            for i in items
        ],
    }

def _mock_spec():
    wires = [
        ("W1-PWR",   12.5, 24.0, 0.082, True),
        ("W2-SIG-A",  0.8, 12.0, 0.012, True),
        ("W3-SIG-B",  1.2, 12.0, 0.018, True),
        ("W4-GND",   10.0, 24.0, 0.095, True),
        ("W5-CAN-H",  0.5,  5.0, 0.008, True),
        ("W6-BATT",  15.0, 12.0, 0.215, False),
    ]
    return {
        "summary": "총 6개 와이어 중 5개 적합. W6-BATT 전압강하 0.215V로 허용값(0.2V) 초과.",
        "items": [
            {
                "wireName": w[0], "current": w[1],
                "voltage": w[2], "voltageDrop": w[3],
                "isAcceptable": w[4],
            }
            for w in wires
        ],
    }

def _mock_quality():
    return {
        "overallResult": "CONDITIONAL_PASS",
        "passRate": 91.3,
        "issues": [
            {
                "id": "Q001",
                "severity": "FAIL",
                "item": "TM-FORK-M4 단자",
                "detail": "포크 단자 압착 부위 절연 피복 손상 가능성",
                "action": "단자 재압착 및 절연 테이프 보강 필요",
            },
            {
                "id": "Q002",
                "severity": "WARNING",
                "item": "W6-BATT 전압강하",
                "detail": "허용값 0.2V 초과 (실측 0.215V)",
                "action": "전선 굵기 2.0sq → 2.5sq로 변경 권장",
            },
            {
                "id": "Q003",
                "severity": "WARNING",
                "item": "CN3 커넥터 배선",
                "detail": "피복 벗김 길이 12mm (기준: 8~10mm)",
                "action": "재작업 후 재검사",
            },
        ],
    }

def _mock_routing():
    return {
        "current_length_m": 12.4,
        "optimized_length_m": 11.8,
        "saving_m": 0.6,
        "saving_percent": 4.8,
        "routes": [
            {"segment": "ECU → CN1", "current": 3.2, "optimized": 3.0},
            {"segment": "CN1 → CN2", "current": 4.8, "optimized": 4.5},
            {"segment": "CN2 → CN3", "current": 4.4, "optimized": 4.3},
        ],
    }

# ── 실행 ──────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("  Harness Eng AI - Mock Backend")
    print("  http://localhost:8010")
    print("  http://localhost:8010/docs  <- Swagger UI")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8010, reload=False)
