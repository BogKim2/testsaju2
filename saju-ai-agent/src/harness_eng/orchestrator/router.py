"""에이전트 이름 → 인스턴스 매핑."""

from typing import Any

from harness_eng.agents import (
    BOMAgent,
    DesignAgent,
    QualityAgent,
    RoutingAgent,
    SpecAgent,
)


class TaskRouter:
    """Orchestrator가 사용하는 에이전트 팩토리."""

    def __init__(self) -> None:
        self._design = DesignAgent()
        self._bom = BOMAgent()
        self._spec = SpecAgent()
        self._quality = QualityAgent()
        self._routing = RoutingAgent()

    def get_agent(self, name: str) -> Any:
        key = name.lower().strip()
        if key == "design":
            return self._design
        if key == "bom":
            return self._bom
        if key == "spec":
            return self._spec
        if key == "quality":
            return self._quality
        if key == "routing":
            return self._routing
        raise ValueError(f"unknown agent: {name}")
