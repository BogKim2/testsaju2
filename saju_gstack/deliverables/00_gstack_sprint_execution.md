# gstack 순차 실행 로그 — `deliverables` 00 → 08

## STATUS (gstack Completion Protocol)

**DONE_WITH_CONCERNS**

- **완료:** `00` 인덱스 역할, `01`~`08` 문서별로 스킬 매핑·코드 정합·체크리스트를 순서대로 실행함. `backend`에서 `compute_saju_strict(1990,1,15,12,'남')` 스모크 테스트 성공(exit 0).
- **주의:** Claude Code 슬래시(`/office-hours` 등)와 gstack **`$B` browse** 기반 E2E는 이 저장소 에이전트가 대신 실행하지 않음. 아래 **자동 검증**은 백엔드·API만 해당.

---

## 실행 기록 (자동 검증, 2026-03-28)

CTO 전략 문서와 코드 정합(음력·타임존·`year_fortune` 등)은 [01_cto_strategy.md](01_cto_strategy.md) 의 **MVP 현재 구현 범위** 단락과 교차 참고. CEO 플랜(단일 페이지·IA·복사)은 [02_ceo_product_plan.md](02_ceo_product_plan.md) 의 **MVP 현재 UI** 단락과 교차 참고. 엔지니어링 레이아웃·API SSOT·에러 형식은 [03_engineering_architecture.md](03_engineering_architecture.md) 와 [schemas/](../schemas/) 를 교차 참고. 디자인·와이어·폰트·탭 vs 스크롤은 [04_design_ui_ux.md](04_design_ui_ux.md) 의 **MVP 현재 구현** 단락과 교차 참고. 엔진·양력·벽시·`warnings`·`_legacy`/`pillars_detail` 은 [05_backend_saju_engine_spec.md](05_backend_saju_engine_spec.md) 의 **MVP 현재 구현** 단락과 교차 참고한다. LLM system/user·`PROMPT_VERSION`·연운 6절 규칙은 [06_llm_interpretation_prompt.md](06_llm_interpretation_prompt.md) 와 [`llm_client.py`](../backend/saju/llm/llm_client.py) 를 교차 참고한다. 아키텍처 리뷰·`detail` 에러·폴백 마크다운 정책은 [07_architecture_code_review.md](07_architecture_code_review.md) 와 교차 참고한다. QA 시나리오·UI 기대·엣지(MVP)는 [08_qa_test_plan.md](08_qa_test_plan.md) 와 교차 참고한다.

| 검증 | 명령/동작 | 결과 |
|------|-----------|------|
| 엔진 UTF-8 JSON | `PYTHONIOENCODING=utf-8` + `compute_saju_strict(1990,1,15,12,'남')` | `day_master` 경, 연주 경오·일주 경오 등 JSON 구조 정상 |
| HTTP | `uvicorn main:app --port 8030` | `GET /health` → `{"status":"ok","service":"saju-gstack"}` |
| 동기 API | `POST /api/saju/analyze` (양력, male, 1990-01-15 12:00) | `ok: true`, 해석 문자열 길이 약 1165자 (LM 폴백 포함 가능) |
| 동기 API + tz | 동일 바디에 `timezone: "Asia/Seoul"` (프론트 기본과 동일) | `meta.timezone` 일치, `year_fortune` 포함 |
| 응답 필드 | 성공 본문 | `year_fortune`, `pillars_detail`, `interpretation.prompt_version` 존재 (03 문서·스키마와 정합) |
| 음력 거절 | 동일 엔드포인트 `calendar: lunar` | HTTP **400** (MVP 양력만) |
| 프로세스 | 검증 후 `uvicorn` 프로세스 종료 | 로컬 포트 정리 |

**아직 안 함:** `frontend` `npm run dev` + gstack **`/qa`** 또는 **`$B goto http://localhost:5175`** 로 화면 클릭 검증.

---

## 순차 실행 표 (00 → 08)

