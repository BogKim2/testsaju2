# Office Hours — CTO & Product Strategy

You are an expert startup CTO and product strategist.

I want to build a Korean SaaS web application that provides Four Pillars of Destiny (사주팔자) analysis.

## Tech Stack

- **Frontend:** React + Vite + TailwindCSS + shadcn/ui
- **Backend:** FastAPI (Python)
- **LLM:** LM Studio (Qwen3.5-9B, OpenAI-compatible API)

## Core Principle

- All saju calculations (원국, 오행, 십성) must be computed **deterministically in Python**.
- **LLM must NOT calculate saju.**
- LLM only receives structured JSON and generates Korean interpretation.

## Goal (MVP)

### User inputs

- name (optional)
- gender
- birth date (solar/lunar)
- birth time
- birth location

### Output

- 사주팔자 (천간/지지)
- 오행 분포
- 십성 분석
- 성격 / 연애 / 재물 / 직업 / 건강 해석
- 올해 운세 요약

## Task

Help me:

1. Define the product scope
2. Identify risks (especially hallucination, cultural accuracy)
3. Suggest MVP boundaries
4. Suggest differentiation vs existing fortune services

Be concise but strategic.
