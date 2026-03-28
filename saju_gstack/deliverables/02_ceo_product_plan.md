# 02 — CEO급 제품 플랜 (실행 결과)

> 원본 지시: `prompts/02_plan_ceo.md`  
> 전제: 한국어 사주 SaaS MVP, 2~3주 빌드 가능 범위

## MVP 현재 UI (`saju_gstack`)

아래는 **현재 코드**와 본 문서의 흐름을 맞추기 위한 단락이다. 스프린트 실행·CTO 문서와 함께 보려면 [00_gstack_sprint_execution.md](00_gstack_sprint_execution.md), [01_cto_strategy.md](01_cto_strategy.md), API·레이어·스키마 SSOT는 [03_engineering_architecture.md](03_engineering_architecture.md) 를 참고한다.

- **화면 구조:** 별도 라우팅 4분할이 아니라 **단일 페이지**에서 랜딩 한 줄 + 입력 폼 + (제출 후) 결과 스크롤. Share는 **텍스트 복사**로 최소 충족 가능, 공유 URL은 후속.
- **입력:** 양력 MVP. 프론트에서 `timezone`(IANA)·선택 `location`을 API로 전달할 수 있음. 음력 UI는 후속.
- **결과 IA:** 사주 표·오행(수치 + 간단 막대)·`year_fortune`(엔진 `target_year`)·LLM 마크다운 순. 연운 문구는 고정 “2025년”이 아니라 **엔진 연도** 기준.
- **요약:** LLM 마크다운의 「한줄 요약」을 결과 상단에서 발췌해 보여 줄 수 있음(선택 UI).

## 1. User Flow

1. **First visit** — 랜딩에서 가치 제안(사주는 코드로, 해석만 AI) + CTA “사주 보기”.
2. **Input** — 생년월일·음양·시간·성별·(선택) 이름·출생지(타임존) 입력 후 제출.
3. **Result** — 로딩 후 대시보드 한 화면에 요약·팔자·오행·십성·영역 해석·올해 요약 표시.
4. **Share (선택)** — 요약 텍스트 복사 또는 짧은 공유 링크(이미지는 MVP 생략 가능).

---

## 2. Core Screens (최대 4)

| # | 화면 | 역할 |
|---|------|------|
| 1 | Landing | 신뢰·프라이버시 한 줄, CTA |
| 2 | Input form | 단일 폼, 검증·에러 메시지 |
| 3 | Result dashboard | 스크롤 섹션으로 전부 소비 |
| 4 | Share (optional) | 복사 전용 또는 최소 정적 공유 URL |

회원·결제·히스토리는 MVP에서 제외.

---

## 3. Information Architecture (결과 페이지)

- **summary** — 한 줄 요약 + 일관된 톤(전문·부드러움).
- **saju chart** — 년·월·일·시 천간/지지 표 또는 카드 4칸.
- **five elements** — 목·화·토·금·수 개수/비율 시각화.
- **ten gods** — 십성 리스트 또는 핵심만 요약.
- **interpretation sections** — 성격 → 연애·재물·직업·건강(각 짧은 문단).
- **year fortune** — 해당 연도(`year_fortune.target_year`) 운세 요약(한 블록, 규칙 기반 JSON + 해석).

---

## 4. MVP Scope (엄격)

**포함:** 위 4화면 흐름, `POST /api/saju/analyze` 단일 호출, Python 결정적 사주 + JSON, LLM 한국어 해석, 기본 로딩/에러 UI.

**제외:** 회원가입, 결제, 저장, 궁합, 채팅, 신살 풀세트, 앱·푸시, 다국어.

**목표:** 동일 입력 → 동일 사주 JSON, 해석은 참고용으로 변동 가능하나 사실과 모순 없음.

---

## 5. Monetization (선택)

1. **Freemium** — 기본 팔자·오행·짧은 요약 무료, 영역별 상세·올해 심층은 유료(후속). MVP는 전 무료 + 가격 UI 플레이스홀더만 가능.
2. **B2B / API** — 해석 API만 연동(사주 계산은 계약에 따라 분리). 초기에는 문의 폼 수준.
