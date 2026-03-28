# 07 — 아키텍처 · 코드 리뷰 (실행 결과)

> 원본 지시: `prompts/07_review.md`  
> 관점: 엄격한 시니어 리뷰어

## MVP 현재 구현 (`saju_gstack`)

아래 판단은 실제 코드 기준이다. 레이아웃·API·에러 형식은 [03_engineering_architecture.md](03_engineering_architecture.md) · [schemas/](../schemas/) 와 교차 참고. 엔진 경계는 [05_backend_saju_engine_spec.md](05_backend_saju_engine_spec.md), LLM 프롬프트는 [06_llm_interpretation_prompt.md](06_llm_interpretation_prompt.md), 실행 로그는 [00_gstack_sprint_execution.md](00_gstack_sprint_execution.md) 와 맞춘다.

## 검토 범위

- architecture
- API design
- separation of logic (critical)
- LLM usage correctness

## 체크리스트

| 질문 | 기대 (MVP) |
|------|------------|
| 사주 계산이 완전히 결정적인가? | 예 — [`saju/core`](../backend/saju/core/) 만 계산(`calculator.py` → `compute_saju_strict`). 동일 입력 동일 출력(단위·골든 테스트는 후속 권장). |
| LLM이 해석만 담당하는가? | 예 — [`llm_client.py`](../backend/saju/llm/llm_client.py) 입력은 엔진 JSON + `year_fortune` 등, 출력은 자연어. 간지·오행 수치를 LLM이 생성하지 않음. |
| 환각 위험이 있는가? | 있음 — JSON에 없는 간지/숫자를 서술에 넣을 수 있음 → 프롬프트(6절·`year_fortune` 일치)·온도·선택적 검증으로 완화. |

## 아키텍처

**잘한 점**

- [`saju/core`](../backend/saju/core/) · [`llm`](../backend/saju/llm/) · [`api_app`](../backend/saju/api_app.py) 분리가 유지보수·감사에 유리하다.
- 단일 엔드포인트 `POST /api/saju/analyze` 는 MVP에 적합하다.

**개선 권장**

- 프론트·백 스키마: 현재 SSOT는 **[schemas/](../schemas/)** JSON Schema + [03](03_engineering_architecture.md) 수동 동기화. 모노레포 `shared-types` 또는 OpenAPI 생성은 **후속**으로 드리프트 방지에 유효.
- 해석 정책: LM Studio 미연결·HTTP 실패 시 [`_default_interpretation_strict`](../backend/saju/llm/llm_client.py) 가 마크다운을 채우므로 **성공 응답(200)에 `interpretation.markdown` 은 항상 존재**. `interpretation: null` 이나 **207** 은 선택 과제로 문서화할 수 있다.

## API 설계

- 오류: FastAPI 표준 **`detail`** 문자열 또는 배열(검증 실패). **`{ "ok": false, "error_code": ... }` 래퍼는 사용하지 않음** ([03](03_engineering_architecture.md) 와 동일).
- 후속: `error_code` + 사람이 읽을 `message` 통일은 별도 설계 시 검토.
- PII 로그 금지(생년월일 마스킹) 권장 — 운영 로깅 시 정책 유지.

## 관심사 분리 (핵심)

| 레이어 | 경로 | 책임 |
|--------|------|------|
| 엔진 | `saju/core/*` | 결정적 계산만, LLM/HTTP 없음 |
| LLM | `saju/llm/llm_client.py` | HTTP로 텍스트만, 사주 공식 없음 |
| API | `saju/api_app.py` | 검증·호출 순서·`pillars_detail` 병합 |

## 액션 가능 피드백

1. **골든 파일 테스트** — `tests/fixtures/saju_golden.json` 등으로 `compute_saju_strict` 회귀(후속).
2. **LLM 폴백 (현재 동작)** — 타임아웃·예외 시 `_default_interpretation_strict` 로 마크다운 생성, API 는 여전히 `interpretation` 객체 반환. `interpretation: null` 만 반환하는 모드는 선택 과제.
3. **프롬프트 버전** — **구현됨**: 응답 `interpretation.prompt_version` ↔ [`PROMPT_VERSION`](../backend/saju/llm/llm_client.py) (현재 v2). 변경 시 코드·[06](06_llm_interpretation_prompt.md) 동기화.
4. **선택** — 응답 본문 간지 키워드와 JSON 불일치 시 로그·재시도 가드는 비용 대비 검토.
