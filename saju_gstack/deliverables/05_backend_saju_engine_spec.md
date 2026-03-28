# 05 — 사주 계산 엔진 스펙 (실행 결과)

> 원본 지시: `prompts/05_backend_spec.md`  
> **LLM 사용 없음** — Python 결정적 계산만.

## MVP 현재 구현 (`saju_gstack`)

실제 엔진은 [`backend/saju/core/calculator.py`](../backend/saju/core/calculator.py) · [`strict_json.py`](../backend/saju/core/strict_json.py) · [`sipseong.py`](../backend/saju/core/sipseong.py) 이고, HTTP 경계는 [`api_app.py`](../backend/saju/api_app.py) 이다. 스코프·음력 거절은 [01_cto_strategy.md](01_cto_strategy.md), API·레이어는 [03_engineering_architecture.md](03_engineering_architecture.md), 실행 로그는 [00_gstack_sprint_execution.md](00_gstack_sprint_execution.md) 와 교차 참고한다.

- **MVP 양력만:** `POST /api/saju/analyze` 에서 `calendar=lunar` → HTTP **400**; 엔진 `compute_saju_strict` 는 **양력 정수** `year, month, day, hour` 만 받는다.
- **타임존:** IANA 는 API 에서 검증되고, 요청 타임존의 “현재 연도”로 `target_year`(연운)를 잡는다. **기둥(사주) 계산은 벽시계 시(0–23)와 양력 일자만 사용**하며, 타임존으로 시각을 시프트하지 않는다(`api_app` 의 `datetime_policy` 문자열과 [03](03_engineering_architecture.md) 과 정합).
- **`warnings`:** 생시 미입력 시 정오(12시) 기본은 **API** 가 `birth_time_default_12` 를 `meta.warnings` 에 넣는다. 엔진은 정수 시만 받는다.

## 출력 JSON (엄격)

[`compute_saju_strict`](../backend/saju/core/strict_json.py) 반환:

```json
{
  "saju": {
    "year": { "stem": "", "branch": "" },
    "month": { "stem": "", "branch": "" },
    "day": { "stem": "", "branch": "" },
    "hour": { "stem": "", "branch": "" }
  },
  "elements": {
    "wood": 0,
    "fire": 0,
    "earth": 0,
    "metal": 0,
    "water": 0
  },
  "ten_gods": [],
  "day_master": "",
  "strength": ""
}
```

내부적으로 `_legacy` 키에 `calculate_saju` 원본 dict 가 들어간다. [`api_app.py`](../backend/saju/api_app.py) 는 응답 직전 `strict.pop("_legacy")` 후 **`pillars_detail`** 로만 외부화한다. API 전체 응답에는 `year_fortune`, `meta`, `interpretation` 등이 추가된다(03·[schemas/](../schemas/) SSOT).

## 입력

- **엔진:** `compute_saju_strict(year, month, day, hour, gender)` — `gender` 는 `남`/`여` 문자열이며 [`calculate_saju`](../backend/saju/core/calculator.py) 에 전달되나 **간지 계산에는 사용하지 않고** `birth` 메타에 포함된다.
- **MVP HTTP:** 위 정수는 API 가 양력 `birth_date`·`birth_time` 파싱 후에만 엔진에 넘긴다. `gender` 는 API 에서 `male`/`female` → `남`/`여` 매핑.

## 계산 파이프라인

### (A) API 경계 (`api_app`)

1. `calendar=lunar` → 400 (엔진 미호출).
2. `birth_date` `YYYY-MM-DD` 파싱, 연도 **1900–2100**.
3. `birth_time` 없으면 시 **12**, `warnings` 에 `birth_time_default_12`.
4. `timezone` IANA 검증 후 해당 존에서 `target_year` 산정(연운).
5. `compute_saju_strict` 호출 후 `_legacy` 분리, `build_year_fortune`, LLM 병합(엔진 본 문서 범위 밖).

### (B) 엔진 내부 (`calculator.py` → `strict_json.py`)

1. **연간지** — `get_year_gan` / `get_year_ji`.
2. **월지** — `JEOLGI_TABLE`·`MONTH_JIJI_SOLAR` 로 절기 기준 월주.
3. **월간** — `get_month_gan(year_gan, month_ji)`.
4. **일간·일지** — 기준일 대비 일수 모듈로 `get_gan_index` / `get_ji_index`.
5. **시지·시간** — `get_siji_index(hour)`, `get_hour_gan(day_gan, hour)`.
6. **오행** — 각 기둥 천간·지지 오행 합산 → 영문 키 `elements` (`strict_json`).
7. **십성** — `ten_gods_for_pillars` → `ten_gods`.
8. **신강 경향** — `strict_json` 의 단순 규칙으로 `strength` 문자열.

같은 입력 → **동일 출력**(정수 카운트 위주).

## 라이브러리 (제안)

- **`zoneinfo`:** API 에서 IANA 검증·`target_year`(엔진 본체는 정수만).
- **`pydantic`:** FastAPI 요청 스키마.
- **MVP 엔진 경로:** 음력 변환 라이브러리 **미사용**; 절기는 코드 내 `JEOLGI_TABLE` 등 **고정 테이블**.
- **`timezonefinder` / 수동 매핑:** `location` → IANA 는 후속(현재 `location` 은 정보용).

엔진 모듈에서 **`openai`, `httpx` 등 LLM/네트워크 import 금지** 권장.

## 엣지 케이스

| 케이스 | 대응 |
|--------|------|
| 생시 없음 | API: 12시 기본 + `meta.warnings` (`birth_time_default_12`) |
| 자시(23–01) | `get_siji_index`·시주 규칙 — 테스트로 고정 권장 |
| 음력 | API **400**, 엔진 미진입 (MVP) |
| 음력 윤달 | MVP 미지원(API 거절 또는 후속 스펙) |
| DST | 기둥은 벽시계 시; `zoneinfo` 는 API·연도 메타용 |
| 역사적 날짜 | API: 연도 1900–2100 |

## 결정성 보장

- 랜덤 시드 없음.
- 외부 API 호출 없음(엔진 내부).
- 모든 분기는 입력 + 상수 테이블에만 의존.
