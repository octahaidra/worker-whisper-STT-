import unittest
import os
from dotenv import load_dotenv
from client import WhisperSTTClient
from client.exceptions import WhisperSTTError, ConfigurationError, ServerError

class TestWhisperSTTServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test class - runs once before all tests"""
        load_dotenv()
        
        # Initialize client
        try:
            cls.client = WhisperSTTClient()
        except ConfigurationError as e:
            raise ValueError(f"Client configuration error: {str(e)}")

        cls.EXPECTED_TEXT = (
            "Hi there, this is a sample voice recording created for speech synthesis testing. "
            "The quit brown fox jumps over the lazy dog. Just a fun way to include every letter "
            "of the alphabet. Numbers like 1, 2, 3 are spoken clearly. Let's see how well this "
            "voice captures tone, timing, and natural rhythm. This audio is provided by samplefiles.com."
        )

    def setUp(self):
        """Set up before each test"""
        # Check if service is available
        if not self.client.is_active():
            self.skipTest("WhisperSTT service is not available")

    def test_url_transcription(self):
        """Test transcription using URL input"""
        print("\n=== Testing with URL input ===")
        
        # Audio file URL
        audio_url = "https://raw.githubusercontent.com/octahaidra/worker-whisper-STT-/dev0/test/voice-sample.wav"
        
        try:
            # Transcribe using URL
            text = self.client.transcribe(
                audio_url,
                is_base64=False,
                model="base",
                language="en"
            )
            
            print("\nExtracted text:")
            print("--------------")
            print(text)
            print("\nExpected text:")
            print("--------------")
            print(self.EXPECTED_TEXT)
            
            self.assertEqual(
                text,
                self.EXPECTED_TEXT,
                "Transcribed text does not match expected text"
            )
        
        except WhisperSTTError as e:
            self.fail(f"Transcription failed: {str(e)}")

    def test_base64_transcription(self):
        """Test transcription using base64 input"""
        print("\n=== Testing with base64 input ===")
        
        # Local audio file path
        audio_path = "test/voice-sample.wav"
        
        try:
            # Transcribe using local file
            text = self.client.transcribe(
                audio_path,
                is_base64=True,
                model="base",
                language="en"
            )
            
            print("\nExtracted text:")
            print("--------------")
            print(text)
            print("\nExpected text:")
            print("--------------")
            print(self.EXPECTED_TEXT)
            
            self.assertEqual(
                text,
                self.EXPECTED_TEXT,
                "Transcribed text does not match expected text"
            )
        
        except WhisperSTTError as e:
            self.fail(f"Transcription failed: {str(e)}")

    def test_service_health(self):
        """Test service health check"""
        self.assertTrue(
            self.client.is_active(),
            "Service health check failed"
        )

if __name__ == '__main__':
    unittest.main(verbosity=2)
