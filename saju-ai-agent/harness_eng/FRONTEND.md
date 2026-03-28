# Frontend — 프론트엔드 기술 스택 및 설계

## 기술 스택 (확정)

| 항목 | 기술 | 비고 |
|------|------|------|
| **Framework** | React 18 | SPA (Single Page App) |
| **Build Tool** | Vite 6 | 빠른 HMR, 가벼운 번들 |
| **Language** | TypeScript | 전체 코드 `.tsx` / `.ts` |
| **Styling** | Tailwind CSS v3 | 유틸리티 퍼스트 CSS |
| **UI 컴포넌트** | shadcn/ui 스타일 | 직접 구현 (Radix UI 기반) |
| **라우팅** | React Router v6 | SPA 클라이언트 라우팅 |
| **HTTP Client** | fetch API (내장) | axios 사용 안 함 |
| **차트** | Recharts | 데이터 시각화 |
| **아이콘** | Lucide React | |
| **토스트** | Sonner | 알림 UI |

> **Next.js를 사용하지 않는 이유**: 개발 환경(exFAT 드라이브)에서 SWC 바이너리 및 심볼릭 링크 관련 설치 오류 발생. React+Vite로 동일한 기능을 더 가볍게 구현.

---

## 설치 명령어

```bash
# 1. 프로젝트 생성 (Vite + React + TypeScript)
npm create vite@latest frontend -- --template react-ts
cd frontend

# 2. Tailwind CSS 설치
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# 3. 라우팅 및 UI 패키지 설치
npm install react-router-dom
npm install lucide-react sonner recharts
npm install clsx tailwind-merge class-variance-authority
npm install @radix-ui/react-slot @radix-ui/react-label
npm install @radix-ui/react-tabs @radix-ui/react-dialog
npm install @radix-ui/react-separator @radix-ui/react-progress @radix-ui/react-select

# 4. 개발 서버 실행
npm run dev
# → http://localhost:5173
```

---

## 페이지 구조 (React Router)

```
/                    ← 메인 (파일 업로드 + 분석 시작)
/login               ← 로그인
/analyze             ← 분석 진행 화면 (에이전트 상태)
/result/:id          ← 분석 결과 종합
/result/:id/design   ← 설계 분석 결과
/result/:id/bom      ← BOM 검증 결과
/result/:id/spec     ← 전기 스펙 결과
/result/:id/quality  ← 품질 검사 결과
/result/:id/routing  ← 경로 최적화 결과
/history             ← 과거 분석 이력
```

---

## 컴포넌트 설계

```
src/
├── main.tsx                ← 진입점
├── App.tsx                 ← Router 설정
├── index.css               ← Tailwind + CSS 변수
│
├── types/
│   └── harness.ts          ← TypeScript 타입 정의
│
├── lib/
│   ├── utils.ts            ← cn() 유틸리티
│   ├── api.ts              ← 백엔드 API 함수
│   └── auth.ts             ← JWT 토큰 관리
│
├── components/
│   ├── ui/                 ← shadcn/ui 스타일 컴포넌트
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   ├── label.tsx
│   │   ├── badge.tsx
│   │   ├── tabs.tsx
│   │   ├── progress.tsx
│   │   ├── separator.tsx
│   │   ├── alert.tsx
│   │   ├── table.tsx
│   │   └── sonner.tsx
│   │
│   ├── harness/            ← 하네스 도메인 전용 컴포넌트
│   │   ├── FileUploadCard.tsx
│   │   ├── AgentStatusBar.tsx
│   │   ├── QualityBadge.tsx
│   │   ├── IssueTable.tsx
│   │   ├── BomTable.tsx
│   │   ├── SpecCard.tsx
│   │   └── ResultTabs.tsx
│   │
│   └── layout/
│       └── Header.tsx
│
└── pages/
    ├── LoginPage.tsx
    ├── HomePage.tsx
    ├── AnalyzePage.tsx
    ├── ResultPage.tsx
    ├── HistoryPage.tsx
    └── result/
        ├── DesignPage.tsx
        ├── BomPage.tsx
        ├── SpecPage.tsx
        ├── QualityPage.tsx
        └── RoutingPage.tsx
```

---

## TypeScript 타입 정의 (types/harness.ts)

```typescript
export type AgentName = "design" | "bom" | "spec" | "quality" | "routing";
export type AgentStatus = "pending" | "running" | "done" | "error";
export type QualityVerdict = "PASS" | "CONDITIONAL_PASS" | "FAIL";
export type IssueSeverity = "FAIL" | "WARNING" | "INFO";

export interface AgentProgress {
  name: AgentName;
  status: AgentStatus;
  started_at: string | null;
  completed_at: string | null;
}

export interface QualityIssue {
  id: string;
  severity: IssueSeverity;
  item: string;
  detail: string;
  action: string;
}

export interface QualityResult {
  overallResult: QualityVerdict;
  passRate: number;
  issues: QualityIssue[];
}
```

---

## API 연동 (lib/api.ts)

```typescript
const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8010";

export async function analyzeHarness(file: File, projectName: string) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("project_name", projectName);
  const res = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: { Authorization: `Bearer ${getToken()}` },
    body: formData,
  });
  if (!res.ok) throw new Error("분석 요청 실패");
  return res.json() as Promise<{ session_id: string }>;
}
```

---

## 환경변수 (.env)

```bash
# 백엔드 FastAPI 서버 주소
VITE_API_URL=http://localhost:8010
```
