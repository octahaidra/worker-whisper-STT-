import os
import json
import base64
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_base64_audio(file_path):
    """Convert audio file to base64 string"""
    with open(file_path, 'rb') as audio_file:
        return base64.b64encode(audio_file.read()).decode('utf-8')

def test_whisper_stt(use_base64=False, audio_path=None):
    """Test Whisper STT with either URL or base64 input"""
    # Get the endpoint and API key from environment variables
    ENDPOINT_URL = os.getenv('RUNPOD_ENDPOINT_URL')
    PORT = os.getenv('PORT', '3001')  # Default to 3001 if not set
    API_KEY = os.getenv('RUNPOD_API_KEY')

    if not ENDPOINT_URL or not API_KEY:
        raise ValueError("Please set RUNPOD_ENDPOINT_URL and RUNPOD_API_KEY in your .env file")

    # Use the public URL for the audio file
    audio_url = "https://raw.githubusercontent.com/octahaidra/worker-whisper-STT-/dev0/test/voice-sample.wav"

    # Test payload based on the schema
    payload = {
        "input": {
            "audio": get_base64_audio(audio_path) if use_base64 else audio_url,
            "is_base64": use_base64,
            "model": "base",
            "transcription": "plain_text",
            "translate": False,
            "language": "en",
            "temperature": 0,
            "best_of": 5,
            "beam_size": 5,
            "patience": 0,
            "length_penalty": 0,
            "suppress_tokens": "-1",
            "initial_prompt": None,
            "condition_on_previous_text": True,
            "temperature_increment_on_fallback": 0.2,
            "compression_ratio_threshold": 2.4,
            "logprob_threshold": -1.0,
            "no_speech_threshold": 0.6
        }
    }

    # Headers for the request
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    try:
        # Make the POST request to the endpoint
        response = requests.post(
            f"{ENDPOINT_URL}:{PORT}/run",
            headers=headers,
            json=payload
        )
        
        # Check if request was successful
        response.raise_for_status()
        
        # Parse and print the response
        result = response.json()
        print("Test Results:")
        print(json.dumps(result, indent=2))
        
        return result

    except requests.exceptions.RequestException as e:
        print(f"Error making request: {str(e)}")
        return None
    finally:
        pass

if __name__ == "__main__":
    # Test 1: Using URL
    print("\n=== Testing with public URL ===")
    test_whisper_stt(use_base64=False, audio_path="voice-sample.wav")

    # Test 2: Using base64 encoded audio
    print("\n=== Testing with base64 encoded audio ===")
    test_whisper_stt(use_base64=True, audio_path="test/voice-sample.wav")
