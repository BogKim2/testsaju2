# Harness Engineering AI Agent — Architecture

## 핵심 원칙
> **"단순 LLM 호출이 아니라, 계획하고 기억하고 도구를 쓰는 진짜 AI 에이전트"**

---

## 이전 구조 (문제점)

```
Frontend
  → FastAPI
    → LLM
```

**문제점:**
- LLM이 무엇을 해야 할지 스스로 판단해야 함 → 불안정
- 이전 대화 내용을 기억하지 못함 → 매번 처음부터
- 여러 작업을 순서대로 처리하는 능력 없음
- 도구(파일 파서, DB, 계산기)를 사용하는 방법을 모름

---

## 현재 구조 (Orchestrator 포함)

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend (UI)                       │
│          사용자 입력 · 결과 표시 · 파일 업로드              │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTP Request
┌──────────────────────────▼──────────────────────────────┐
│                  FastAPI Gateway                         │
│          입력 유효성 검사 · 인증 · 라우팅                    │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│                   ORCHESTRATOR ◀◀◀ 핵심                  │
│                                                          │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────┐  │
│  │   Planner    │  │ Memory Manager│  │ Task Router  │  │
│  │ (계획 수립)   │  │  (기억 관리)   │  │ (작업 배분)   │  │
│  └──────┬───────┘  └───────┬───────┘  └──────┬───────┘  │
└─────────┼──────────────────┼─────────────────┼──────────┘
          │                  │                 │
          └──────────────────┼─────────────────┘
                             │ 작업 지시
┌────────────────────────────▼────────────────────────────┐
│                     Agent Pool                           │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │Design Agent │  │  BOM Agent   │  │Quality Agent  │  │
│  │ (설계 분석) │  │ (BOM 관리)   │  │ (품질 검사)   │  │
│  └─────────────┘  └──────────────┘  └───────────────┘  │
│  ┌─────────────┐  ┌──────────────┐                      │
│  │Routing Agent│  │  Spec Agent  │                      │
│  │(경로 최적화)│  │ (스펙 검증)  │                      │
│  └─────────────┘  └──────────────┘                      │
└────────────────────────────┬────────────────────────────┘
                             │ 도구 호출 / LLM 호출
          ┌──────────────────┼──────────────────────┐
          │                  │                       │
┌─────────▼──────┐  ┌────────▼────────┐  ┌──────────▼──────┐
│   Tool Layer   │  │  LLM Layer      │  │  Memory Store   │
│                │  │                 │  │                 │
│ - File Parser  │  │ LM Studio       │  │ - Short-term    │
│ - DB Query     │  │ (Qwen3.5-9B)    │  │   (대화 컨텍스트)│
│ - Calculator   │  │                 │  │ - Long-term     │
│ - Validator    │  │ localhost:1234  │  │   (설계 이력)   │
│ - DXF Reader   │  │                 │  │ - Vector DB     │
└────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## 계층별 역할

### Layer 1: FastAPI Gateway
- 사용자 요청 수신 및 응답 반환
- JWT 인증 및 권한 확인
- 입력 유효성 검사 (Pydantic)
- 요청을 Orchestrator에 전달

### Layer 2: Orchestrator (핵심)
세 가지 핵심 모듈로 구성:

| 모듈 | 역할 |
|------|------|
| **Planner** | 작업을 단계별 계획으로 분해 |
| **Memory Manager** | 단기/장기 기억 관리 |
| **Task Router** | 적합한 에이전트에 작업 배분 |

### Layer 3: Agent Pool
각 에이전트는 특정 도메인에 특화:

| 에이전트 | 담당 |
|---------|------|
| Design Agent | 하네스 설계도 분석 |
| BOM Agent | 부품 목록 관리 및 검증 |
| Quality Agent | 품질 기준 검사 |
| Routing Agent | 배선 경로 최적화 |
| Spec Agent | 전기 스펙 검증 |

### Layer 4: Tool Layer
에이전트가 사용하는 도구들:
- **File Parser**: DXF, PDF, Excel 파일 읽기
- **DB Query**: 부품 DB 조회
- **Calculator**: 전기 계산 (전압강하, 전류, 저항)
- **Validator**: 설계 규칙 검사
- **DXF Reader**: CAD 도면 파싱

---

## 요청 처리 흐름 (예시)

사용자: "이 하네스 설계 파일의 BOM을 검토하고 문제점을 찾아줘"

```
1. FastAPI  → 파일 업로드 수신, 유효성 검사
2. Orchestrator → 요청 분석
3. Planner → 계획 수립:
             Step 1: 파일 파싱
             Step 2: BOM 추출
             Step 3: 스펙 검증
             Step 4: 문제점 분석
             Step 5: 보고서 작성
4. Memory  → 이전 유사 작업 이력 조회
5. Router  → BOM Agent + Spec Agent 선택
6. BOM Agent → File Parser 도구로 BOM 추출
7. Spec Agent → Validator 도구로 규칙 검사
8. Orchestrator → 결과 취합
9. LLM → 최종 분석 보고서 작성
10. FastAPI → 사용자에게 응답 반환
```

---

## 기술 스택

| 항목 | 기술 |
|------|------|
| Frontend | Next.js 14 + **React + TypeScript** |
| UI 컴포넌트 | **shadcn/ui** (https://ui.shadcn.com/) |
| Styling | **Tailwind CSS** |
| Gateway | FastAPI (Python) |
| Orchestrator | Python (커스텀 구현) |
| Agent 프레임워크 | LangChain 또는 커스텀 |
| LLM | LM Studio + Qwen3.5-9B |
| Memory Store | Redis (단기) + SQLite (장기) |
| Vector DB | ChromaDB (문서 검색) |
| 파일 처리 | ezdxf, openpyxl, pdfplumber |

> 📄 프론트엔드 상세: `harness_eng/FRONTEND.md`  
> 📄 API 명세: `harness_eng/API.md`  
> 📄 환경 설정: `harness_eng/references/SETUP.md`

---

## 보안

| 항목 | 방식 |
|------|------|
| 인증 | JWT Bearer Token (Access 1h / Refresh 7d) |
| 통신 | HTTPS (배포 시 필수) |
| CORS | 허용 도메인 화이트리스트 |
| Rate Limit | 분당 60 요청 |
| LLM 데이터 | LM Studio 로컬 실행 → 외부 전송 없음 |
| 파일 검증 | 업로드 시 MIME 타입 + 확장자 이중 검사 |
