# **Contributing to AudioKit**

Thank you for your interest in contributing to **AudioKit**! We welcome contributions from the community to improve and expand the project. This document outlines guidelines to help ensure a smooth development process.

---

## **1. Setting Up a Development Environment**

### **Prerequisites**
- **Latest Compatible Python Version** (Recommended: **Python 3.11+**)
- **FFmpeg** (for audio file processing)

```bash
# Install FFmpeg (Linux/macOS)
brew install ffmpeg   # macOS
sudo apt install ffmpeg  # Ubuntu
```

### **Clone the Repository**
```bash
git clone https://github.com/epsilon-records/audiokit.git
cd audiokit
```

### **Using `uv` for Dependency Management**
```bash
# Install uv (modern dependency manager)
pip install uv

# Install dependencies
uv pip install -r requirements.txt
```

### **Using `hatch` for Packaging & Development**
```bash
# Install hatch
uv pip install hatch

# Run in development mode
hatch run ak --help
```

---

## **2. Code Style & Linting**

We use **ruff** instead of `black` and `flake8` for **code formatting and linting**.

### **Installing Ruff**
```bash
uv pip install ruff
```

### **Run Formatting & Linting**
```bash
ruff check .  # Run linting
ruff format .  # Auto-format code
```

### **Pre-commit Hook Setup**
```bash
ruff --fix .
```

---

## **3. Running Tests**

### **Run Tests Using Hatch**
```bash
hatch test
```

### **Run Specific Test Files**
```bash
hatch run pytest tests/test_audio.py
```

---

## **4. Submitting Contributions**

### **1️⃣ Fork the Repository**
Click the **Fork** button at the top of the repository page on GitHub.

### **2️⃣ Create a Feature Branch**
```bash
git checkout -b feature-branch-name
```

### **3️⃣ Make Changes & Commit**
```bash
git add .
git commit -m "Add new feature or fix"
```

### **4️⃣ Push Changes to GitHub**
```bash
git push origin feature-branch-name
```

### **5️⃣ Open a Pull Request**
1. Go to your forked repository on GitHub.
2. Click on **Compare & pull request**.
3. Provide a clear title and description of your changes.
4. Submit the pull request.

---

## **5. License**
By contributing, you agree that your contributions will be licensed under the **MIT License**.