"""
Custom exceptions for the Whisper STT client.
"""

class WhisperSTTError(Exception):
    """Base exception for Whisper STT client errors."""
    pass

class ConfigurationError(WhisperSTTError):
    """Raised when there's an error in the client configuration."""
    pass

class ServerError(WhisperSTTError):
    """Raised when there's an error communicating with the server."""
    pass

class TranscriptionError(WhisperSTTError):
    """Raised when there's an error during transcription."""
    pass

class TimeoutError(WhisperSTTError):
    """Raised when a request times out."""
    pass

class PodManagementError(WhisperSTTError):
    """Raised when there's an error managing RunPod pods."""
    pass
