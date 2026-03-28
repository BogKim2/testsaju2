"""Base agent interface (CONSTITUTION Rule A-01)."""

from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    """모든 에이전트가 구현해야 하는 공통 인터페이스."""

    @abstractmethod
    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """에이전트 실행 — 표준 dict 반환 (CONSTITUTION Rule A-04)."""
        raise NotImplementedError

    @abstractmethod
    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """입력 유효성 검사."""
        raise NotImplementedError

    @abstractmethod
    def get_status(self) -> str:
        """현재 상태 문자열."""
        raise NotImplementedError
