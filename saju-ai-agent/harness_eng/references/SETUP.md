# SETUP — 개발 환경 및 배포 설정

## Python 환경 설정 (uv 권장)

`uv`는 pip보다 10~100배 빠른 Python 패키지 매니저입니다.

```bash
# uv 설치
pip install uv

# 프로젝트 초기화
uv init backend
cd backend

# 패키지 설치
uv add fastapi uvicorn pydantic ezdxf openpyxl pdfplumber

# 가상환경 활성화
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate

# 서버 실행
uv run uvicorn main:app --reload --port 8000

# requirements.txt 생성 (배포용)
uv pip freeze > requirements.txt
```

---

## LM Studio 설정

```bash
# 1. LM Studio 다운로드: https://lmstudio.ai/
# 2. qwen/qwen3-9b 모델 다운로드
# 3. Local Server 탭 → 서버 시작 (포트 1234)

# 연결 확인
curl http://localhost:1234/v1/models
```

환경 변수:
```
LM_STUDIO_URL=http://localhost:1234/v1/chat/completions
```

---

## 클라우드 배포 (Nixpacks)

```toml
# nixpacks.toml

[phases.setup]
nixPkgs = ["python311"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[phases.build]
cmds = []

[start]
cmd = "uvicorn main:app --host 0.0.0.0 --port $PORT"
```

> ⚠️ LM Studio는 로컬 전용.  
> 클라우드 배포 시 `LM_STUDIO_URL`을 OpenAI 또는 다른 API로 교체.

```
# 클라우드용 환경 변수
LLM_API_URL=https://api.openai.com/v1/chat/completions
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
```

---

## 전체 로컬 실행 순서

```bash
# 터미널 1: LM Studio 서버 (GUI로 시작)

# 터미널 2: FastAPI 백엔드
cd backend
uvicorn main:app --reload --port 8000

# 터미널 3: Next.js 프론트엔드
cd frontend
npm run dev

# 확인
# API: http://localhost:8000/docs
# UI:  http://localhost:3000
```
