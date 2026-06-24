# 🛡️ RakshaNet: AI-Powered Digital Public Safety Intelligence Platform

RakshaNet is an intelligent, multi-layered public safety platform built to intercept, analyze, and map modern digital cybercrimes. By combining local Computer Vision pipeline networks, neural audio classifiers, real-time speech analytics, and automated entity extraction, RakshaNet equips citizens and special law enforcement divisions to detect and dismantle organized fraud networks.

---

## 📌 Executive Summary & Core Value Proposition

Modern scammers leverage advanced digital tactics—such as **impersonating law enforcement in Skype "Digital Arrest" lockdowns**, passing **counterfeit banknotes** in physical markets, and using **synthesized voice clones** to demand ransom. 

RakshaNet provides a comprehensive shield against these threats by linking citizen-reported events to a central intelligence dashboard:

* **Citizen Protection**: Real-time voice call monitoring, voice deepfake verification, and instant geo-tagged reporting.
* **Law Enforcement Analytics**: Visual correlation charts linking scam VoIP numbers to mule bank accounts, geospatial heatmaps highlighting fraud centers, and legally valid, tamper-proof forensic evidence packages.

---

## 🌟 Core Features

### 1. 📞 Suspicious Call Analyzer & Live Monitor
* **Hybrid Execution Flow**: Supports both **live background speech monitoring** (streaming audio transcripts over WebSockets to identify high-pressure scams) and **offline audio recording uploads** (analyzing recorded MP3/M4A calls).
* **AI Analysis**: Transcribes call audio and invokes the Gemini API to detect digital arrest indicators (e.g., impersonation of CBI, custom authorities, Skype lockdowns), outputting a danger rating (Risk Score) and alert notifications.

### 2. 🎙️ Deepfake Voice Detection
* **First-Class Neural Classifier**: Ingests suspect call files, extracts voice frequency characteristics, and executes inference via a **local ONNX speech model** to calculate synthetic probability.
* **Security Shield**: Alerts users if the speaker is a human or an AI-generated voice clone, combating synthetic media extortion.

### 3. 💵 Counterfeit Banknote Auditor (OpenCV + CNN + Gemini)
* **Visual Preprocessing Pipeline**: Standardizes banknote uploads using **OpenCV** (contrast adjustments, resizing, Gaussian blur, Canny edge detection).
* **Double Validation**: Runs preprocessed images through a **local CNN/YOLO model** to obtain an initial authenticity score, followed by **Gemini Vision** to identify and write descriptive reports on specific visual print anomalies.

### 4. 🕸️ Fraud Network Intelligence (React Flow)
* **Graph Correlation**: Automatically extracts phone numbers, mule bank accounts, suspect names, and UPI IDs from scam reports and links them together.
* **Interactive Canvas**: Renders these links visually on the analyst dashboard using **React Flow**, allowing investigators to trace syndicates.

### 5. 📍 Geospatial Crime Heatmaps
* **Dynamic Mapping**: Gathers GPS coordinates from mobile reports and banknote scans.
* **Hot-Spot Identification**: Plots crime locations using Leaflet map layers, pointing law enforcement to geographical coordinates of active operations.

### 6. 📂 Sealed Evidence Package Generator
* **Tamper-Proof Forensic Logs**: Compiles all verified transcripts, suspect phone numbers, and scanned banknotes into a structured PDF document.
* **Cryptographic Lock**: Computes a SHA-256 hash of the generated file, registers the signature in Firestore, and saves the file directly to Firebase Storage.

---

## 🛠️ Hybrid Technology Stack

