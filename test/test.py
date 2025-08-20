import os
import json
import base64
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_whisper_stt():
    # Get the endpoint and API key from environment variables
    ENDPOINT_URL = os.getenv('RUNPOD_ENDPOINT_URL')
    PORT = os.getenv('PORT', '3001')  # Default to 3001 if not set
    API_KEY = os.getenv('RUNPOD_API_KEY')
    
    if not ENDPOINT_URL or not API_KEY:
        raise ValueError("Please set RUNPOD_ENDPOINT_URL and RUNPOD_API_KEY in your .env file")

    # Test payload based on the schema
    payload = {
        "input": {
            "audio": "https://drive.usercontent.google.com/u/0/uc?id=1ElvMrB5OqvHaMKBQ3UJLmaxaO8ewtmYx&export=download",  # Replace with your audio URL
            "model": "base",
            "transcription": "plain_text",
            "translate": False,
            "language": None,
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
    url = f"{ENDPOINT_URL}:{PORT}/run"
    try:
        # Make the POST request to the endpoint
        response = requests.post(
            ENDPOINT_URL,
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

if __name__ == "__main__":
    test_whisper_stt()