| Step | gstack 스킬(대응) | 산출/확인 | 근거 |
|------|-------------------|-----------|------|
| **00** | 스프린트 인덱스 | 본 파일 + 매핑표 | 아래 섹션 전체 |
| **01** | `/office-hours` | 스코프·리스크·MVP 정합 | `01_cto_strategy.md`, `api_app.py` 음력 400 |
| **02** | `/plan-ceo-review` | 플로·IA vs `App.tsx` | 단일 페이지·오행 막대·복사, 공유 URL은 미구현 |
| **03** | `/plan-eng-review` | API·레이어 분리 | `03_engineering_architecture.md`, `schemas/`, `api_app.py`, `core/`, `llm/` |
| **04** | `/plan-design-review` | MVP·와이어·폰트 vs 목표(shadcn/Tailwind) | `04_design_ui_ux.md`, `index.css` 시스템 폰트·`App.tsx` 인라인·스크롤 한 열·탭 후속 |
| **05** | Build(엔진) | 결정적 JSON·MVP 정책 | `05_backend_saju_engine_spec.md`, 양력·벽시·API `warnings`, `calculator.py`·`strict_json.py`·`sipseong.py` |
| **06** | 프롬프트 고정 | JSON만 해석·v2 | `06_llm_interpretation_prompt.md`, `llm_client.py` `SYSTEM_PROMPT_STRICT_JSON`, `PROMPT_VERSION` v2, `year_fortune` 6절 규칙 |
| **07** | `/review` | 레이어·LLM 격리·에러 형식 | `07_architecture_code_review.md`, FastAPI `detail`, `_default_interpretation_strict` 폴백, `core`/`llm`/`api_app` |
| **08** | `/qa` | 시나리오·수동 QA | `08_qa_test_plan.md`, 양력·폴백·텍스트 해석 표시, 브라우저 자동화는 미실행 |

---

## GSTACK REVIEW REPORT (플레이스홀더)

로컬에 `/plan-ceo-review` 등이 아직 돌지 않았으면 아래와 같음. 나중에 `gstack-review-read` 출력이 있으면 표를 덮어쓰면 됨.

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope and strategy | 0 | — | See 02 row |
| Eng Review | `/plan-eng-review` | Architecture and tests | 0 | — | See 03 row |
| Design Review | `/plan-design-review` | UI/UX gaps | 0 | — | See 04 row |

**VERDICT:** NO AUTOMATED REVIEW RUNS IN CI — optional next: `/autoplan` or individual skills in Claude Code.

---

