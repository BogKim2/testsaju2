# Harness Engineering AI Agent

하네스 설계를 AI가 자동으로 분석하고 설계하는  시스템입니다.  
**Orchestrator 기반 멀티 에이전트 아키텍처**로 구축되었습니다.

---

## 프로젝트 정보

| 항목 | 내용 |
|------|------|
| **GitHub** | https://github.com/BogKim2/testsaju2 |
| **Branch 전략** | `main` (배포) / `dev` (개발) / `feature/*` (기능) |
| **클론** | `git clone https://github.com/BogKim2/testsaju2.git` |

---

## 핵심 차별점

| 기존 방식 | 이 시스템 |
|---------|---------|
| Frontend → LLM | Frontend → FastAPI → **Orchestrator** → Agent → LLM |
| LLM이 모든 것 판단 | Planner가 계획 수립 후 전문 에이전트에 배분 |
| 기억 없음 | Memory Manager가 단기/장기 기억 관리 |
| 단일 작업 | 여러 에이전트 병렬 처리 |
| 도구 사용 불가 | Tool Controller로 파일/DB/계산기 제어 |

---

## 시스템 구조

```
Frontend (Next.js)
   ↓
FastAPI Gateway
   ↓
Orchestrator  ← Planning + Memory + Task Router
   ↓
Agent Pool
   ├── Design Agent    (도면 구조 분석)
   ├── BOM Agent       (부품 목록 검증)
   ├── Spec Agent      (전기 스펙 계산)
   ├── Quality Agent   (품질 종합 판정)
   └── Routing Agent   (배선 경로 최적화)
   ↓
Tool Layer + LLM (LM Studio / Qwen3.5-9B)
```

---

## 문서 구조

```
saju-ai-agent/
├── README.md              ← 이 파일
├── AGENTS.md              ← 에이전트 개요 (루트)
├── ARCHITECTURE.md        ← 전체 구조 다이어그램
├── PLANS.md               ← 개발 계획
│
└── harness_eng/           ← 하네스 엔지니어링 상세 문서
    ├── ARCHITECTURE.md    ← 상세 아키텍처 (Orchestrator 포함)
    ├── ORCHESTRATOR.md    ← Orchestrator 설계 (Planning/Memory/Routing)
    ├── MEMORY.md          ← 단기/장기 메모리 시스템
    ├── PLANNING.md        ← 계획 수립 시스템
    ├── TOOLS.md           ← 도구 제어 시스템
    ├── AGENTS.md          ← 에이전트 목록 및 시나리오
    └── agents/
        ├── design_agent.md   ← 설계 분석 에이전트
        ├── bom_agent.md      ← BOM 관리 에이전트
        ├── spec_agent.md     ← 전기 스펙 에이전트
        ├── quality_agent.md  ← 품질 검사 에이전트
        └── routing_agent.md  ← 경로 최적화 에이전트
```

---

## 주요 기능

### 1. 신규 설계 전체 검토
- DXF 도면 업로드 → 5개 에이전트 자동 분석 → 종합 보고서

### 2. BOM 검증
- Excel BOM 업로드 → 부품번호 검증 → 스펙 대조 → 오류 목록

### 3. 전기 스펙 계산
- 회로 정보 입력 → 전압강하/와이어 사이징/퓨즈 계산 → 결과 보고

### 4. 배선 경로 최적화
- 도면 분석 → 간섭 위험 탐지 → 최적 경로 제안 → 원가 절감 추정

### 5. 품질 종합 판정
- 20개 체크리스트 자동 검사 → PASS / CONDITIONAL PASS / FAIL 판정

---

## 기술 스택

| Layer | 기술 |
|-------|------|
| Frontend | Next.js 14 + React + TypeScript |
| UI 컴포넌트 | shadcn/ui (https://ui.shadcn.com/) |
| Styling | Tailwind CSS |
| Gateway | FastAPI (Python) |
| Orchestrator | Python 커스텀 |
| Memory | Redis + SQLite + ChromaDB |
| LLM | LM Studio + Qwen3.5-9B |
| 파일 처리 | ezdxf, openpyxl, pdfplumber |
