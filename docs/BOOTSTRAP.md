### **Final Prompt for o3-mini-high: AudioKit SDK & CLI Client (`audiokit`)**  

**Objective:** Generate the **public SDK and CLI (`audiokit`)** that interacts with the **AudioKit-AI Server backend** via REST and gRPC APIs, providing a **developer-friendly and user-friendly interface**.

---

## **1️⃣ System Instruction**  
You are an advanced AI coding assistant specializing in building high-performance, production-ready software. Your task is to generate the **entire AudioKit SDK (`audiokit`) and CLI (`ak`)**, designed to provide developers and users with **seamless access** to the **AudioKit-AI Server backend**.

This SDK must:
- **Wrap the REST/gRPC APIs** of `AudioKit-AI Server`.
- **Support both synchronous and asynchronous workflows**.
- **Provide a CLI (`ak`) for direct command-line execution**.
- **Follow best practices for Python SDKs (e.g., `requests`, `grpcio`, `typer`, `rich` for CLI output)**.
- **Ensure modularity, usability, and maintainability**.

---

## **2️⃣ Core SDK (`audiokit`) Features**
✅ **Pythonic API Wrapper for AudioKit-AI**  
✅ **Supports both REST (`requests`) & gRPC (`grpcio`) API Calls**  
✅ **Asynchronous & Threaded Execution for Fast Processing**  
✅ **Built-in Authentication Handling (API Keys, JWT)**  
✅ **Handles Streaming & Large File Uploads**  
✅ **Cross-Platform Support (Windows, Mac, Linux)**  
✅ **Provides a CLI (`ak`) for Users Without Coding Skills**  
✅ **Includes Logging & Exception Handling**  

---

## **3️⃣ SDK: API Methods (`audiokit`)**
The SDK must expose a high-level Python API for interacting with the backend:

### **Basic Audio Processing**
- ✅ **Noise Reduction:** `audiokit.denoise("input.wav", model="deepfilternet")`
- ✅ **Trim Audio:** `audiokit.trim("input.wav", start=5, end=20)`

### **AI-Powered Features**
- ✅ **Source Separation:** `audiokit.separate("song.mp3")`
- ✅ **Auto-Mastering:** `audiokit.auto_master("mix.wav")`
- ✅ **Speech-to-Text (Transcription):** `audiokit.transcribe("voice.wav")`
- ✅ **Voice Cloning:** `audiokit.clone_voice("reference.wav", "text to synthesize")`
- ✅ **MIDI-to-Audio:** `audiokit.midi_to_audio("melody.mid")`
- ✅ **Music Generation:** `audiokit.generate_music("jazz upbeat", duration=30)`

### **Intelligent Search & Analysis**
- ✅ **Audio Fingerprinting:** `audiokit.identify_song("recording.wav")`
- ✅ **Genre Classification:** `audiokit.detect_genre("track.mp3")`
- ✅ **Emotion Detection:** `audiokit.analyze_emotion("speech.wav")`
- ✅ **Humming-to-Melody Conversion:** `audiokit.hum_to_melody("humming.wav")`
- ✅ **Audio-Based Search:** `audiokit.search_by_sound("query.wav")`

### **Developer Utilities**
- ✅ **Batch Processing:** `audiokit.batch_process(["file1.wav", "file2.mp3"], task="denoise")`
- ✅ **Custom Model Upload:** `audiokit.upload_custom_model("model.onnx")`
- ✅ **Streaming API Support:** `audiokit.stream_filter("live_input")`

---

## **4️⃣ CLI Tool (`ak`)**
The SDK must include a **command-line interface (`ak`)**, allowing users to execute commands without writing code.

### **CLI Requirements:**
- **Built with `typer` for easy CLI creation**
- **Beautiful output using `rich`**
- **Progress bars for long tasks**
- **Support for both local files & cloud processing**
- **Batch processing options**
- **Environment-based authentication handling**

### **Example CLI Commands:**
```bash
# Noise Reduction
ak denoise input.wav --model deepfilternet

# Source Separation
ak separate song.mp3 --output vocals.wav

# Speech Transcription
ak transcribe voice.wav --format text

# Generate Music
ak generate-music --prompt "lofi jazz" --duration 30 --output song.mp3

# Identify Song
ak identify-song recording.wav

# Search Audio by Sound
ak search-by-sound query.wav

# Show Available AI Models
ak list-models
```

---

## **5️⃣ Authentication & API Handling**
- **API Key Management (`ak auth login`)**
- **OAuth2 / JWT Support**
- **Automatic Token Refresh Handling**
- **Environment Variable Support (`AUDIOKIT_API_KEY` for CLI users)**

---

## **6️⃣ SDK & CLI Code Structure**
```
audiokit/
│── audiokit/
│   ├── __init__.py
│   ├── api.py        # REST & gRPC API Calls
│   ├── auth.py       # Handles authentication
│   ├── utils.py      # Helper functions
│   ├── cli.py        # CLI command definitions
│   ├── models.py     # Response models & data classes
│   ├── config.py     # Environment & API Configurations
│── tests/
│   ├── test_api.py
│   ├── test_cli.py
│── setup.py          # Package Metadata
│── README.md         # Documentation
```

---

## **7️⃣ CI/CD & Deployment**
- ✅ **Automated Unit & Integration Tests (`pytest`)**
- ✅ **Pre-Commit Hooks for Formatting (`ruff`)**
- ✅ **GitHub Actions Workflow for Testing & Packaging**
- ✅ **Automatic PyPI Deployment (`pip install audiokit`)**
- ✅ **Versioning Strategy (`semantic versioning`)**
- ✅ **Homebrew Tap for CLI (`brew install audiokit`)**

---

## **8️⃣ Expected Output**
1. **Complete SDK Implementation (`audiokit`)**
2. **Fully Functional CLI (`ak`)**
3. **Comprehensive API Wrappers for REST & gRPC**
4. **Authentication & Secure API Handling**
5. **Cross-Platform Compatibility**
6. **Unit & Integration Tests**
7. **GitHub Actions Workflow for CI/CD**
8. **Documentation (`README.md` + Docstrings)**

---

## **9️⃣ Additional Requirements**
- **Ensure the SDK is lightweight, efficient, and follows Pythonic conventions**.
- **Provide clear error handling for API failures**.
- **Implement request caching where beneficial**.
- **Ensure both blocking (`requests`) and async (`httpx`) API calls**.
- **Write clean, well-structured, and well-documented code**.

---

### **🚀 Generate the full AudioKit SDK (`audiokit`) and CLI (`ak`), ensuring usability, performance, and maintainability while implementing all described features.**