| Category | Technology / Framework | Usage |
|---|---|---|
| **Web Dashboard** | React JS (Vite), Tailwind CSS, React Flow, Leaflet | Analyst intelligence console, graph visualizer |
| **Mobile App** | React Native (Expo), NativeWind, Expo Camera, Expo AV | Citizen call recording, banknote capture, and alert feed |
| **Backend Services** | FastAPI (Uvicorn), Python, Pydantic | Decoupled high-performance analytical endpoints |
| **Database & Auth** | Firebase Auth, Firestore NoSQL | User validation, graph documents, incident metadata |
| **Media Storage** | Firebase Storage | Direct archiving of PDFs, images, and audio files |
| **Computer Vision** | OpenCV, ONNX Runtime, PyTorch | Banknote image transformations & edge contrast analysis |
| **Speech & AI** | Gemini 1.5 API (Flash/Pro) | Call transcript analysis, entity extraction, PDF briefings |

---

## 🏗️ Folder Hierarchy & Responsibilities

The project is structured as a modular workspace:

```
RakshaNet/
├── models/                           # Centralized Machine Learning models (ONNX files)
│   ├── counterfeit/                  # Banknote visual classification models
│   └── deepfake_voice/               # Waveform voice clone classification models
│
├── shared/                           # Shared Python package imported by both backends
│   ├── models/                       # Type-safe Pydantic definitions (scam, currency, graph, evidence)
│   └── utils/                        # Shared handlers (Storage, JWT verify, Gemini wrappers)
│
├── web-backend/                      # Analyst API server (FastAPI)
│   └── app/
│       ├── api/                      # Endpoints (/analytics, /currency/scan, /evidence/generate)
│       ├── services/                 # Service layer (currency_service, graph_service, evidence_service)
│       └── repositories/             # Access repository layer (firestore_repo, storage_repo, graph_repo)
│
├── mobile-backend/                   # Citizen API server (FastAPI)
│   └── app/
│       ├── api/                      # Endpoints (/shield/upload, /geospatial, /analyze-deepfake)
│       ├── services/                 # Service layer (scam_service, deepfake_service, heatmap_service)
│       └── repositories/             # Access repository layer (firestore_repo, storage_repo)
│
├── web-app/                          # React web dashboard frontend (Vite + Tailwind)
│   └── src/
│       ├── pages/                    # Views (Dashboard, FraudGraph, Heatmap, CurrencyAnalysis, EvidenceCenter)
│       ├── services/                 # Analytics & graph API bindings
│       └── layouts/                  # Shared dashboard layout template
│
└── mobile-app/                       # React Native Expo citizen app
    └── src/
        ├── screens/                  # Views (HomeScreen, ScamAnalyzerScreen, DeepfakeScreen, CurrencyScanner)
        └── services/                 # API, auth, and storage endpoints
```

---

## ⚡ Setup & Run Guidelines

### Prerequisites
* Python 3.11+
* Node.js v18+
* Firebase Service Account JSON credentials

### 1. Backend Launch Setup

Both backends require a copy of the Firebase Service Account JSON file named `firebase-key.json` placed inside their respective directories (`web-backend/` and `mobile-backend/`).

<details>
<summary>📂 Booting the FastAPI Services</summary>

In two separate terminals:

**Term 1: Web Backend Service (Port 8000)**
```bash
cd web-backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Term 2: Mobile Backend Service (Port 8001)**
```bash
cd mobile-backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

</details>

### 2. Frontend Launch Setup

<details>
<summary>📂 Running the React Web Dashboard</summary>

```bash
cd web-app
npm install
npm run dev
```
Open `http://localhost:3000` in your web browser.

</details>

<details>
<summary>📂 Running the Mobile Expo App</summary>

```bash
cd mobile-app
npm install
npx expo start
```
Scan the QR code in the terminal using the Expo Go mobile application.

</details>

---

## 🛡️ Forensic Security & Safety Standards
* **Data Privacy**: Sound recordings are stored securely in dedicated Firebase Storage folders. Only decoded call metadata and entity logs are saved in Firestore documents.
* **Tamper Proofing**: PDF Evidence reports are cryptographically locked using SHA-256 hashing. Modifying report contents invalidates the registered document hash on the ledger.
