"""
RunPod Whisper STT Client implementation.
Provides a client interface for interacting with the RunPod Whisper STT service.
"""

import os
import json
import time
import base64
import requests
from typing import Optional, Dict, Any, Union
from dotenv import load_dotenv

from .exceptions import (
    ConfigurationError,
    ServerError,
    TranscriptionError,
    TimeoutError
)

class WhisperSTTClient:
    """
    Client for interacting with RunPod Whisper STT service.
    
    This client handles configuration, connection management, and transcription
    requests to the Whisper STT service running on RunPod.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        pod_id: Optional[str] = None,
        port: Optional[str] = None,
        env_file: Optional[str] = None,
        timeout: int = 300
    ):
        """
        Initialize the Whisper STT client.

        Args:
            api_key: RunPod API key. If not provided, will look for RUNPOD_API_KEY in env
            pod_id: RunPod Pod ID. If not provided, will look for POD_ID in env
            port: Pod port number. If not provided, will look for PORT in env or default to 3000
            env_file: Path to .env file for configuration
            timeout: Default timeout for requests in seconds
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        self.api_key = api_key or os.getenv('RUNPOD_API_KEY')
        self.pod_id = pod_id or os.getenv('POD_ID')
        self.port = port or os.getenv('PORT', '3000')
        self.timeout = timeout

        if not self.api_key or not self.pod_id:
            raise ConfigurationError(
                "API key and Pod ID must be provided either through parameters or environment variables"
            )

        self.endpoint_url = f"https://{self.pod_id}-{self.port}.proxy.runpod.net"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def is_active(self) -> bool:
        """
        Check if the RunPod service is active and responding.

        Returns:
            bool: True if service is active, False otherwise
        """
        try:
            response = requests.get(
                f"{self.endpoint_url}/health",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def _encode_audio_file(self, file_path: str) -> str:
        """
        Convert an audio file to base64 string.

        Args:
            file_path: Path to the audio file

        Returns:
            str: Base64 encoded string of the audio file
        """
        try:
            with open(file_path, 'rb') as audio_file:
                return base64.b64encode(audio_file.read()).decode('utf-8')
        except Exception as e:
            raise ConfigurationError(f"Error reading audio file: {str(e)}")

    def _wait_for_job(self, job_id: str) -> Dict[str, Any]:
        """
        Wait for job completion with timeout.

        Args:
            job_id: The ID of the job to wait for

        Returns:
            dict: The completed job data

        Raises:
            TimeoutError: If job doesn't complete within timeout
            ServerError: If job fails or server returns error
        """
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                response = requests.get(
                    f"{self.endpoint_url}/status/{job_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                status_data = response.json()

                if status_data.get("status") == "COMPLETED":
                    return status_data
                elif status_data.get("status") == "FAILED":
                    raise ServerError(f"Job failed: {json.dumps(status_data, indent=2)}")

                time.sleep(2)

            except requests.exceptions.RequestException as e:
                raise ServerError(f"Error checking job status: {str(e)}")

        raise TimeoutError(f"Job did not complete within {self.timeout} seconds")

    def _extract_text(self, data: Dict[str, Any]) -> str:
        """
        Extract text from the transcription response.

        Args:
            data: Response data containing segments

        Returns:
            str: Extracted and formatted text

        Raises:
            TranscriptionError: If text cannot be extracted from response
        """
        try:
            if not data or 'output' not in data or 'segments' not in data['output']:
                raise TranscriptionError("Invalid response format")

            # Extract text from each segment and join them
            text = ' '.join(
                segment['text'].strip()
                for segment in data['output']['segments']
            )

            # Clean up any double spaces
            return ' '.join(text.split())
        except Exception as e:
            raise TranscriptionError(f"Error extracting text from response: {str(e)}")

    def transcribe(
        self,
        audio_input: str,
        is_base64: bool = False,
        model: str = "base",
        language: str = "en",
        translate: bool = False,
        **kwargs
    ) -> str:
        """
        Transcribe audio using Whisper STT service.

        Args:
            audio_input: Either a URL to an audio file or path to local audio file
            is_base64: If True, audio_input is treated as a path to local file
            model: Whisper model to use (default: "base")
            language: Language code (default: "en")
            translate: Whether to translate to English (default: False)
            **kwargs: Additional parameters for the Whisper model

        Returns:
            str: Transcribed text

        Raises:
            ConfigurationError: If input configuration is invalid
            ServerError: If server communication fails
            TranscriptionError: If transcription fails
            TimeoutError: If request times out
        """
        # If is_base64 is True, encode the local file
        if is_base64:
            audio_input = self._encode_audio_file(audio_input)

        payload = {
            "input": {
                "audio": audio_input,
                "is_base64": is_base64,
                "model": model,
                "transcription": "plain_text",
                "translate": translate,
                "language": language,
                "temperature": kwargs.get('temperature', 0),
                "best_of": kwargs.get('best_of', 5),
                "beam_size": kwargs.get('beam_size', 5),
                "patience": kwargs.get('patience', 0),
                "suppress_tokens": kwargs.get('suppress_tokens', "-1"),
                "condition_on_previous_text": kwargs.get('condition_on_previous_text', True),
                "temperature_increment_on_fallback": kwargs.get('temperature_increment_on_fallback', 0.2),
                "compression_ratio_threshold": kwargs.get('compression_ratio_threshold', 2.4),
                "logprob_threshold": kwargs.get('logprob_threshold', -1.0),
                "no_speech_threshold": kwargs.get('no_speech_threshold', 0.6),
            }
        }

        try:
            # Send transcription request
            response = requests.post(
                f"{self.endpoint_url}/run",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            if "id" not in data:
                raise ServerError("No job ID in response")

            # Wait for job completion and get result
            result = self._wait_for_job(data["id"])

            # Extract and return text
            return self._extract_text(result)

        except requests.exceptions.RequestException as e:
            raise ServerError(f"Error communicating with server: {str(e)}")
        except Exception as e:
            raise TranscriptionError(f"Transcription failed: {str(e)}")
