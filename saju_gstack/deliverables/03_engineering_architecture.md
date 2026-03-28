# 03 — 엔지니어링 · 아키텍처 (실행 결과)

> 원본 지시: `prompts/03_plan_eng.md`  
> 스택: React + Vite 프론트, FastAPI 백엔드, LM Studio(OpenAI 호환) LLM  
> 본 문서의 **API 요청/응답 필드**는 코드와 동일하게 유지하며, 세부 제약은 [schemas/api_analyze_request.schema.json](../schemas/api_analyze_request.schema.json) · [schemas/api_analyze_response.schema.json](../schemas/api_analyze_response.schema.json) 를 SSOT로 본다.

스프린트 실행·다른 deliverable과의 교차 참고: [00_gstack_sprint_execution.md](00_gstack_sprint_execution.md), [01_cto_strategy.md](01_cto_strategy.md), [02_ceo_product_plan.md](02_ceo_product_plan.md).

## 실제 레이아웃 (`saju_gstack/`)

모노레포 `apps/web` 구조가 아니라, 단일 프로젝트 폴더 아래 프론트·백엔드를 둔다. 프론트는 **Tailwind/shadcn 없이** Vite + React 인라인 스타일 중심([`frontend/src/App.tsx`](../frontend/src/App.tsx)).

```
saju_gstack/
  frontend/
    src/
      App.tsx
      main.tsx
      index.css
    vite.config.ts
    package.json
  backend/
    main.py                    # uvicorn 진입: from saju.api_app import app
    saju/
      api_app.py               # FastAPI, CORS, GET /health, POST /api/saju/analyze
      core/                    # 순수 사주 엔진 (LLM import 없음)
        calculator.py
        strict_json.py         # compute_saju_strict → API JSON
        sipseong.py
        saju_data.py
        year_fortune.py
      llm/
        llm_client.py          # LM Studio HTTP, JSON 해석만
  schemas/
    api_analyze_request.schema.json
    api_analyze_response.schema.json
  deliverables/
  prompts/
```

## API 스키마

### `POST /api/saju/analyze`

필드 정의·필수 여부는 **JSON Schema 파일**을 따른다. 아래는 요약 예시이다.

**Request (요약)**

```json
{
  "name": null,
  "gender": "male",
  "birth_date": "1990-01-15",
  "calendar": "solar",
  "birth_time": "12:00",
  "timezone": "Asia/Seoul",
  "location": null
}
```

- `gender`: API 구현상 **`male` | `female`** 만 허용.
- `calendar`: `lunar` 는 MVP에서 **400** (양력만).
- `birth_time`: 없으면 서버에서 12시 기본 + `warnings` 에 `birth_time_default_12` 등.
- `timezone`: IANA 문자열, `zoneinfo` 로 검증. 원국 간지 계산에는 **양력 연·월·일·시(벽시계 정수)** 만 사용하고, 타임존은 **`target_year`(올해 운세 연도)** 산정 등 메타에 사용 ([`api_app.py`](../backend/saju/api_app.py)).

**Response 200 (요약)**

```json
{
  "ok": true,
  "computed_at": "2026-03-28T12:00:00Z",
  "saju": {
    "year": { "stem": "경", "branch": "오" },
    "month": { "stem": "…", "branch": "…" },
    "day": { "stem": "경", "branch": "오" },
    "hour": { "stem": "…", "branch": "…" }
  },
  "elements": { "wood": 0, "fire": 0, "earth": 0, "metal": 0, "water": 0 },
  "ten_gods": ["비견", "겁재", "비견", "편관"],
  "day_master": "경",
  "strength": "신강(경향)",
  "year_fortune": {
    "target_year": 2026,
    "annual_pillar": { "stem": "병", "branch": "오" },
    "year_stem_ten_god_vs_day_master": "편관"
  },
  "meta": {
    "timezone": "Asia/Seoul",
    "location": null,
    "calendar": "solar",
    "warnings": [],
    "target_year": 2026,
    "datetime_policy": "Pillars use solar Y-M-D and wall-clock hour …"
  },
  "interpretation": {
    "markdown": "string",
    "model": "qwen3.5-9b",
    "prompt_version": "v2"
  },
  "pillars_detail": {}
}
```

- `pillars_detail`: 엔진 내부 레거시 dict(진단·디버그용). 프론트는 필수 표시 대상 아님.
- `interpretation.prompt_version`: [`llm_client.py`](../backend/saju/llm/llm_client.py) 의 `PROMPT_VERSION` 과 동기.

**Error (FastAPI)**

- HTTP **4xx / 5xx** 시 본문은 보통 `{"detail": "..." }` 또는 `{"detail": [ ... ] }` 형태 (검증 실패 시 `detail` 배열).
- **`{ "ok": false, "error_code": ... }` 래퍼는 사용하지 않음.**

## 데이터 흐름 (단계)

1. 프론트: 폼 → `POST /api/saju/analyze` (JSON).
2. `api_app`: Pydantic 검증, `calendar=lunar` → 400, 잘못된 `timezone` → 400.
3. **`saju.core`만**으로 원국: `compute_saju_strict` → 사주·오행·십성·일간·신강 경향. **음력 변환·자시를 타임존으로 보정하는 로직은 MVP에 없음** (정책은 `meta.datetime_policy` 문자열).
4. `build_year_fortune` 로 해당 연도 연주·일간 대비 연간 십성 (결정적 JSON).
5. LLM용 payload (`strict_for_llm`) 구성 후 **`llm_client`** 가 LM Studio에 system+user(JSON 문자열) 전달. **`core`는 `llm`을 import하지 않고, `llm`은 HTTP로 사주 재계산을 하지 않음.**
6. 응답 병합: `ok`, `computed_at`, 엔진 필드, `year_fortune`, `interpretation`, `pillars_detail`.
7. 프론트: 표·오행 막대·연운 블록·마크다운 등.

## 관심사 분리 (핵심)

| 레이어 | 경로(실제) | 책임 | 금지 |
|--------|------------|------|------|
| 엔진 | `saju/core/*` | 결정적 계산만 | HTTP, LLM 호출 |
| LLM | `saju/llm/llm_client.py` | 텍스트 생성만 | 사주 공식·역학 계산 |
| API | `saju/api_app.py` | 검증·호출 순서·HTTP 에러 | 엔진 로직 중복·LLM에 계산 위임 |
| 프론트 | `frontend/src/*` | UI·fetch | 사주 알고리즘 |

**제약:** LLM은 사주를 계산하지 않는다. 엔진·JSON이 단일 진실 공급원(SSOT)이다.
