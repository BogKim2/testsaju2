# saju_gstack

gstack 스타일 **프롬프트·산출물**(`prompts/`, `deliverables/`)과, **이 폴더 안에서만** 동작하는 **실행 가능한 MVP**(백엔드 + 프론트)를 둡니다.

## 실행 (MVP)

### 1) 백엔드 (FastAPI, 포트 8030)

```text
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8030 --reload
```

Windows: `backend\run_server.bat`

### 2) LM Studio (선택)

로컬에서 OpenAI 호환 API(`http://localhost:1234`)를 켜 두면 해석이 풍부해집니다. 없으면 엔진 JSON 기반 기본 해설만 반환합니다.

### 3) 프론트엔드 (Vite, 포트 5175)

```text
cd frontend
npm install
npm run dev
```

브라우저에서 `http://localhost:5175` — API는 Vite 프록시로 `/api` → `8030`입니다.

## 폴더 구조

| 경로 | 설명 |
|------|------|
| `prompts/` | AI 지시문 (01~08) |
| `deliverables/` | 산출물 문서 (01~08) |
| `schemas/` | API JSON 스키마 |
| `examples/` | 샘플 JSON |
| `backend/` | FastAPI, 결정적 사주 + `POST /api/saju/analyze` |
| `frontend/` | React + Vite 최소 UI |
| `REVIEW.md` | 구현 검토 요약 |

## gstack (Garry Tan) 전역 설치

공식 저장소: [github.com/garrytan/gstack](https://github.com/garrytan/gstack)

- **bun**이 필요합니다. 클론 후 디렉터리에서 `./setup` 실행 (Claude Code 스킬 등록).
- Windows: Git Bash 등에서 `~/.claude/skills/gstack` 경로로 클론한 뒤 `./setup`을 권장합니다.

이 레포의 **앱 코드는 `saju_gstack/backend`·`frontend`만 사용**하면 되며, `saju_project`와는 별개입니다.
