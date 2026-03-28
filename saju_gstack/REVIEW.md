# saju_gstack 구현 검토 (요약)

## 아키텍처

- **백엔드** `backend/`: `saju/core`에서 사주·십성·strict JSON만 계산. `saju/llm`은 HTTP로 LM Studio 호출만 수행.
- **관심사 분리**: LLM 모듈에 천간/지지 공식 없음. 엔진에 `urllib` 없음.

## API

- `POST /api/saju/analyze`: 요청 스키마는 `schemas/api_analyze_request.schema.json`과 정합.
- 음력(`lunar`)은 400으로 명시적 거절(MVP).

## 환각 리스크

- LLM system 프롬프트에 “계산 금지·JSON만 근거” 명시.
- LM Studio 미기동 시 `_default_interpretation_strict`는 JSON 필드만 사용.

## 프론트엔드

- Vite 프록시로 `/api` → `8030`. LM Studio는 로컬에서 별도 실행.

## gstack 전역 설치

저장소: `https://github.com/garrytan/gstack` — `bun` 필요. Windows에서는 Git Bash 등에서:

`cd ~/.claude/skills/gstack && ./setup`

(클론은 `%USERPROFILE%\.claude\skills\gstack` 등에 가능)
