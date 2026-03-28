"""Custom exceptions for agents and orchestrator (CONSTITUTION Rule E-02)."""


class AgentError(Exception):
    """Base class for all agent-related errors."""

    pass


class ParseError(AgentError):
    """File or data parsing failed."""

    pass


class ValidationError(AgentError):
    """Input validation failed."""

    pass


class LLMConnectionError(AgentError):
    """Cannot reach LLM server."""

    pass
