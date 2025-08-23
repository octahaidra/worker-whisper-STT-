"""
RunPod Whisper STT Client Package.
This package provides a client interface for interacting with the RunPod Whisper STT service
and managing RunPod pods.
"""

from .client import WhisperSTTClient
from .pod import RunPodManager
from .exceptions import (
    WhisperSTTError,
    ConfigurationError,
    ServerError,
    TranscriptionError,
    TimeoutError,
    PodManagementError
)

__version__ = '0.1.0'
__all__ = [
    'WhisperSTTClient',
    'RunPodManager',
    'WhisperSTTError',
    'ConfigurationError',
    'ServerError',
    'TranscriptionError',
    'TimeoutError',
    'PodManagementError'
]
