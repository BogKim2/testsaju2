# FastAPI 메인 API 라우터
# CORS, JWT 인증, 사주 분석 엔드포인트

import threading
import time
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .auth.jwt_utils import create_access_token
from .auth.deps import get_current_user
from .core.calculator import calculate_saju
from .core.daewoon import calculate_daewoon, calculate_seun
from .llm.llm_client import generate_saju_interpretation
from . import session_store as store

# 데모 계정
DEMO_EMAIL = "demo@saju.com"
DEMO_PASSWORD = "saju1234"
DEMO_USER_ID = "user-001"

app = FastAPI(
    title="사주 분석 API",
    description="사주 8자 계산 및 LLM 해설 API",
    version="1.0.0",
)

# CORS 설정 (개발 환경)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────── 요청/응답 스키마 ────────────────

class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str


class AnalyzeRequest(BaseModel):
    name: str
    gender: str  # "남" 또는 "여"
    birth_year: int
    birth_month: int
    birth_day: int
    birth_hour: int  # 0~23


class AnalyzeResponse(BaseModel):
    session_id: str
    message: str = "분석이 시작되었습니다."


# ──────────────── 인증 엔드포인트 ────────────────

@app.post("/auth/login", response_model=LoginResponse)
def login(req: LoginRequest):
    """JWT 토큰 발급"""
    if req.email != DEMO_EMAIL or req.password != DEMO_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
        )
    token = create_access_token(DEMO_USER_ID, DEMO_EMAIL)
    return LoginResponse(access_token=token, email=DEMO_EMAIL)


# ──────────────── 사주 분석 엔드포인트 ────────────────

def _run_analysis_background(session_id: str, req: AnalyzeRequest) -> None:
    """백그라운드에서 사주 분석 실행"""
    try:
        # 1단계: 사주 계산 (10%)
        store.update_progress(session_id, 10, "running")
        saju_result = calculate_saju(
            year=req.birth_year,
            month=req.birth_month,
            day=req.birth_day,
            hour=req.birth_hour,
            gender=req.gender,
        )
        time.sleep(0.5)

        # 2단계: 대운 계산 (40%)
        store.update_progress(session_id, 40, "running")
        pillars = saju_result["pillars"]

        # 월주 간지 인덱스 추출
        from .core.saju_data import CHEONGAN, JIJI
        month_gan_idx = CHEONGAN.index(pillars["month"]["gan"])
        month_ji_idx = JIJI.index(pillars["month"]["ji"])

        daewoon = calculate_daewoon(
            birth_year=req.birth_year,
            birth_month=req.birth_month,
            birth_day=req.birth_day,
            gender=req.gender,
            year_is_yang=saju_result["year_is_yang"],
            month_gan_idx=month_gan_idx,
            month_ji_idx=month_ji_idx,
        )
        time.sleep(0.5)

        # 3단계: 세운 계산 (60%)
        store.update_progress(session_id, 60, "running")
        current_year = datetime.now().year
        seun = calculate_seun(current_year, req.birth_year)
        time.sleep(0.3)

        # 4단계: LLM 해설 생성 (80%)
        store.update_progress(session_id, 80, "running")
        interpretation = generate_saju_interpretation(saju_result, req.name)
        time.sleep(0.2)

        # 5단계: 완료 (100%)
        store.set_result(session_id, saju_result, daewoon, seun, interpretation)

    except Exception as e:
        store.set_error(session_id, str(e))


@app.post("/saju/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest, user: dict = Depends(get_current_user)):
    """사주 분석 시작 - session_id 즉시 반환 후 백그라운드 실행"""
    # 입력 검증
    if not (1900 <= req.birth_year <= 2100):
        raise HTTPException(status_code=400, detail="연도가 유효하지 않습니다.")
    if not (1 <= req.birth_month <= 12):
        raise HTTPException(status_code=400, detail="월이 유효하지 않습니다.")
    if not (1 <= req.birth_day <= 31):
        raise HTTPException(status_code=400, detail="일이 유효하지 않습니다.")
    if not (0 <= req.birth_hour <= 23):
        raise HTTPException(status_code=400, detail="시간이 유효하지 않습니다.")
    if req.gender not in ["남", "여"]:
        raise HTTPException(status_code=400, detail="성별은 '남' 또는 '여'로 입력하세요.")

    # 세션 생성
    session_id = store.create_session(
        user_id=user["user_id"],
        name=req.name,
        birth_year=req.birth_year,
        birth_month=req.birth_month,
        birth_day=req.birth_day,
        birth_hour=req.birth_hour,
        gender=req.gender,
    )

    # 백그라운드 분석 실행
    t = threading.Thread(target=_run_analysis_background, args=(session_id, req))
    t.daemon = True
    t.start()

    return AnalyzeResponse(session_id=session_id)


@app.get("/saju/{session_id}/status")
def get_status(session_id: str, user: dict = Depends(get_current_user)):
    """분석 진행 상태 조회"""
    session = store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    if session.user_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")

    return {
        "session_id": session_id,
        "status": session.status,
        "progress": session.progress,
        "error": session.error_msg,
    }


@app.get("/saju/{session_id}/result")
def get_result(session_id: str, user: dict = Depends(get_current_user)):
    """분석 완료 결과 조회"""
    session = store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    if session.user_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")
    if session.status != "done":
        raise HTTPException(status_code=400, detail="분석이 아직 완료되지 않았습니다.")

    return {
        "session_id": session_id,
        "name": session.name,
        "gender": session.gender,
        "birth": {
            "year": session.birth_year,
            "month": session.birth_month,
            "day": session.birth_day,
            "hour": session.birth_hour,
        },
        "pillars": session.saju_result["pillars"],
        "ohaeng": session.saju_result["ohaeng"],
        "yangeum": session.saju_result["yangeum"],
        "ilgan": session.saju_result["ilgan"],
        "ilgan_ohaeng": session.saju_result["ilgan_ohaeng"],
        "animal": session.saju_result["animal"],
        "daewoon": session.daewoon,
        "seun": session.seun,
        "interpretation": session.interpretation,
        "created_at": session.created_at,
        "completed_at": session.completed_at,
    }


@app.get("/history")
def get_history(user: dict = Depends(get_current_user)):
    """분석 이력 목록 조회"""
    sessions = store.get_history(user["user_id"])
    return {
        "items": [
            {
                "session_id": s.session_id,
                "name": s.name,
                "gender": s.gender,
                "birth_year": s.birth_year,
                "birth_month": s.birth_month,
                "birth_day": s.birth_day,
                "animal": s.saju_result["animal"] if s.saju_result else "",
                "ilgan": s.saju_result["ilgan"] if s.saju_result else "",
                "created_at": s.created_at,
            }
            for s in sessions
        ]
    }


@app.get("/health")
def health():
    """헬스체크"""
    return {"status": "ok", "service": "사주 분석 API"}
