# 사주 분석 웹앱 (四柱分析 Web App)

사주(四柱) 8자를 자동 계산하고 LLM(Qwen3.5-9B)으로 한국어 해설을 생성하는 웹 애플리케이션입니다.

## 기술 스택

| 구분 | 기술 |
|------|------|
| Frontend | React 18 + Vite 6 + TypeScript + Tailwind CSS v3 + shadcn/ui |
| Backend | FastAPI (Python 3.11+) + JWT |
| LLM | LM Studio + Qwen3.5-9B (localhost:1234) |
| 차트 | Recharts |

## 실행 방법

### 빠른 시작
```bat
run.bat
```

### 수동 실행

**백엔드**
```bash
cd saju_project
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8020 --reload
```

**프론트엔드**
```bash
cd saju_project/frontend
npm install
npm run dev
```

## 접속 URL

- 프론트엔드: http://localhost:5174
- 백엔드 API: http://localhost:8020
- API 문서: http://localhost:8020/docs

## 로그인 정보

- Email: `demo@saju.com`
- Password: `saju1234`

## LM Studio 설정

1. LM Studio를 실행하고 Qwen3.5-9B 모델을 로드합니다.
2. Local Server를 시작합니다 (기본 포트: 1234).
3. LLM 없이도 기본 사주 계산 결과는 확인할 수 있습니다.

## 주요 기능

- **사주 8자 계산**: 양력 생년월일시 → 천간/지지 자동 산출
- **오행 분석**: 木火土金水 분포 레이더 차트
- **대운/세운**: 10년 단위 대운 흐름 타임라인
- **AI 해설**: LLM 기반 한국어 운세 해설
- **분석 이력**: 과거 분석 결과 조회
