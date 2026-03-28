"""BOM Agent — 부품 목록 검증 (스텁)."""

import time
from typing import Any

from harness_eng.agents.base_agent import BaseAgent


class BOMAgent(BaseAgent):
    """BOM 추출 및 검증 에이전트."""

    def __init__(self) -> None:
        self._status = "idle"

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        return "file_path" in input_data

    def get_status(self) -> str:
        return self._status

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """CONTRACTS — bom + summary."""
        self._status = "running"
        start = time.perf_counter()
        result: dict[str, Any] = {
            "bom": [
                {
                    "line_no": 1,
                    "part_no": "C-001",
                    "name": "stub connector",
                    "qty": 4,
                    "unit_price": 1200,
                    "total_price": 4800,
                    "spec": {"max_current": 10.0, "waterproof": True},
                    "status": "정상",
                    "error": None,
                }
            ],
            "summary": {
                "total_items": 1,
                "total_cost": 4800,
                "errors": 0,
                "warnings": 0,
            },
        }
        duration_ms = int((time.perf_counter() - start) * 1000)
        self._status = "done"
        return {
            "agent": "bom_agent",
            "status": "done",
            "result": result,
            "errors": [],
            "duration_ms": duration_ms,
        }
