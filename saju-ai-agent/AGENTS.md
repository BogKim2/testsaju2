# Agents — 에이전트 개요

> 상세 내용은 `harness_eng/AGENTS.md` 및 각 에이전트 문서 참조

## 에이전트 목록

| 에이전트 | 파일 | 핵심 역할 |
|---------|------|---------|
| Design Agent | `harness_eng/agents/design_agent.md` | DXF 도면 구조 분석 |
| BOM Agent | `harness_eng/agents/bom_agent.md` | 부품 목록 검증 |
| Spec Agent | `harness_eng/agents/spec_agent.md` | 전기 스펙 계산 |
| Quality Agent | `harness_eng/agents/quality_agent.md` | 품질 종합 판정 |
| Routing Agent | `harness_eng/agents/routing_agent.md` | 배선 경로 최적화 |

## 에이전트의 3대 핵심 역량

```
각 에이전트는 Orchestrator의 지휘 아래:

1. Planning   → 자신이 맡은 작업을 단계로 분해
2. Memory     → 과거 분석 이력과 표준 규격 참조
3. Tool       → 파일파서/DB/계산기를 활용하여 실제 작업 수행
```
