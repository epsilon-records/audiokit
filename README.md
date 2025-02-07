# **AudioKit: AI-Powered Audio Processing SDK & CLI**

## **Overview**
AudioKit is an **open-source AI-powered audio processing toolkit** featuring a **Python SDK (`audiokit`)** and a **command-line interface (`ak`)**. It enables users to apply **AI-based noise reduction, speech transcription, source separation, voice cloning, and text-to-image album cover generation.**

### **Features**
✅ **Hybrid AI Processing** – Uses **local processing or cloud API fallback** for efficiency.  
✅ **Noise Reduction** – AI-powered **DeepFilterNet** for audio cleaning.  
✅ **Speech Transcription** – Leverages **OpenAI Whisper** for high-quality ASR.  
✅ **Source Separation** – Uses **Demucs** to split vocals, drums, and instruments.  
✅ **Text-to-Image (Album Covers)** – Generates **AI-based cover art** via **Stable Diffusion XL**.  
✅ **CLI for Non-Developers** – Process audio **via simple `ak` commands**.  

---

# **Installation**

## **Prerequisites**
- **Latest Compatible Python Version** (Recommended: **Python 3.11+**)
- **FFmpeg** (for audio file processing)

```bash
# Install FFmpeg (Linux/macOS)
brew install ffmpeg   # macOS
sudo apt install ffmpeg  # Ubuntu
```

## **Using `uv` for Dependency Management**
```bash
# Install uv (modern pip alternative)
pip install uv

# Install AudioKit dependencies
uv pip install audiokit
```

## **Using `hatch` for Packaging & Development**
```bash
# Install hatch (build system)
uv pip install hatch

# Clone and enter the project directory
git clone https://github.com/epsilon-records/audiokit.git
cd audiokit

# Run in development mode
hatch run ak --help
```

---

# **Usage**

## **1️⃣ Python SDK (`audiokit`)**
```python
import audiokit as ak

# Load an audio file
audio = ak.Audio("speech.wav")

# Apply AI-powered noise reduction
clean_audio = audio.denoise()
clean_audio.save("cleaned_speech.wav")
```

## **2️⃣ CLI (`ak`) Commands**
```bash
# Remove noise from an audio file
ak denoise input.wav output.wav

# Transcribe speech-to-text
ak transcribe input.wav

# Separate vocals and instruments
ak separate input.wav

# Generate AI album cover art
ak generate-cover "A futuristic cyberpunk album cover with neon lights" --output album.png
```

---

# **License**
AudioKit is released under the **MIT License**. See `LICENSE` for more details.