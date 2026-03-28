"""Orchestrator — Planner + Memory + Router + LLMClient."""

# Orchestrator만 에이전트 순서와 LLM 호출을 담당합니다 (CONSTITUTION A-02, A-03).

import os
from typing import Any

from harness_eng.exceptions import LLMConnectionError
from harness_eng.llm.llm_client import LLMClient
from harness_eng.orchestrator.memory_manager import MemoryManager
from harness_eng.orchestrator.planner import build_plan
from harness_eng.orchestrator.router import TaskRouter


def _circuits_from_context(design_result: dict[str, Any]) -> list[dict[str, Any]]:
    """Design 결과에서 Spec Agent용 회로 목록 생성."""
    bundles = design_result.get("bundles", [])
    out: list[dict[str, Any]] = []
    for i, b in enumerate(bundles):
        length_mm = float(b.get("length", 1000.0))
        out.append(
            {
                "circuit_id": f"CIR-{i + 1}",
                "current": 8.5,
                "length": length_mm / 1000.0,
                "cross_section": 1.25,
                "wire_material": "copper",
            }
        )
    if not out:
        out.append(
            {
                "circuit_id": "CIR-1",
                "current": 5.0,
                "length": 2.0,
                "cross_section": 1.0,
                "wire_material": "copper",
            }
        )
    return out


class Orchestrator:
    """에이전트 실행 순서만 결정 — 에이전트끼리 직접 호출 금지 (Rule A-03)."""

    def __init__(self) -> None:
        self.memory = MemoryManager()
        self.router = TaskRouter()
        self.llm = LLMClient()

    def create_session(
        self,
        project_name: str,
        version: str,
        file_path: str,
        agents_param: str | None,
    ) -> str:
        """세션만 생성하고 session_id 반환 (비동기 실행 전 호출)."""
        meta: dict[str, Any] = {
            "agents": agents_param or "",
            "session_hint": "run",
        }
        plan = build_plan(meta)
        order = list(plan["agents"])
        session = self.memory.create_session(project_name, version, file_path, order)
        return session.session_id

    def run_pipeline(self, session_id: str) -> None:
        """백그라운드에서 에이전트를 순서대로 실행 — API가 background task로 호출."""
        st = self.memory.get(session_id)
        if st is None:
            return

        file_path = st.file_path
        order = st.agent_order

        design_out: dict[str, Any] | None = None
        bom_out: dict[str, Any] | None = None
        spec_out: dict[str, Any] | None = None
        routing_out: dict[str, Any] | None = None
        quality_out: dict[str, Any] | None = None

        for name in order:
            # 실행 시작 상태 기록
            self.memory.set_agent_running(session_id, name)
            agent = self.router.get_agent(name)
            try:
                if name == "design":
                    design_out = agent.run({"file_path": file_path})
                    self.memory.save_agent_output(session_id, "design", design_out)
                elif name == "bom":
                    payload = {
                        "source": "dxf",
                        "file_path": file_path,
                        "design_data": design_out["result"] if design_out else {},
                    }
                    bom_out = agent.run(payload)
                    self.memory.save_agent_output(session_id, "bom", bom_out)
                elif name == "spec":
                    dr = design_out["result"] if design_out else {}
                    payload = {"circuits": _circuits_from_context(dr)}
                    spec_out = agent.run(payload)
                    self.memory.save_agent_output(session_id, "spec", spec_out)
                elif name == "routing":
                    dr = design_out["result"] if design_out else {}
                    payload = {"bundles": dr.get("bundles", [])}
                    routing_out = agent.run(payload)
                    self.memory.save_agent_output(session_id, "routing", routing_out)
                elif name == "quality":
                    payload = {
                        "design_result": design_out["result"] if design_out else {},
                        "bom_result": bom_out["result"] if bom_out else {},
                        "spec_result": spec_out["result"] if spec_out else {},
                    }
                    quality_out = agent.run(payload)
                    self.memory.save_agent_output(session_id, "quality", quality_out)
            except Exception as exc:  # noqa: BLE001
                # 에이전트 오류 — 기록 후 계속 진행
                self.memory.save_agent_output(
                    session_id, name,
                    {"agent": name, "status": "error", "result": {}, "errors": [str(exc)], "duration_ms": 0},
                )

        # 요약 생성
        summary_prompt = self._build_summary_prompt(
            st.project_name, design_out, bom_out, spec_out, routing_out, quality_out
        )
        if os.environ.get("HARNESS_SKIP_LLM") == "1":
            summary = "[LLM skipped] set HARNESS_SKIP_LLM=0 to call LM Studio."
        else:
            try:
                summary = self.llm.summarize(summary_prompt)
            except LLMConnectionError:
                summary = "[LLM unavailable] analysis finished with rule-based agents only."

        self.memory.set_summary(session_id, summary)
        self.memory.set_session_done(session_id)

    def _build_summary_prompt(
        self,
        project: str,
        design_out: dict[str, Any] | None,
        bom_out: dict[str, Any] | None,
        spec_out: dict[str, Any] | None,
        routing_out: dict[str, Any] | None,
        quality_out: dict[str, Any] | None,
    ) -> str:
        lines = [
            f"Project: {project}",
            "Summarize harness review in 3 short bullet points in Korean.",
            f"Design summary keys: {list((design_out or {}).get('result', {}).keys())}",
            f"BOM items: {len((bom_out or {}).get('result', {}).get('bom', []))}",
            f"Spec circuits: {len((spec_out or {}).get('result', {}).get('circuits', []))}",
            f"Routing risks: {len((routing_out or {}).get('result', {}).get('interference_risks', []))}",
            f"Quality verdict: {(quality_out or {}).get('result', {}).get('overall_verdict', 'n/a')}",
        ]
        return "\n".join(lines)
