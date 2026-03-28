# Plan — Engineering / Architecture

You are a senior software architect.

Design a monorepo for:

- **frontend** (React + Vite)
- **backend** (FastAPI)

## Requirements

### Backend

- Deterministic saju calculation module
- API endpoint: `POST /api/saju/analyze`
- LLM integration via LM Studio (OpenAI-compatible)

### Frontend

- Form input
- Result visualization
- API integration

## Output

- Folder structure
- API schema (request/response JSON)
- Data flow (step-by-step)
- Separation of concerns (**VERY IMPORTANT**)

## Constraints

- LLM never calculates saju
- Backend returns structured JSON + LLM interpretation

Be explicit and implementation-ready.
