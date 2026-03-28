# saju_gstack FastAPI — JWT 없음, POST /api/saju/analyze 만 (동기)

import os
from datetime import datetime, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .core.strict_json import compute_saju_strict
from .core.year_fortune import build_year_fortune
from .llm.llm_client import (
    generate_interpretation_from_strict_json,
    get_effective_max_tokens,
    get_llm_max_tokens_env_raw,
    get_model_name,
    PROMPT_VERSION,
)

app = FastAPI(
    title="saju-gstack API",
    description="결정적 사주 계산 + LLM은 JSON 해석만",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _log_llm_model_on_startup() -> None:
    # 실제로 LM Studio에 보내는 model id 확인용 (환경변수 LLM_MODEL_NAME 이 우선)
    env_raw = os.getenv("LLM_MODEL_NAME", "")
    print(
        f"[saju-gstack] LLM effective model id: {get_model_name()!r} "
        f"(LLM_MODEL_NAME env: {env_raw!r})"
    )
    # max_tokens=768 처럼 보이면: 다른 셸이 아니라 uvicorn 프로세스의 LLM_MAX_TOKENS 확인
    mt_raw = get_llm_max_tokens_env_raw()
    mt_eff = get_effective_max_tokens()
    print(
        f"[saju-gstack] LLM max_tokens: {mt_eff} "
        f"(LLM_MAX_TOKENS env raw: {mt_raw!r} - empty means code default)"
    )


class ApiSajuAnalyzeRequest(BaseModel):
    name: Optional[str] = None
    gender: str
    birth_date: str
    calendar: str = "solar"
    birth_time: Optional[str] = None
    timezone: str = "Asia/Seoul"
    location: Optional[str] = None


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "saju-gstack",
        "llm_model": get_model_name(),
        "llm_max_tokens": get_effective_max_tokens(),
        "llm_max_tokens_env": get_llm_max_tokens_env_raw(),
    }


@app.post("/api/saju/analyze")
def api_saju_analyze(req: ApiSajuAnalyzeRequest):
    if req.calendar not in ("solar", "lunar"):
        raise HTTPException(status_code=400, detail="calendar는 solar 또는 lunar 여야 합니다.")
    if req.calendar == "lunar":
        raise HTTPException(
            status_code=400,
            detail="MVP는 양력(solar)만 지원합니다.",
        )
    if req.gender not in ("male", "female"):
        raise HTTPException(status_code=400, detail="gender는 male 또는 female 입니다.")

    tz_key = (req.timezone or "").strip()
    if not tz_key:
        raise HTTPException(status_code=400, detail="timezone은 비울 수 없습니다. 예: Asia/Seoul")
    try:
        zi = ZoneInfo(tz_key)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="timezone은 유효한 IANA 이름이어야 합니다. 예: Asia/Seoul, UTC",
        )

    try:
        dt = datetime.strptime(req.birth_date.strip(), "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="birth_date는 YYYY-MM-DD 형식이어야 합니다.")

    year, month, day = dt.year, dt.month, dt.day
    if not (1900 <= year <= 2100):
        raise HTTPException(status_code=400, detail="연도는 1900~2100 범위여야 합니다.")

    warnings: list[str] = []
    hour = 12
    if req.birth_time and req.birth_time.strip():
        try:
            parts = req.birth_time.strip().split(":")
            hour = int(parts[0])
            if not (0 <= hour <= 23):
                raise ValueError
        except (ValueError, IndexError):
            raise HTTPException(status_code=400, detail="birth_time은 HH:mm 형식(00~23)이어야 합니다.")
    else:
        warnings.append("birth_time_default_12")

    gender_kr = "남" if req.gender == "male" else "여"

    strict = compute_saju_strict(
        year=year,
        month=month,
        day=day,
        hour=hour,
        gender=gender_kr,
    )
    legacy = strict.pop("_legacy")

    # 요청 timezone의 "현재 연도" = 올해 운세 대상 연도 (서버 로컬이 아님)
    target_year = datetime.now(zi).year
    datetime_policy = (
        "Pillars use solar Y-M-D and wall-clock hour (0–23) only; timezone does not shift pillar math. "
        "IANA timezone is validated and used for target_year (annual fortune year) in that zone. "
        "Location string is informational; geocode-to-timezone is out of scope for MVP."
    )

    year_fortune = build_year_fortune(strict["day_master"], target_year)

    strict_for_llm = {
        "saju": strict["saju"],
        "elements": strict["elements"],
        "ten_gods": strict["ten_gods"],
        "day_master": strict["day_master"],
        "strength": strict["strength"],
        "year_fortune": year_fortune,
        "meta": {
            "target_year": target_year,
            "timezone": tz_key,
            "datetime_policy": datetime_policy,
            "warnings": warnings,
        },
    }

    display_name = (req.name or "").strip() or "사용자"
    markdown = generate_interpretation_from_strict_json(strict_for_llm, display_name)

    return {
        "ok": True,
        "computed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "saju": strict["saju"],
        "elements": strict["elements"],
        "ten_gods": strict["ten_gods"],
        "day_master": strict["day_master"],
        "strength": strict["strength"],
        "year_fortune": year_fortune,
        "meta": {
            "timezone": tz_key,
            "location": req.location,
            "calendar": req.calendar,
            "warnings": warnings,
            "target_year": target_year,
            "datetime_policy": datetime_policy,
        },
        "interpretation": {
            "markdown": markdown,
            "model": get_model_name(),
            "prompt_version": PROMPT_VERSION,
        },
        "pillars_detail": legacy,
    }
