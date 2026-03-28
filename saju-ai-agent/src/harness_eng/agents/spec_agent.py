"""Spec Agent — 전기 스펙 계산."""

import time
from typing import Any

from harness_eng.agents.base_agent import BaseAgent
from harness_eng.tools.calculators import calc_voltage_drop


class SpecAgent(BaseAgent):
    """전압강하 등 전기 계산 에이전트."""

    def __init__(self) -> None:
        self._status = "idle"

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        circuits = input_data.get("circuits")
        return isinstance(circuits, list) and len(circuits) > 0

    def get_status(self) -> str:
        return self._status

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """circuits 리스트에 대해 전압강하 계산."""
        self._status = "running"
        start = time.perf_counter()
        circuits_in = input_data.get("circuits", [])
        out_circuits: list[dict[str, Any]] = []
        for c in circuits_in:
            cid = str(c.get("circuit_id", "unknown"))
            cur = float(c.get("current", 1.0))
            length = float(c.get("length", 1.0))
            area = float(c.get("cross_section", 1.0))
            mat = str(c.get("wire_material", "copper"))
            vd = calc_voltage_drop(cur, length, area, mat)
            st = "PASS" if vd["is_acceptable"] else "FAIL"
            out_circuits.append(
                {
                    "circuit_id": cid,
                    "voltage_drop": float(vd["voltage_drop"]),
                    "resistance": float(vd["resistance"]),
                    "status": st,
                    "message": str(vd.get("warning", "")),
                }
            )
        result: dict[str, Any] = {
            "circuits": out_circuits,
            "fuse_checks": [],
        }
        duration_ms = int((time.perf_counter() - start) * 1000)
        self._status = "done"
        return {
            "agent": "spec_agent",
            "status": "done",
            "result": result,
            "errors": [],
            "duration_ms": duration_ms,
        }
