<div align="center">
  <img src="frontend/assets/img/logo.ico" alt="JARVIS Logo" width="120"/>
  <h1>J.A.R.V.I.S.</h1>
  <p><em>Advanced Multimodal AI Desktop Assistant</em></p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg" alt="Python Version" />
    <img src="https://img.shields.io/badge/AI-NVIDIA%20NIM-76B900.svg" alt="NVIDIA NIM" />
    <img src="https://img.shields.io/badge/Security-Face%20Auth-red.svg" alt="Face Auth" />
    <img src="https://img.shields.io/badge/Platform-macOS%20%7C%20Windows-lightgray.svg" alt="Platform" />
  </p>
</div>

---

**J.A.R.V.I.S.** is a futuristic, highly interactive AI desktop assistant inspired by Tony Stark's iconic system. It combines a state-of-the-art **Sci-Fi Holographic GUI**, rapid voice interaction, and robust facial recognition security. Under the hood, it leverages the powerful **NVIDIA Kimi LLM** (via the NVIDIA NIM API) to handle complex logic, multi-turn conversations, and visual reasoning.

---

## 🌟 Key Features

* 💻 **Futuristic HUD GUI**: A beautiful, glassmorphic interface with real-time system metrics (CPU, RAM, Battery), dynamic text rendering, and voice waveform visualizers.
* 🔒 **Biometric Security**: Built-in OpenCV facial recognition ensures only authorized users can bypass the startup sequence.
* 🧠 **Conversational AI**: Powered by NVIDIA's `moonshotai/kimi-k2.6`, featuring conversational memory, deep reasoning, and multimodal optics (webcam image analysis).
* 🗣️ **Native TTS**: Utilizes the macOS `say` command with the "Evan" voice for high-quality, rapid speech synthesis (with a `pyttsx3` fallback for other platforms).
* 🎤 **"Always Listening" Wake Word**: Run entirely hands-free. Just say *"Jarvis"* to trigger the AI safely in the background.
* ⚡ **Native Capabilities**:
  * **System Control**: Open applications, send WhatsApp messages, control system volume, brightness, and sleep states.
  * **Information Retrieval**: Fetch real-time weather (`wttr.in`), global news headlines (Google RSS), and Wikipedia summaries seamlessly.
  * **Utilities**: Set timers, compute complex math expressions, take screenshots, and tell jokes.

---

## 🛠️ Prerequisites

Ensure you have the following installed on your system before beginning:
- **Python 3.10+**
- A **webcam** (Required for Face Authentication and Vision processing)
- A **microphone** (Required for Wake Word and Voice Commands)
- **Git**

---

## 🚀 Setup & Installation

**1. Clone the repository:**
```bash
git clone https://github.com/SiddhantSharma64/J.A.R.V.I.S..git
cd J.A.R.V.I.S.
```

**2. Set up the virtual environment:**
```bash
python3 -m venv envjarvis
source envjarvis/bin/activate
pip install -r requirements.txt
```

**3. Configure your API Keys:**
Create a `.env` file in the root folder and add your credentials:
```env
NVIDIA_API_KEY=your_nvidia_nim_api_key
COUNTRY_CODE=+1 # Used for WhatsApp integrations
```

---

## ⚙️ Usage

The easiest way to launch the assistant is using the included shell script, which automatically handles the virtual environment:

```bash
# Make the script executable (only needed once)
chmod +x start.sh

# Start J.A.R.V.I.S.
./start.sh
```

### 🔒 Initial Setup (Face Enrollment)
If Face Authentication is enabled, J.A.R.V.I.S. will prompt you to run the **Security Setup Wizard** on the first launch. Simply enter your name, look into the camera, and wait for the biometric scan to compile. Once trained, your face will be required to unlock the interface.

---

## 💬 Example Commands

Once J.A.R.V.I.S. is listening, try out these native commands:
> ⛅ *"What is the weather?"* <br>
> ⏱️ *"Set a timer for 5 minutes."* <br>
> 📰 *"What are the latest news headlines?"* <br>
> 🔍 *"Who is Elon Musk?"* <br>
> 🧮 *"Calculate 150 divided by 5."* <br>
> 🌐 *"Open Safari."* <br>
> 📸 *"Take a screenshot."* <br>
> 🌙 *"Go to sleep."* <br>

---

<p align="center">
  <em>Designed & Built for peak productivity and sci-fi immersion.</em>
</p>
