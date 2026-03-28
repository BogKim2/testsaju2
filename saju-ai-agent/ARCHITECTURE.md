# Architecture — 시스템 구조 개요

> 상세 구조는 `harness_eng/ARCHITECTURE.md` 참조

## Before vs After

```
❌ 이전 (약점):
  Frontend → FastAPI → LLM
  - 계획 없음, 기억 없음, 도구 없음

✅ 현재 (개선):
  Frontend
    → FastAPI
      → Orchestrator
          ├── Planner   (계획 수립)
          ├── Memory    (기억 관리)
          └── Router    (에이전트 배분)
              → Agent Pool
                  ├── Design Agent
                  ├── BOM Agent
                  ├── Spec Agent
                  ├── Quality Agent
                  └── Routing Agent
                      → Tools + LLM
```

## Orchestrator의 3대 책임

| 책임 | 설명 |
|------|------|
| **Planning** | 복잡한 요청을 단계별 계획으로 분해 |
| **Memory** | 단기(Redis) + 장기(SQLite) + 벡터(ChromaDB) 기억 |
| **Tool Control** | 파일파서, DB조회, 계산기, 검증기 제어 |

→ 상세: `harness_eng/ORCHESTRATOR.md`
