# 🏥 MediSign — Medical Sign Language Recognition System

> **Real-time AI-powered sign language translation for healthcare communication.**
> Converts medical sign language gestures into text, audio, and 3D avatar animations — bridging communication between deaf/mute patients and medical professionals.

---

## 🌐 Live URLs (Development)

| Service | URL | Description |
|---|---|---|
| **React Frontend** | `http://localhost:5173` | Modern dashboard (Vite + React) |
| **Flask Backend** | `http://localhost:5000` | REST API + ML inference |
| **Communication Bridge** | `http://localhost:5173/dashboard/bridge` | Split-screen two-way translator |

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [Features](#-features)
3. [System Architecture](#-system-architecture)
4. [Tech Stack](#-tech-stack)
5. [Project Structure](#-project-structure)
6. [Setup & Installation](#-setup--installation)
7. [Running the Application](#-running-the-application)
8. [API Reference](#-api-reference)
9. [Frontend Pages](#-frontend-pages)
10. [ML Pipeline](#-ml-pipeline)
11. [Supported Medical Terms](#-supported-medical-terms)
12. [Multilingual TTS](#-multilingual-tts)
13. [Configuration](#-configuration)
14. [Testing](#-testing)
15. [Troubleshooting](#-troubleshooting)

---

## 📖 Project Overview

MediSign is a full-stack medical AI system that allows:

- **Patients** to communicate via medical sign language, which is recognized in real time by a trained BiLSTM+Attention model.
- **Doctors** to speak or type instructions, which are converted to sign language via a 3D animated avatar.
- **Cross-lingual support**: Audio feedback in English, Telugu, Hindi, Marathi, and Tamil.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎥 **Live Webcam Capture** | Records 3-second clips, processes 60 frames through MobileNetV2 + BiLSTM |
| 📤 **Video Upload** | Batch upload pre-recorded sign language videos |
| 🤖 **3D Avatar Interpreter** | Canvas-based medical doctor avatar signs instructions in ISL |
| 🌐 **Communication Bridge** | Split-screen: webcam recognition on the left, avatar interpreter on the right |
| 🔊 **Multilingual TTS** | Audio output via gTTS in 5 languages |
| 📊 **Prediction History** | CSV-backed audit log of all predictions |
| 🌙 **Dark Mode** | Full dark/light mode toggle |
| 📱 **Responsive Design** | Mobile-first layout, sidebar collapses on small screens |

---

## 🏗 System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    FRONTEND (React/Vite)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐   │
│  │ WebcamView│  │Interpreter│  │ CommunicationBridge  │   │
│  │  (port   │  │   View   │  │ (Split Screen)       │   │
│  │  5173)   │  │ SignAvatar│  │ Webcam + Avatar       │   │
│  └────┬─────┘  └─────┬────┘  └──────────┬───────────┘   │
└───────┼──────────────┼─────────────────┼────────────────┘
        │  axios /api  │                 │
┌───────┼──────────────┼─────────────────┼────────────────┐
│       ▼     BACKEND (Flask, port 5000) ▼                 │
│  ┌─────────────────────────────────────────────────┐    │
│  │  POST /api/recognize  GET /api/info  /audio/<f>  │    │
│  └──────────┬──────────────────────────────────────┘    │
│             │                                            │
│  ┌──────────▼──────────────────────────────────────┐    │
│  │              ML PIPELINE                         │    │
│  │  video → preprocess → MobileNetV2 → BiLSTM →    │    │
│  │  softmax → label → translate → gTTS → mp3       │    │
│  └─────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

---

## 🛠 Tech Stack

### Backend
| Library | Version | Purpose |
|---|---|---|
| Python | 3.12 | Runtime |
| Flask | 2.x | REST API server |
| TensorFlow | 2.16.1 | Model inference |
| OpenCV | 4.8.0.76 | Frame extraction |
| NumPy | 1.24.4 | Numerical processing |
| gTTS | 2.5.1 | Text-to-speech |
| googletrans | 4.0.0-rc1 | Translation |
| scikit-learn | 1.3.2 | Label encoding |

### Frontend
| Library | Version | Purpose |
|---|---|---|
| React | 19.x | UI framework |
| Vite | 7.x | Build tool & dev server |
| TailwindCSS | 4.x | Styling |
| Framer Motion | 12.x | Animations |
| Lucide React | Latest | Icons |
| Axios | 1.x | HTTP client |
| React Router | 7.x | Routing |
| Three.js | 0.183.x | 3D rendering base |

---

## 📁 Project Structure

```
medisign/
│
├── web_app.py                  # ✅ Flask backend & REST API (MAIN ENTRY)
├── requirements.txt            # Python dependencies
├── config_train.json           # Model training configuration
│
├── modules/                    # Core ML modules
│   ├── preprocessing.py        # Video frame extraction (60 frames, 224×224)
│   ├── feature_extractor.py    # MobileNetV2 feature extraction
│   ├── sequence_model.py       # BiLSTM + Attention model definition
│   ├── text_to_speech.py       # gTTS + googletrans TTS pipeline
│   ├── prediction_logger.py    # CSV audit logging
│   └── trainer.py              # Model training utilities
│
├── models/                     # Trained model files (.h5, label_map.json)
├── dataset/                    # Medical sign language video dataset
├── logs/                       # Prediction logs & audio files
│   └── audio/                  # Generated TTS audio (mp3)
│
├── templates/                  # Flask HTML templates (fallback web UI)
│   ├── index.html
│   ├── demo.html
│   ├── about.html
│   └── features.html
│
├── frontend/                   # React/Vite frontend
│   ├── index.html              # Root HTML
│   ├── vite.config.js          # Vite configuration
│   ├── tailwind.config.js      # Tailwind configuration
│   └── src/
│       ├── App.jsx             # Router setup
│       ├── main.jsx            # React entry point
│       ├── index.css           # Global styles
│       ├── pages/
│       │   ├── Dashboard.jsx   # Dashboard view switcher
│       │   └── Login.jsx       # Login page
│       ├── layouts/
│       │   └── DashboardLayout.jsx  # Sidebar + header layout
│       ├── components/
│       │   ├── Overview.jsx         # Dashboard home stats
│       │   ├── WebcamView.jsx       # Live webcam capture + inference
│       │   ├── UploadView.jsx       # Video file upload + inference
│       │   ├── InterpreterView.jsx  # 3D avatar + speech-to-sign
│       │   ├── CommunicationBridge.jsx  # ✨ Split-screen two-way bridge
│       │   ├── SignAvatar.jsx       # Canvas-based animated doctor avatar
│       │   ├── HistoryView.jsx      # Prediction history log
│       │   ├── Settings.jsx         # App settings
│       │   ├── AboutView.jsx        # About page
│       │   └── SupportView.jsx      # Help & support
│       └── services/
│           └── predictionService.js  # Axios API calls to Flask
│
├── medisign_env/               # Python virtual environment
├── train.py                    # Full model training script
└── download_youtube_medical.py # Dataset acquisition script
```

---

## ⚙️ Setup & Installation

### Prerequisites

- **Python 3.12** (via virtual environment `medisign_env`)
- **Node.js 18+** and npm
- **Git** (optional)
- Webcam (for live recording features)

### 1. Clone / Navigate to Project

```bash
cd "c:\Users\vishn\OneDrive\Desktop\New folder\medisign"
```

### 2. Backend Setup (Python)

The project includes a pre-configured virtual environment:

```bash
# Activate virtual environment (Windows)
.\medisign_env\Scripts\activate

# Install dependencies (if re-creating env)
pip install -r requirements.txt
```

### 3. Frontend Setup (Node.js)

```bash
cd frontend
npm install
```

---

## 🚀 Running the Application

### Start Backend (Terminal 1)

```bash
# From project root
.\medisign_env\Scripts\python.exe web_app.py
```

The Flask server starts at: **http://localhost:5000**

> 💡 **Note**: TensorFlow will load the model on startup (~5-15 seconds). Look for `Model loaded successfully` in the logs.

### Start Frontend (Terminal 2)

```bash
cd frontend
npm.cmd run dev
```

The React app starts at: **http://localhost:5173**

### Access the Application

Open your browser and navigate to: **http://localhost:5173**

Default login: any username/password (auth is stored in localStorage).

---

## 📡 API Reference

Base URL: `http://localhost:5000`

### `POST /api/recognize`

Recognizes a sign language video clip.

**Request** (`multipart/form-data`):

| Field | Type | Description |
|---|---|---|
| `video` | File | Video file (mp4, webm) |
| `language` | string | Target language: `en`, `te`, `hi`, `mr`, `ta` |

**Response** (`application/json`):

```json
{
  "success": true,
  "prediction": "Heart Attack",
  "confidence": 0.94,
  "all_predictions": {
    "Heart Attack": 0.94,
    "Diabetes": 0.04,
    "Fever": 0.02
  },
  "translation": "హృదయ విఫలత",
  "audio_url": "/audio/heart_attack_1234567.mp3",
  "language": "te"
}
```

### `GET /api/info`

Returns system info and supported vocabulary.

```json
{
  "name": "MediSign",
  "version": "2.0",
  "classes": 10,
  "medical_terms": ["Heart Attack", "Diabetes", ...]
}
```

### `GET /api/stats`

Returns usage statistics.

### `GET /audio/<filename>`

Serves a generated TTS audio file.

---

## 🖥 Frontend Pages

| Route | Component | Description |
|---|---|---|
| `/` | Redirects to `/dashboard` | — |
| `/login` | `Login.jsx` | Authentication page |
| `/dashboard` | `Overview.jsx` | Stats & quick actions |
| `/dashboard/webcam` | `WebcamView.jsx` | 🎥 Live webcam recording + inference |
| `/dashboard/upload` | `UploadView.jsx` | 📤 Upload video file |
| `/dashboard/interpreter` | `InterpreterView.jsx` | 🤖 3D avatar sign interpreter |
| `/dashboard/bridge` | `CommunicationBridge.jsx` | 🌐 Split-screen two-way bridge |
| `/dashboard/history` | `HistoryView.jsx` | 📊 Prediction audit log |
| `/dashboard/about` | `AboutView.jsx` | About MediSign |
| `/dashboard/support` | `SupportView.jsx` | Help & support |
| `/dashboard/settings` | `Settings.jsx` | App settings |

---

## 🧠 ML Pipeline

```
Raw Video (3s, 20-30fps)
    ↓
preprocessing.py → Sample 60 frames, resize to 224×224 RGB
    ↓
feature_extractor.py → MobileNetV2 (pretrained ImageNet, frozen) → 1280-dim vectors
    ↓
Shape: (1, 60, 1280)
    ↓
sequence_model.py → BiLSTM (256 units) + Attention mechanism → Dense(10) + Softmax
    ↓
Predicted Label + Confidence
    ↓
text_to_speech.py → googletrans → gTTS → MP3 audio
```

### Model Details

| Parameter | Value |
|---|---|
| Feature extractor | MobileNetV2 (ImageNet pretrained, no top) |
| Sequence model | Bidirectional LSTM (256 units) |
| Attention | Custom additive attention |
| Input frames | 60 frames per video |
| Frame size | 224 × 224 × 3 |
| Feature vector | 1280-dim per frame |
| Output classes | 10 medical terms |
| Optimizer | Adam |
| Loss | Categorical Crossentropy |

---

## 🩺 Supported Medical Terms

| # | Term | Description |
|---|---|---|
| 1 | Heart Attack | Cardiac emergency sign |
| 2 | Diabetes | Metabolic condition |
| 3 | Broken Arm | Limb fracture |
| 4 | Fever | Elevated body temperature |
| 5 | Medication | Drug/medicine reference |
| 6 | Headache | Head pain |
| 7 | Hospital | Medical facility |
| 8 | Surgeon | Surgical doctor |
| 9 | Emergency | Urgent medical need |
| 10 | Pain | General pain expression |

---

## 🔊 Multilingual TTS

The system supports audio output in the following languages via `googletrans` + `gTTS`:

| Code | Language |
|---|---|
| `en` | English (default) |
| `te` | Telugu (తెలుగు) |
| `hi` | Hindi (हिंदी) |
| `mr` | Marathi (मराठी) |
| `ta` | Tamil (தமிழ்) |

> Both the audio **and** the translated text are returned by the `/api/recognize` endpoint. The frontend displays the translated text as the primary label when a non-English language is selected.

---

## ⚙️ Configuration

### `config_train.json`

```json
{
  "num_frames": 60,
  "target_size": [224, 224],
  "lstm_units": 256,
  "dropout": 0.3,
  "epochs": 50,
  "batch_size": 8,
  "learning_rate": 0.0001
}
```

### `frontend/src/services/predictionService.js`

```js
const BASE_URL = 'http://localhost:5000';
```

Change this to your deployment URL for production.

### Environment Variables (optional)

| Variable | Default | Description |
|---|---|---|
| `TF_CPP_MIN_LOG_LEVEL` | `2` | Suppress TF verbose logs |
| `FLASK_ENV` | `production` | Flask environment |
| `FLASK_PORT` | `5000` | Backend port |

---

## 🧪 Testing

### Backend Tests

```bash
# Activate venv first
.\medisign_env\Scripts\activate

# Test the inference API
python test_api_recognize.py

# Test TTS integration
python test_tts_integration.py

# Test audio serving
python test_audio_serving.py

# Run all module vtests
python -m pytest modules/ -v
```

### Frontend Build Verification

```bash
cd frontend
npm.cmd run build  # Build check (no broken imports)
npm.cmd run lint   # ESLint check
```

---

## 🔧 Troubleshooting

### Backend won't start

```
Error: Model not found
```
→ Ensure `models/` directory contains `*.h5` and `label_map.json`.

```
AttributeError: module 'httpcore' has no attribute 'SyncHTTPTransport'
```
→ Always run using the virtual environment: `.\medisign_env\Scripts\python.exe web_app.py`

### Frontend won't compile

```
npm : File cannot be loaded because running scripts is disabled
```
→ Use `npm.cmd run dev` instead of `npm run dev` in PowerShell.

### Camera not working

→ Ensure the browser has camera permissions. Check DevTools → Application → Permissions.

### Audio not playing

→ Browsers may block autoplay. Click anywhere on the page first, then try recording.

### Translation text not showing for Telugu/Hindi

→ Ensure the backend has internet access for `googletrans`. The translation field in the API response must be non-null.

---

## 📄 HTML: Flask Fallback Web Interface

The project also includes standalone HTML templates served by Flask at `http://localhost:5000`:

### `templates/index.html` — Home Page

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MediSign - Medical Sign Language Recognition</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #0f172a; color: #f1f5f9; }
        .hero {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(ellipse at center, #1e3a5f 0%, #0f172a 70%);
        }
        .hero-content { text-align: center; max-width: 700px; padding: 2rem; }
        .badge {
            display: inline-block;
            background: rgba(14, 165, 233, 0.15);
            border: 1px solid rgba(14, 165, 233, 0.3);
            color: #38bdf8;
            font-size: 0.7rem;
            font-weight: 800;
            letter-spacing: 0.2em;
            text-transform: uppercase;
            padding: 0.4em 1em;
            border-radius: 999px;
            margin-bottom: 1.5rem;
        }
        h1 { font-size: 3.5rem; font-weight: 900; line-height: 1.1; margin-bottom: 1.5rem; }
        h1 span { color: #38bdf8; }
        p { color: #94a3b8; font-size: 1.1rem; line-height: 1.8; margin-bottom: 2rem; }
        .btn-primary {
            display: inline-block;
            background: #0284c7;
            color: white;
            padding: 0.9rem 2.5rem;
            border-radius: 0.75rem;
            font-weight: 700;
            text-decoration: none;
            transition: all 0.2s;
        }
        .btn-primary:hover { background: #0369a1; transform: translateY(-2px); }
    </style>
</head>
<body>
    <section class="hero">
        <div class="hero-content">
            <div class="badge">Medical AI · Sign Language · Real-time</div>
            <h1>Breaking Barriers with <span>MediSign</span></h1>
            <p>AI-powered sign language recognition that bridges communication between deaf/mute patients and healthcare professionals. Real-time, multilingual, and medically accurate.</p>
            <a href="/demo" class="btn-primary">Try Live Demo</a>
        </div>
    </section>
</body>
</html>
```

### Core Demo Page (`templates/demo.html`) — Key features

```html
<!-- Video Upload Section -->
<form id="uploadForm" enctype="multipart/form-data">
    <input type="file" name="video" accept="video/*" required />
    <select name="language">
        <option value="en">English</option>
        <option value="te">Telugu</option>
        <option value="hi">Hindi</option>
    </select>
    <button type="submit">Analyze Sign</button>
</form>

<script>
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const res = await fetch('/api/recognize', { method: 'POST', body: formData });
    const data = await res.json();
    // data.prediction = English label
    // data.translation = Translated text (e.g., Telugu)
    // data.audio_url = path to TTS audio
    console.log(data);
});
</script>
```

---

## 📸 Screenshots

**Dashboard Overview**

The main dashboard displays real-time stats, supported vocabulary, and platform performance metrics.

**Communication Bridge (Split Screen)**

Left: Live webcam for patient sign recognition → Right: 3D doctor avatar with speech-to-sign translation.

---

## 🤝 Contributing

1. Fork the repo.
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m "feat: add your feature"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request.

---

## 📜 License

This project is developed for academic and healthcare accessibility research purposes.

---

## 👤 Author

**MediSign Team** — Medical AI for Accessible Healthcare Communication  
Built with ❤️ for making healthcare communication barrier-free.

---

*MediSign v2.0 — Flask Backend + React Frontend + BiLSTM+Attention ML Model*
