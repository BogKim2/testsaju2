# 06 — LLM 해석 프롬프트 (핵심 · 실행 결과)

> 원본 지시: `prompts/06_prompt_llm.md`  
> 용도: LM Studio(OpenAI 호환) **`/v1/chat/completions`** 의 `messages` 에 `system` + `user` 로 전달.

## SSOT (코드)

실행 시 사용하는 문자열·버전·온도는 **[`backend/saju/llm/llm_client.py`](../backend/saju/llm/llm_client.py)** 가 단일 출처다. 아래는 복사·리뷰용 요약이며, 변경 시 **코드를 먼저 수정**하고 `PROMPT_VERSION` 을 올린다.

## MVP · 교차 참고

- API 응답의 `interpretation.prompt_version` · 레이어 분리: [03_engineering_architecture.md](03_engineering_architecture.md)
- 엔진만 결정·LLM은 JSON 해석만: [05_backend_saju_engine_spec.md](05_backend_saju_engine_spec.md)
- 스프린트 검증: [00_gstack_sprint_execution.md](00_gstack_sprint_execution.md)

---

## System (`SYSTEM_PROMPT_STRICT_JSON`)

코드에 정의된 문자열과 동일하다.

```
You are a Korean saju interpretation expert.

IMPORTANT RULES:
- You MUST NOT calculate saju or stems/branches.
- You ONLY interpret the given JSON.
- Do NOT invent missing data.
- Be consistent and structured.
- Section 6 MUST match year_fortune: use annual_pillar and year_stem_ten_god_vs_day_master exactly as given. Do not contradict target_year.

Output in KOREAN with these sections:
### 1. 한줄 요약
### 2. 전체 성향
### 3. 오행 분석
- 부족한 요소
- 과한 요소
- 균형 평가
### 4. 십성 해석
### 5. 영역별 운세
- 연애 / 재물 / 직업 / 건강
### 6. (NNNN년 운세 요약 — NNNN is year_fortune.target_year from JSON)

Tone: professional, soft Korean, no exaggeration, prefer "경향" over absolute claims.
Keep under 800 words.
```

6절 제목의 연도는 JSON 의 `year_fortune.target_year` 와 맞추고, 고정 연도(예: 2025) 문구는 쓰지 않는다.

---

## User (실제 구성)

[`generate_interpretation_from_strict_json`](../backend/saju/llm/llm_client.py) 가 만든다.

1. (선택) `display_name` 이 있으면 맨 위에 한 줄: `이름(참고만): {display_name}`
2. 고정 영문 전제:
   - `The following JSON is the only source of truth.`
   - `Do not add stems, branches, or counts not present in it.`
3. 빈 줄 뒤에 **`json.dumps(strict_payload, ensure_ascii=False, indent=2)`** 문자열.

`strict_payload` 는 API 가 LLM 에 넘기는 객체(`saju`, `elements`, `ten_gods`, `day_master`, `strength`, `year_fortune`, `meta` 등)이며, 문서 예시의 `{{SAJU_JSON}}` 는 이 **직렬화 결과**를 가리킨다.

---

## 런타임 상수 (코드와 동일)

| 항목 | 값 |
|------|-----|
| `PROMPT_VERSION` | `v2` |
| `LM_STUDIO_URL` | `http://localhost:1234/v1/chat/completions` |
| `MODEL_NAME` | `qwen3.5-9b` |
| `temperature` | `0.45` (대략 0.3~0.6 권장 안에서 설정) |
| `max_tokens` | `2048` |

---

## 폴백 (LM 미연결)

`call_llm_strict` 가 실패하면 [`_default_interpretation_strict`](../backend/saju/llm/llm_client.py) 가 동일 섹션(1~6) 형식의 마크다운을 엔진 JSON 만으로 생성한다. 응답 본문의 `interpretation.markdown` 은 이 경우에도 유효하다.

---

## 운영 메모

- 프롬프트·규칙을 바꾸면 **`llm_client.py` 의 `PROMPT_VERSION`** 을 올리고, [03](03_engineering_architecture.md) · API 응답과 설명을 맞춘다.
- `target_year` / `year_fortune` 은 API·엔진이 채우므로 LLM 프롬프트에서 연도를 하드코딩하지 않는다.
