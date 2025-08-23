# Whisper STT Worker with Client Library

This repository contains a Whisper Speech-to-Text (STT) Worker for RunPod, along with a comprehensive client library for managing pods and performing transcriptions. The system supports both URL-based and local audio file transcription, with various Whisper models and configuration options.

## Features

- 🎯 Complete RunPod pod management
- 🔊 Audio transcription from URLs or local files
- 🌐 Multiple language support
- 🛠 Configurable Whisper models and parameters
- 🧪 Comprehensive test suite
- 📦 Easy-to-use client library

## Installation

```bash
# Clone the repository
git clone https://github.com/octahaidra/worker-whisper-STT-.git
cd worker-whisper-STT-

# Install the client library
pip install .
```

## Configuration

Create a `.env` file in your project root:

```env
RUNPOD_API_KEY=your_api_key
POD_ID=your_pod_id
PORT=3000
```

## Usage

### 1. Basic Transcription

```python
from client import WhisperSTTClient

# Initialize client
client = WhisperSTTClient()

# Transcribe from URL
text = client.transcribe(
    "https://example.com/audio.wav",
    is_base64=False,
    model="base",
    language="en"
)

# Transcribe local file
text = client.transcribe(
    "path/to/audio.wav",
    is_base64=True,
    model="base",
    language="en"
)
```

### 2. Pod Management

```python
from client import RunPodManager

# Initialize pod manager
pod_manager = RunPodManager()

# Check pod status
status = pod_manager.get_pod_status("your_pod_id")

# Resume pod if stopped
if status == "STOPPED":
    pod_manager.resume_pod("your_pod_id", gpu_count=1)
    pod_manager.wait_for_pod_status("your_pod_id", "RUNNING")

# Stop pod when done
pod_manager.stop_pod("your_pod_id")
```

### 3. Complete Example

See `client/example.py` for a complete workflow including:
- Pod status checking
- Automatic pod resumption
- Service health verification
- Transcription
- Error handling

```bash
python client/example.py
```

## Model Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `model` | str | Whisper model ("tiny", "base", "small", "medium", "large-v1", "large-v2") | "base" |
| `language` | str | Audio language (None for auto-detection) | None |
| `translate` | bool | Translate to English | False |
| `is_base64` | bool | Whether input is a local file path | False |
| `temperature` | float | Temperature for sampling | 0 |
| `best_of` | int | Candidates for sampling with non-zero temperature | 5 |
| `beam_size` | int | Beams in beam search (temperature=0) | 5 |
| `patience` | float | Beam decoding patience value | None |
| `length_penalty` | float | Token length penalty coefficient | None |
| `suppress_tokens` | str | Tokens to suppress during sampling | "-1" |
| `initial_prompt` | str | First window prompt text | None |
| `condition_on_previous_text` | bool | Use previous output as next window prompt | True |
| `temperature_increment_on_fallback` | float | Temperature increase on decoding failure | 0.2 |
| `compression_ratio_threshold` | float | Failed decoding gzip compression ratio threshold | 2.4 |
| `logprob_threshold` | float | Failed decoding average log probability threshold | -1.0 |
| `no_speech_threshold` | float | Silence segment probability threshold | 0.6 |

## Audio Input Methods

1. **URL Method**:
   ```python
   text = client.transcribe(
       "https://example.com/audio.wav",
       is_base64=False
   )
   ```

2. **Local File Method**:
   ```python
   text = client.transcribe(
       "path/to/local/audio.wav",
       is_base64=True
   )
   ```

## Testing

The package includes a comprehensive test suite:

```bash
# Run all tests
python -m unittest -v test/test.py

# Run specific test cases
python -m unittest test.test_url_transcription
python -m unittest test.test_base64_transcription
```

## Error Handling

The client library includes custom exceptions for better error handling:
- `ConfigurationError`: Configuration issues
- `ServerError`: Communication problems
- `TranscriptionError`: Transcription failures
- `PodManagementError`: Pod management issues
- `TimeoutError`: Operation timeouts

## Pod Management Features

- List all pods
- Get pod information
- Create new pods
- Stop/Resume/Terminate pods
- Monitor pod status
- Wait for status changes
- Resource management

## Development

1. **Setup Development Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -e .
   ```

2. **Run Tests**:
   ```bash
   python -m unittest discover -s test
   ```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under octahaidra License - see the LICENSE file for details.
