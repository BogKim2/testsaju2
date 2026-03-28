"""In-memory session store (단기 기억 — MVP)."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


@dataclass
class AgentState:
    """에이전트 1개의 실행 상태."""
    name: str
    status: str = "pending"        # pending | running | done | error
    started_at: str | None = None
    completed_at: str | None = None


@dataclass
class SessionState:
    """분석 세션 한 건."""
    session_id: str
    project_name: str
    version: str
    file_path: str
    agent_order: list[str]
    created_at: str
    # 전체 세션 상태
    status: str = "pending"        # pending | running | done | error
    # 에이전트별 상태
    agent_states: dict[str, AgentState] = field(default_factory=dict)
    agent_outputs: dict[str, Any] = field(default_factory=dict)
    summary_text: str = ""


class MemoryManager:
    """세션별 상태 저장 (프로덕션에서는 Redis 등으로 교체)."""

    def __init__(self) -> None:
        self._sessions: dict[str, SessionState] = {}

    def create_session(
        self,
        project_name: str,
        version: str,
        file_path: str,
        agent_order: list[str],
    ) -> SessionState:
        sid = f"sess-{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        agent_states = {name: AgentState(name=name) for name in agent_order}
        st = SessionState(
            session_id=sid,
            project_name=project_name,
            version=version,
            file_path=file_path,
            agent_order=agent_order,
            created_at=now,
            status="pending",
            agent_states=agent_states,
        )
        self._sessions[sid] = st
        return st

    def get(self, session_id: str) -> SessionState | None:
        return self._sessions.get(session_id)

    def set_agent_running(self, session_id: str, agent_key: str) -> None:
        """에이전트 실행 시작 기록."""
        st = self._sessions.get(session_id)
        if st is None:
            return
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        if agent_key in st.agent_states:
            st.agent_states[agent_key].status = "running"
            st.agent_states[agent_key].started_at = now
        st.status = "running"

    def save_agent_output(self, session_id: str, agent_key: str, output: dict[str, Any]) -> None:
        """에이전트 완료 + 결과 저장."""
        st = self._sessions.get(session_id)
        if st is None:
            return
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        st.agent_outputs[agent_key] = output
        if agent_key in st.agent_states:
            is_error = output.get("status") == "error"
            st.agent_states[agent_key].status = "error" if is_error else "done"
            st.agent_states[agent_key].completed_at = now

    def set_session_done(self, session_id: str) -> None:
        st = self._sessions.get(session_id)
        if st:
            st.status = "done"

    def set_summary(self, session_id: str, text: str) -> None:
        st = self._sessions.get(session_id)
        if st is None:
            return
        st.summary_text = text

    def list_sessions(self) -> list[SessionState]:
        """이력 조회 — 최신 순 정렬."""
        return list(reversed(list(self._sessions.values())))
