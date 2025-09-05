class LLMException(Exception):
    """Base exception for LLM-related errors."""


class OllamaException(LLMException):
    """Exception raised for Ollama service errors."""


class OllamaConnectionError(OllamaException):
    """Exception raised when cannot connect to Ollama service."""


class OllamaTimeoutError(OllamaException):
    """Exception raised when Ollama service times out."""


# General application exceptions
class ConfigurationError(Exception):
    """Exception raised when configuration is invalid."""
