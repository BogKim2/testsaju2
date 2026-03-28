"""실행할 에이전트 순서 결정 (PLANNING.md)."""

from typing import Any


DEFAULT_AGENTS = ["design", "bom", "spec", "routing", "quality"]


def parse_agent_list(agents_param: str | None) -> list[str]:
    """쉼표 구분 문자열을 리스트로."""
    if not agents_param or not agents_param.strip():
        return list(DEFAULT_AGENTS)
    parts = [p.strip().lower() for p in agents_param.split(",") if p.strip()]
    order: list[str] = []
    for name in parts:
        if name in DEFAULT_AGENTS and name not in order:
            order.append(name)
    return order if order else list(DEFAULT_AGENTS)


def build_plan(user_request_meta: dict[str, Any]) -> dict[str, Any]:
    """요청 메타로부터 Plan ID와 스텝 목록 생성."""
    agents = parse_agent_list(str(user_request_meta.get("agents", "")))
    return {
        "plan_id": f"plan-{user_request_meta.get('session_hint', 'local')}",
        "agents": agents,
        "status": "ready",
    }
