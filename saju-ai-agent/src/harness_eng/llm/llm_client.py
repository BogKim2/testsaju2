"""HTTP client for OpenAI-compatible LM Studio endpoint."""

import os
from typing import Any

import httpx

from harness_eng.exceptions import LLMConnectionError


class LLMClient:
    """Orchestrator만 사용 — 에이전트는 직접 호출 금지 (Rule A-02)."""

    def __init__(self, base_url: str | None = None) -> None:
        env_url = os.environ.get("LM_STUDIO_URL", "http://localhost:1234/v1/chat/completions")
        self._url = base_url or env_url

    def summarize(self, prompt: str, max_tokens: int = 256) -> str:
        """간단 요약 호출 — 실패 시 예외."""
        payload: dict[str, Any] = {
            "model": os.environ.get("LLM_MODEL", "local-model"),
            "messages": [
                {"role": "system", "content": "You are a harness engineering assistant."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.4,
        }
        try:
            with httpx.Client(timeout=30.0) as client:
                r = client.post(self._url, json=payload)
                r.raise_for_status()
                data = r.json()
                return str(data["choices"][0]["message"]["content"])
        except (httpx.HTTPError, KeyError, IndexError) as e:
            raise LLMConnectionError(str(e)) from e