> **방법:** Garry Tan [gstack](https://github.com/garrytan/gstack)의 스프린트 흐름(Think → Plan → Build → Review → Test)에 맞춰, `deliverables/` 각 문서를 **역할·산출물 기준으로 한 번씩 진행**하고, 현재 **`saju_gstack/` 코드와의 정합**을 표로 남깁니다.  
> 로컬에서 슬래시 명령(`/office-hours` 등)을 쓰려면 `~/.claude/skills/gstack`에서 `./setup`(bun 필요)을 실행하면 됩니다. **에이전트 세션에서는 아래를 그 실행에 해당하는 산출로 간주합니다.**

---

## gstack 스킬 ↔ 본 프로젝트 문서 매핑

| 순서 | gstack에 가까운 단계 | `deliverables` 파일 | 역할 |
|------|------------------------|---------------------|------|
| 1 | `/office-hours` (제품 방향·전제 검증) | `01_cto_strategy.md` | CTO · 스코프·리스크·MVP |
| 2 | `/plan-ceo-review` | `02_ceo_product_plan.md` | CEO · 플로·화면·IA·수익 |
| 3 | `/plan-eng-review` | `03_engineering_architecture.md` | 아키텍처·API·관심사 분리 |
| 4 | `/plan-design-review` | `04_design_ui_ux.md` | 디자인 시스템·와이어프레임 |
| 5 | 구현 스펙 (코드 레이어) | `05_backend_saju_engine_spec.md` | 결정적 엔진·JSON·엣지 |
| 6 | 프롬프트 고정 (품질) | `06_llm_interpretation_prompt.md` | LLM은 JSON만 해석 |
| 7 | `/review` | `07_architecture_code_review.md` | 아키텍처·LLM 격리 |
| 8 | `/qa` | `08_qa_test_plan.md` | 시나리오·심각도 |

---

## 01 — CTO 전략 (`01_cto_strategy.md`)

| 항목 | 진행 내용 | 코드/산출 반영 |
|------|-----------|----------------|
| 스코프 | Python 결정적 계산 + JSON + LLM 해석만 | `backend/saju/core/*`, `strict_json.py` |
| 리스크 | 환각·음력/시간 — 음력 MVP 제외, 시각 없으면 12시+경고 | `api_app.py` 400 on lunar, `warnings` |
| MVP 경계 | 회원/결제 없음 | gstack API만 JWT 없음 |

**상태:** ✅ 문서와 방향 일치.

---

## 02 — CEO 플랜 (`02_ceo_product_plan.md`)

| 항목 | 진행 내용 | 현재 구현 |
|------|-----------|-----------|
| 플로우 | 방문 → 입력 → 결과 | `frontend/src/App.tsx` 단일 폼 → 결과 표시 |
| 화면 4종 | 랜딩/입력/결과/공유 | MVP는 **입력+결과 동일 페이지** (공유·별도 랜딩 미구현) |
| IA | summary / chart / elements / ten gods / 해석 | JSON + `interpretation.markdown` + `pillars_detail` |

**상태:** ✅ 핵심 플로우 충족 · ⚠️ 공유 페이지·별도 랜딩은 미구현(문서의 “optional” 범위).

---

## 03 — 엔지니어링 (`03_engineering_architecture.md`)

| 항목 | 문서 요구 | 실제 (`saju_gstack`) |
|------|-----------|------------------------|
| 레이아웃 | 단일 `saju_gstack/` 트리 | `frontend/` + `backend/saju/` + `schemas/` (문서 **실제 레이아웃** 절과 일치) |
| API | `POST /api/saju/analyze` | `backend/saju/api_app.py` · JSON Schema SSOT |
| 관심사 분리 | 엔진 / LLM / HTTP | `core/` vs `llm/` vs `api_app.py` |

**상태:** ✅ API·분리·스키마·에러 형식(`detail`) 문서 갱신됨.

---

## 04 — 디자인 (`04_design_ui_ux.md`)

| 항목 | 문서 | 현재 |
|------|------|------|
| shadcn + Tailwind | 권장 | MVP는 **인라인 스타일 + 단순 CSS** (`index.css`) |
| 다크 퍼스트 | ✅ | 배경 `#0c0e12` 등 반영 |

**상태:** ⚠️ shadcn/Tailwind는 미적용 — “minimal MVP”로 두고, 차기에 `04`에 맞춰 Tailwind+shadcn 도입 가능.

---

## 05 — 백엔드 엔진 스펙 (`05_backend_saju_engine_spec.md`)

| 항목 | 요구 | 구현 |
|------|------|------|
| 결정적 계산 | 동일 입력 동일 출력 | `calculator.py` + `sipseong.py` |
| strict JSON | saju, elements, ten_gods, day_master, strength | `strict_json.py` |
| LLM 금지 | 엔진에 LLM 없음 | `core/`에 `urllib` 없음 |

**상태:** ✅

---

## 06 — LLM 프롬프트 (`06_llm_interpretation_prompt.md`)

| 항목 | 요구 | 구현 |
|------|------|------|
| JSON만 해석 | system 규칙 | `llm/llm_client.py` `SYSTEM_PROMPT_STRICT_JSON` |
| 실패 시 | 엔진 데이터만 사용 | `_default_interpretation_strict` |
| 버전 | 추적 | `PROMPT_VERSION = "v1"` |

**상태:** ✅

---

## 07 — 코드 리뷰 (`07_architecture_code_review.md`)

| 체크 | 결과 |
|------|------|
| 결정적 사주 | ✅ |
| LLM 해석만 | ✅ |
| 환각 완화 | 프롬프트 + 폴백 · 후처리 검증은 선택 |

**상태:** ✅ `REVIEW.md`와 합치.

---

## 08 — QA (`08_qa_test_plan.md`)

| 시나리오 | 권장 조치 |
|----------|-----------|
| 양력·시간·경계 | 수동: 알려진 생일로 간지 대조 |
| LLM 다운 | LM Studio 끈 상태로 API 호출 → 기본 해설 |
| 프론트 프록시 | `npm run dev` + 백엔드 8030 |

**상태:** ✅ 시나리오는 문서대로 **수동·회귀 테스트** 권장.

---

## 한 줄 결론

**01~08을 gstack 순서대로 “진행”한 결과**, 제품 방향·API·엔진·LLM 격리·검토·QA 항목은 **문서와 구현이 대체로 정합**합니다. **남은 갭**은 (1) CEO 문서의 **공유/랜딩** 선택 기능, (2) 디자인 문서의 **shadcn/Tailwind** 풀스택, (3) **자동화 테스트**입니다.

---

*최종 갱신: 2026-03-28 · 대상 폴더: `saju_gstack/`만 · 순차 실행(00→08) 반영*
