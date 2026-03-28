# 인메모리 세션 저장소
# 분석 세션의 상태와 결과를 관리합니다

import uuid
import time
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class AnalysisSession:
    """분석 세션 데이터 클래스"""
    session_id: str
    user_id: str
    name: str
    status: str  # "pending" | "running" | "done" | "error"
    progress: int  # 0~100
    created_at: float
    completed_at: Optional[float] = None
    error_msg: Optional[str] = None
    # 입력 데이터
    birth_year: int = 0
    birth_month: int = 0
    birth_day: int = 0
    birth_hour: int = 0
    gender: str = ""
    # 결과 데이터
    saju_result: Optional[dict] = None
    daewoon: Optional[list] = None
    seun: Optional[list] = None
    interpretation: Optional[str] = None


# 전역 세션 저장소
_sessions: dict[str, AnalysisSession] = {}


def create_session(
    user_id: str,
    name: str,
    birth_year: int,
    birth_month: int,
    birth_day: int,
    birth_hour: int,
    gender: str,
) -> str:
    """새 분석 세션 생성, session_id 반환"""
    session_id = str(uuid.uuid4())
    _sessions[session_id] = AnalysisSession(
        session_id=session_id,
        user_id=user_id,
        name=name,
        status="pending",
        progress=0,
        created_at=time.time(),
        birth_year=birth_year,
        birth_month=birth_month,
        birth_day=birth_day,
        birth_hour=birth_hour,
        gender=gender,
    )
    return session_id


def get_session(session_id: str) -> Optional[AnalysisSession]:
    """세션 조회"""
    return _sessions.get(session_id)


def update_progress(session_id: str, progress: int, status: str = "running") -> None:
    """분석 진행률 업데이트"""
    session = _sessions.get(session_id)
    if session:
        session.progress = progress
        session.status = status


def set_result(
    session_id: str,
    saju_result: dict,
    daewoon: list,
    seun: list,
    interpretation: str,
) -> None:
    """분석 결과 저장 및 완료 처리"""
    session = _sessions.get(session_id)
    if session:
        session.saju_result = saju_result
        session.daewoon = daewoon
        session.seun = seun
        session.interpretation = interpretation
        session.status = "done"
        session.progress = 100
        session.completed_at = time.time()


def set_error(session_id: str, msg: str) -> None:
    """에러 상태 저장"""
    session = _sessions.get(session_id)
    if session:
        session.status = "error"
        session.error_msg = msg


def get_history(user_id: str, limit: int = 20) -> list:
    """사용자의 분석 이력 조회 (최신순)"""
    user_sessions = [
        s for s in _sessions.values()
        if s.user_id == user_id and s.status == "done"
    ]
    user_sessions.sort(key=lambda x: x.created_at, reverse=True)
    return user_sessions[:limit]
