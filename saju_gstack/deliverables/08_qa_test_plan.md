# 08 — QA 시나리오 · 버그 추적 (실행 결과)

> 원본 지시: `prompts/08_qa.md`

## MVP 현재 구현 (`saju_gstack`)

수동 QA는 [frontend/src/App.tsx](../frontend/src/App.tsx) · [backend/saju/api_app.py](../backend/saju/api_app.py) · [llm_client.py](../backend/saju/llm/llm_client.py) 기준이다. 교차 참고: [00_gstack_sprint_execution.md](00_gstack_sprint_execution.md), [03_engineering_architecture.md](03_engineering_architecture.md), [04_design_ui_ux.md](04_design_ui_ux.md), [05_backend_saju_engine_spec.md](05_backend_saju_engine_spec.md), [07_architecture_code_review.md](07_architecture_code_review.md).

- **양력 MVP:** UI는 `calendar: "solar"` 고정. 음력 요청은 API **400** (엔진 미진입).
- **LLM 실패:** HTTP 500이 아니라 [`_default_interpretation_strict`](../backend/saju/llm/llm_client.py) 마크다운 폴백 → 성공 응답(200)에 `interpretation.markdown` 존재.
- **해석 표시:** 마크다운을 HTML로 파싱하지 않고 **텍스트**로 렌더(`whiteSpace: pre-wrap`) — React 자식 문자열 이스케이프. HTML 마크다운 렌더를 도입하면 그때 sanitize 검토.

## 기능 테스트

| ID | 시나리오 | 기대 결과 |
|----|----------|-----------|
| F1 | 알려진 **양력** 입력(날짜·시각)·`POST /api/saju/analyze` | `saju` 연월일시 간지가 엔진 기대와 일치(회귀 시 `compute_saju_strict` 또는 고정 JSON과 대조) |
| F2 | API 응답 JSON | `ok`, `saju`, `elements`, `ten_gods`, `day_master`, `strength`, `year_fortune`, `interpretation`(markdown·model·`prompt_version`), `meta`(timezone·warnings·`target_year` 등), `pillars_detail` 존재 (03·스키마 SSOT) |
| F3 | LLM 응답 | 한국어, `### 1`~`6` 구조·800단어 이하 정책([06](06_llm_interpretation_prompt.md)); 폴백 시에도 섹션 형식 유지 |

## 엣지 케이스

| ID | 시나리오 | 위험 | 조치 (MVP) |
|----|----------|------|------------|
| E1 | 생시 없음(또는 빈 `birth_time`) | 시주 기본값 오해 | API: 시 **12** + `meta.warnings` `birth_time_default_12`. UI 라벨: “비우면 12시 기본” ([App.tsx](../frontend/src/App.tsx)) |
| E2 | `calendar: lunar`·윤달 | 잘못된 변환 | **API 400** — 엔진·음력 라이브러리 미사용. 음력 지원은 후속 |
| E3 | 타임존·DST | 기둥 시프트 오해 | 기둥은 벽시·양력만([05](05_backend_saju_engine_spec.md)). `timezone` 은 검증·`target_year` 등 메타. DST 단위 테스트는 후속 권장 |
| E4 | 자시(23–01) | 일·시주 불일치 | `get_siji_index` 규칙·전용 테스트(후속) |

## UX

| ID | 시나리오 | 기대 (현재 UI) |
|----|----------|----------------|
| U1 | 제출 직후 | 제출 버튼 비활성 + **「분석 중…」** (별도 스켈레톤 컴포넌트 없음) |
| U2 | 네트워크 오류·4xx/5xx | `detail` 기반 **에러 문구** 표시(`role="alert"`). 재시도 전용 버튼 없음 — 폼 **재제출**으로 재시도 |
| U3 | 해석 영역 | 마크다운 **텍스트** 표시 — HTML 파이프라인 없음. 향후 `react-markdown` 등 도입 시 `rehype-sanitize` 등 검토 |

## 버그 리스트 (예시 템플릿)

| # | 내용 | 심각도 | 수정 제안 |
|---|------|--------|-----------|
| B1 | (과거 가정) LLM만 실패해도 전체 500 | — | **현 구현:** 폴백 마크다운으로 200. 해당 이슈는 재현 시 케이스만 기록 |
| B2 | 시 미입력 시 시주 의미가 사용자에게 불명확 | 중 | 입력 라벨·`meta.warnings` 노출 유지; 자시 규칙 안내 문구 강화는 선택 |
| B3 | (HTML 렌더 시) 마크다운 XSS | 중→조건부 | **MVP:** 텍스트 표시로 완화. HTML 렌더 시 sanitize 필수 |
| B4 | 동일 입력인데 해석만 매번 크게 달라짐 | 낮 | `temperature`·프롬프트 고정([06](06_llm_interpretation_prompt.md)) + “참고용” 문구 |

## 회귀

- 버그 수정 시 해당 시나리오를 자동화 테스트 또는 본 체크리스트에 추가한다.
