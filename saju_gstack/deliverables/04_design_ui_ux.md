# 04 — 디자인 시스템 · UI/UX (실행 결과)

> 원본 지시: `prompts/04_design.md`  
> 도구(목표): shadcn/ui, TailwindCSS

## MVP 현재 구현 (`saju_gstack`)

아래 **실제 화면**은 [frontend/src/App.tsx](../frontend/src/App.tsx) · [frontend/src/index.css](../frontend/src/index.css) 기준이다. 제품 흐름·IA는 [02_ceo_product_plan.md](02_ceo_product_plan.md), 레이아웃·API는 [03_engineering_architecture.md](03_engineering_architecture.md), 스프린트 로그는 [00_gstack_sprint_execution.md](00_gstack_sprint_execution.md) 와 교차 참고한다.

- **스택:** Tailwind/shadcn **미도입**. 전역은 `index.css`(배경·본문 색·폰트), 컴포넌트는 **React 인라인 스타일** 위주.
- **레이아웃:** 단일 페이지, **탭 없이** 세로 스크롤로 요약 → 사주 표 → 오행 막대 → 연운 → 해석 순.
- **연운 블록:** 고정 “2025년”이 아니라 API `year_fortune.target_year` 및 규칙 기반 연주 표시.
- **공유:** “요약·해석 복사” 버튼(`navigator.clipboard`). 공유 URL은 후속.

## 스타일 방향

- **calm, minimal, premium** — 여백 넉넉, 정보 위계 명확.
- **dark mode first** — 기본 테마는 다크.
- **slightly mystical, NOT cheesy** — 은은한 테두리·그라데이션만, 과한 보라/금색/이모지 남발 금지.

## 디자인 시스템

### 컬러 (다크 퍼스트)

- 배경: `#0c0e12` ~ `#12151c` (단색 또는 아주 약한 그라데이션).
- 카드/표면: `#161b24`, 테두리 `border-white/10`.
- 악센트: 청회색·슬레이트 계열 `#94a3b8` ~ `#cbd5e1` (고급스럽게 제한적으로).
- 오행(목·화·토·금·수): **낮은 채도** 팔레트로 막대/범례만 구분 (접근성 대비 색 + 라벨). MVP는 [App.tsx](../frontend/src/App.tsx) 의 `ElementBars` 에서 색·라벨 병기.

### 타이포그래피

- **MVP:** `body`에 `system-ui`, `"Segoe UI"`, sans-serif ([index.css](../frontend/src/index.css)).
- **목표(차기):** 한글 Pretendard 또는 Noto Sans KR, Tailwind 유틸(`text-lg` ~ `text-2xl`, `font-semibold`, `text-slate-300` 등).
- 간지·숫자: 목표는 `tabular-nums` 표 정렬. MVP는 표·막대에 숫자·한글 병기.

## 컴포넌트 정의

| 컴포넌트 | 용도 | shadcn 참고(목표) | 현재 (`App.tsx`) |
|----------|------|-------------------|------------------|
| Input form | 이름(선택), 성별, 생일, 시각, 타임존, 출생지(선택) | Form, Input, Select, RadioGroup, Button | 단일 `<form>` 인라인 입력. 양력 고정(`calendar: solar`). |
| Result 영역 | 요약·팔자·오행·연운·해석 | Card, Tabs, Separator | 스크롤 한 열. 결과 후 폼은 접고 “입력 수정”으로 재노출. |
| Five elements viz | 5요소 비율 | Progress 또는 custom bar | `ElementBars`: 비율 % 막대 + 목/화/토/금/수 라벨 |
| Summary highlight | 한 줄 요약 상단 강조 | Alert 또는 상단 Card + Badge | 마크다운 `### 1. 한줄 요약` 발췌 카드 |
| Year fortune | 올해 연주·규칙 블록 | (문서용 카드) | `year_fortune` 카드 + `meta.datetime_policy` 선택 표시 |
| Share | 텍스트 복사 | Button | “요약·해석 복사” |

## 레이아웃 와이어프레임 (텍스트, MVP)

```
[Header: 제목 + 부제 — 다크 고정]

[Landing / Input]
  히어로 제목 1줄 + 부제 (결과 없거나 입력 펼침 시)
  또는 [분석 완료 · 입력 수정] 바 (결과 있고 폼 접힘 시)

[Input 폼]
  이름(선택) | 성별 | 생년월일 | 시각 | 타임존(IANA) | 출생지(선택)
  [사주 보기 / POST 제출]
  [검증 에러]

[Result — 스크롤 한 열, 탭 없음]
  ┌ 한 줄 요약 (해석에서 발췌) ────┐
  └──────────────────────────────┘
  일간·십성 한 줄
  사주표: 4행(연월일시) × 천간/지지
  오행: 5막대 + 비율 %
  해당 연도(target_year) 연운 블록 (규칙 기반 JSON 반영)
  경고·datetime_policy (있을 때)
  해석(LLM 마크다운)
  [요약·해석 복사]
```

## 사용성

- MVP는 **한 열 스크롤**로 표(팔자) → 오행 막대 → 연운 → 글(해석) 순서를 유지한다. **Tabs** 로 보조하는 것은 후속(목표 UX).
- 로딩 중에는 버튼 비활성·문구 “분석 중…” (스켈레톤/스피너는 08 UX 시나리오와 연계해 확장 가능).
