# 사주 분석 웹앱 — 설계 문서

## 프로젝트 구조

```
saju_project/
├── README.md
├── PLAN.md
├── run.bat
├── kill.bat
├── requirements.txt
├── backend/
│   ├── main.py               # uvicorn 진입점 (port 8020)
│   └── saju/
│       ├── __init__.py
│       ├── api.py            # FastAPI (CORS, JWT, endpoints)
│       ├── auth/
│       │   ├── __init__.py
│       │   ├── jwt_utils.py
│       │   └── deps.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── saju_data.py  # 천간/지지/오행 상수
│       │   ├── calculator.py # 사주 8자 계산 엔진
│       │   └── daewoon.py    # 대운/세운 계산
│       ├── llm/
│       │   ├── __init__.py
│       │   └── llm_client.py # LM Studio 연동
│       └── session_store.py  # 인메모리 세션
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.ts
    ├── tsconfig.json
    ├── index.html
    └── src/
        ├── App.tsx
        ├── main.tsx
        ├── index.css
        ├── types/saju.ts
        ├── lib/api.ts
        ├── lib/auth.ts
        ├── lib/utils.ts
        ├── components/ui/    # shadcn/ui 공식 컴포넌트
        ├── components/saju/
        │   ├── SajuInputForm.tsx
        │   ├── Pillars.tsx
        │   ├── OhaengChart.tsx
        │   └── DaewoonBar.tsx
        └── pages/
            ├── LoginPage.tsx
            ├── HomePage.tsx
            ├── AnalyzePage.tsx
            ├── ResultPage.tsx
            └── HistoryPage.tsx
```

## 데이터 흐름

```
사용자 입력(이름/성별/생년월일시)
  → POST /saju/analyze
  → session_id 즉시 반환
  → 백그라운드: calculator.py → llm_client.py
  → GET /saju/{id}/status 폴링 (0~100%)
  → GET /saju/{id}/result 결과 조회
```

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/auth/login` | JWT 발급 |
| POST | `/saju/analyze` | 분석 시작 → session_id 반환 |
| GET | `/saju/{id}/status` | 진행 상태 폴링 |
| GET | `/saju/{id}/result` | 전체 결과 |
| GET | `/history` | 이력 목록 |

## 사주 계산 원리

### 연주 (年柱)
- 60갑자 기준: 甲子년 = 1984
- 연간: (year - 4) % 10 → 천간
- 연지: (year - 4) % 12 → 지지

### 월주 (月柱)
- 절기(24절기) 기준으로 월 결정
- 월간: (연간index * 2 + month) % 10

### 일주 (日柱)
- 기준일: 1900-01-01 = 甲子일
- 경과 일수 % 60 → 60갑자

### 시주 (時柱)
- 시지: (hour + 1) // 2 % 12
- 시간: (일간index * 2 + 시지index) % 10

### 대운
- 양남음녀: 순행 / 음남양녀: 역행
- 절기까지 일수 ÷ 3 = 대운 시작 나이
