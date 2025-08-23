"""
Example script demonstrating the usage of WhisperSTT client with RunPod management.
This script shows how to:
1. Check and manage pod status
2. Wait for pod to be ready
3. Perform transcription
4. Handle errors gracefully
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from client import WhisperSTTClient, RunPodManager, PodManagementError, ConfigurationError

def main():
    # Load environment variables
    load_dotenv()
    
    # Get pod ID from environment
    pod_id = os.getenv('POD_ID')
    if not pod_id:
        print("Error: POD_ID environment variable not set")
        sys.exit(1)

    try:
        # Initialize the pod manager
        pod_manager = RunPodManager()
        print(f"\nChecking pod {pod_id} status...")
        
        # Check current pod status
        current_status = pod_manager.get_pod_status(pod_id)
        print(f"Current pod status: {current_status}")

        # If pod is stopped, resume it
        if current_status == "STOPPED" or current_status == "EXITED":
            print("\nPod is stopped. Resuming...")
            pod_manager.resume_pod(pod_id, gpu_count=1)
            
            print("Waiting for pod to be ready...")
            if not pod_manager.wait_for_pod_status(pod_id, "RUNNING", timeout=300):
                print("Error: Pod did not reach RUNNING status within timeout")
                sys.exit(1)
            print("Pod is now running!")

        # Initialize the Whisper STT client
        client = WhisperSTTClient()
        
        # Wait for service to be active
        print("\nChecking if service is ready...")
        # Wait until the client is active
        max_attempts = 30
        for attempt in range(max_attempts):
            if client.is_active():
                break
            print(f"Service not ready, waiting... ({attempt + 1}/{max_attempts})")
            time.sleep(10)
        else:
            print("Error: Service is not responding after waiting")
            sys.exit(1)
        print("Service is ready!")

        # Example audio file path
        audio_file = "test/voice-sample.wav"
        
        # Check if file exists
        if not Path(audio_file).is_file():
            print(f"Error: Audio file not found: {audio_file}")
            sys.exit(1)

        # Perform transcription
        print(f"\nTranscribing audio file: {audio_file}")
        try:
            text = client.transcribe(
                audio_file,
                is_base64=True,
                model="base",
                language="en"
            )
            print("\nTranscription result:")
            print("-" * 50)
            print(text)
            print("-" * 50)

        except Exception as e:
            print(f"Error during transcription: {str(e)}")
            sys.exit(1)

        print("\nTranscription completed successfully!")
        
        # Optionally stop the pod when done
        should_stop = input("\nWould you like to stop the pod? (y/N): ").lower()
        if should_stop == 'y':
            print("Stopping pod...")
            pod_manager.stop_pod(pod_id)
            print("Pod stopped successfully!")

    except PodManagementError as e:
        print(f"Pod management error: {str(e)}")
        sys.exit(1)
    except ConfigurationError as e:
        print(f"Configuration error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
