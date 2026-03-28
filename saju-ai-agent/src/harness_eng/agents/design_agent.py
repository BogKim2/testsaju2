"""Design Agent — 도면 구조 분석 (스텁 + 최소 구조)."""

import time
from typing import Any

from harness_eng.agents.base_agent import BaseAgent


class DesignAgent(BaseAgent):
    """DXF/PDF 설계 구조 분석 에이전트."""

    def __init__(self) -> None:
        self._status = "idle"

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        # 파일 경로가 있으면 통과 (실제 DXF 파싱은 추후)
        return "file_path" in input_data and bool(input_data["file_path"])

    def get_status(self) -> str:
        return self._status

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """CONTRACTS.md Design Agent 출력 형식에 맞춘 결과."""
        self._status = "running"
        start = time.perf_counter()
        file_path = str(input_data.get("file_path", ""))

        # 최소 스텁 결과 — 실제로는 DXFParser 사용
        result: dict[str, Any] = {
            "summary": {
                "total_connectors": 2,
                "total_wires": 4,
                "total_splices": 0,
                "circuit_count": 2,
            },
            "connectors": [
                {
                    "id": "J1",
                    "type": "12핀 방수",
                    "location": "엔진룸 좌측",
                    "pins": [
                        {"pin": 1, "circuit": "IGN", "color": "R"},
                        {"pin": 2, "circuit": "GND", "color": "B"},
                    ],
                }
            ],
            "bundles": [
                {
                    "id": "B-001",
                    "wires": ["W-001", "W-002"],
                    "diameter": 12.5,
                    "length": 1200.0,
                }
            ],
            "drc_issues": [
                {"type": "WARNING", "description": f"stub: analyzed {file_path}"}
            ],
        }
        duration_ms = int((time.perf_counter() - start) * 1000)
        self._status = "done"
        return {
            "agent": "design_agent",
            "status": "done",
            "result": result,
            "errors": [],
            "duration_ms": duration_ms,
        }
