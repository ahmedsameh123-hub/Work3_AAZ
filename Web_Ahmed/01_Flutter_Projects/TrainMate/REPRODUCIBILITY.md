# TrainMate — Reproducibility Guide

**Graduation project:** TrainMate — AI-Powered Mobile Smart Gym Assistant  
**Purpose:** Anyone who receives this repository from GitHub can install all dependencies and run the full system **from scratch** on an **Android emulator** or a **physical Android phone** without help from the team.

> **Related docs:**  
> - `README.md` — technical overview and API reference  
> - `Document/GP_Report_Semester2_G6.docx` — final graduation report (optional reading)

---

## Table of contents

1. [What success looks like](#1-what-success-looks-like)
2. [Hardware and software requirements](#2-hardware-and-software-requirements)
3. [Download and install tools (one-time)](#3-download-and-install-tools-one-time)
4. [Project structure](#4-project-structure)
5. [Correct run order (important)](#5-correct-run-order-important)
6. [Step 1 — Backend server](#6-step-1--backend-server)
7. [Step 2 — ML model files](#7-step-2--ml-model-files)
8. [Step 3 — Flutter mobile app](#8-step-3--flutter-mobile-app)
9. [Running on Android emulator](#9-running-on-android-emulator)
10. [Running on a physical Android phone](#10-running-on-a-physical-android-phone)
11. [Server URL in the app](#11-server-url-in-the-app)
12. [First use — register to workout](#12-first-use--register-to-workout)
13. [Optional features](#13-optional-features)
14. [Building a release APK](#14-building-a-release-apk)
15. [Checklists](#15-checklists)
16. [Troubleshooting](#16-troubleshooting)
17. [Quick command reference](#17-quick-command-reference)

---

## 1. What success looks like

| Component | URL / check | Expected result |
|-----------|-------------|-----------------|
| Backend | `http://127.0.0.1:8000/api/health` | JSON with `"status": "ok"` |
| API docs | `http://127.0.0.1:8000/docs` | Swagger UI opens |
| Mobile app | Runs on emulator or phone | Login screen appears |
| Connectivity | App → backend | Register + login succeed |

---

## 2. Hardware and software requirements

### Development PC (laptop)

| Requirement | Details |
|-------------|---------|
| OS | Windows 10/11 (commands below use PowerShell) |
| CPU | Intel i5 or better |
| RAM | 8 GB minimum — **16 GB recommended** (TensorFlow is heavy) |
| Disk | ~10 GB free (Flutter SDK + Android SDK + Python venv + ML) |
| Internet | Required for first install and for Groq chatbot |

### Physical Android phone (additional)

| Requirement | Details |
|-------------|---------|
| Android device | API 24+ (Android 7+) |
| USB cable | For `flutter run` / debugging |
| Same Wi‑Fi network | **Phone and PC on the same Wi‑Fi** (USB alone does not carry HTTP to the backend) |
| Camera | Required for live exercise tracking |

---

## 3. Download and install tools (one-time)

### 3.1 Python 3.10 or 3.11

1. Download: https://www.python.org/downloads/
2. During install: enable **Add Python to PATH**
3. Verify in PowerShell:

```powershell
python --version
```

Expected: `Python 3.10.x` or `Python 3.11.x`  
**Do not use Python 3.12+** — MediaPipe may fail to install.

---

### 3.2 Git

1. Download: https://git-scm.com/download/win
2. Verify:

```powershell
git --version
```

---

### 3.3 Flutter SDK

1. Install guide: https://docs.flutter.dev/get-started/install/windows
2. Extract to a path without spaces (e.g. `C:\flutter`)
3. Add `C:\flutter\bin` to Windows **PATH**
4. Verify:

```powershell
flutter --version
flutter doctor
```

---

### 3.4 Android Studio

1. Download: https://developer.android.com/studio
2. Install **Android SDK** and **Android SDK Platform-Tools**
3. Android Studio → **SDK Manager**:
   - Android SDK Platform 34 (or 33+)
   - Android SDK Build-Tools
   - Android Emulator
4. Accept licenses:

```powershell
flutter doctor --android-licenses
```

Type `y` for each prompt.

5. `flutter doctor` should show:

```
[✓] Android toolchain
[✓] Android Studio
```

---

### 3.5 (Optional) Groq API for chatbot

1. Sign up: https://console.groq.com
2. Create an API key
3. Add to `trainmate_backend/.env` as `GROQ_API_KEY`

Without the key: the app runs, but the chatbot uses limited built-in fallback replies.

---

## 4. Project structure

```
PP/                                 ← repository root
├── REPRODUCIBILITY.md              ← this file
├── README.md
├── ai/                             ← ML training, body analyzer, Streamlit demo
│   ├── models/                     ← trained weights (.h5, .pkl)
│   └── export_for_flutter.py       ← export TFLite for mobile
├── trainmate_backend/              ← FastAPI server
│   ├── .env.example
│   ├── requirements.txt            ← core install (~2 min)
│   ├── requirements-ml.txt         ← heavy ML (optional)
│   ├── start.ps1                   ← quick Windows start (-HostAll for phone)
│   └── start-window.ps1            ← backend in a separate window
├── trainmate_app/                  ← Flutter client
│   └── assets/models/              ← TFLite after export
└── Document/                       ← graduation report + screenshots + diagrams
```

---

## 5. Correct run order (important)

```
① Install Python + Flutter + Android Studio (one-time)
② Clone or unzip the project
③ Start the backend
④ (Optional) Export TFLite model
⑤ flutter pub get
⑥ flutter run on emulator or phone
⑦ Set server URL in app settings if needed
⑧ Register an account and test
```

**Do not start the mobile app before the backend.**

---

## 6. Step 1 — Backend server

### 6.1 Get the project

```powershell
cd Desktop
git clone <your-github-repo-url>
cd PP
```

Or unzip the submission ZIP into a folder named `PP`.

---

### 6.2 Create Python virtual environment and install packages

```powershell
cd trainmate_backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If script execution is blocked:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate the venv again.

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> **Important:** Do not cancel `pip install` — wait 1–2 minutes.

---

### 6.3 Configure `.env`

```powershell
copy .env.example .env
```

Edit `.env` — at minimum:

```env
JWT_SECRET_KEY=replace-with-a-long-random-secret-at-least-32-chars
EXPOSE_VERIFICATION_CODES=true
GROQ_API_KEY=gsk_xxxxxxxx
```

| Variable | Required? | Purpose |
|----------|-----------|---------|
| `JWT_SECRET_KEY` | Yes | Login security |
| `EXPOSE_VERIFICATION_CODES=true` | For demo | Verification code shown in app (no inbox needed) |
| `GROQ_API_KEY` | For full chatbot | Groq API key |

---

### 6.4 Start the server

**Recommended for physical phone (same Wi‑Fi):**

```powershell
.\start.ps1 -HostAll
```

Or open a dedicated window (keeps running even if the IDE terminal closes):

```powershell
.\start-window.ps1 -HostAll
```

**Manual start (emulator or phone):**

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

> `--host 0.0.0.0` is **required** so phones on the LAN can reach the server.  
> `start.ps1` defaults to `127.0.0.1` without `-HostAll`. It does **not** enable `--reload` by default (OneDrive sync can kill the server).

---

### 6.5 Verify

Open in the PC browser:

- http://127.0.0.1:8000/api/health  
- http://127.0.0.1:8000/docs  

You should see `"status":"ok"`.

**Leave this PowerShell window open** — the server runs there.

---

### 6.6 (Optional) Install server-side ML

Needed only for:

- Server-side exercise classification fallback
- Before/after body photo analysis

```powershell
pip install -r requirements-ml.txt
```

Wait 10–20 minutes (~500 MB). **Do not interrupt the install.**

---

## 7. Step 2 — ML model files

### 7.1 Required files in `ai/models/`

| File | Purpose |
|------|---------|
| `final_forthesis_bidirectionallstm_and_encoders_exercise_classifier_model.h5` | Trained Keras model |
| `thesis_bidirectionallstm_scaler.pkl` | Feature scaler |
| `thesis_bidirectionallstm_label_encoder.pkl` | Class labels |

If not in the repo (large files): copy from the submission package or train via `ai/model_training.py`.

See also: `ai/models/REQUIRED_FILES.txt`

---

### 7.2 Export TFLite for on-device classification (recommended)

```powershell
cd ..\ai
pip install -r requirements-tflite-export.txt
python export_for_flutter.py
```

**Output:**

```
trainmate_app/assets/models/
├── exercise_classifier.tflite
├── scaler_params.json
└── classes.json
```

Without TFLite: use **manual exercise selection**, or auto-classify via the server if ML is installed.

---

## 8. Step 3 — Flutter mobile app

```powershell
cd ..\trainmate_app
flutter pub get
flutter doctor
```

Android toolchain should show ✓

---

## 9. Running on Android emulator

### 9.1 Create an emulator (one-time)

1. Android Studio → **Device Manager**
2. **Create Device** → e.g. Pixel 6
3. System image: API 34 (or 33) → Download if needed
4. Finish → **Play** to start the emulator

---

### 9.2 Start backend (PowerShell window 1)

```powershell
cd trainmate_backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

### 9.3 Run the app (PowerShell window 2)

```powershell
cd trainmate_app
flutter devices
flutter run
```

You usually **do not need** `--dart-define` on the emulator — the app auto-discovers `10.0.2.2`.

---

### 9.4 Emulator backend address

| Environment | Backend URL from emulator |
|-------------|---------------------------|
| Android Emulator | `http://10.0.2.2:8000` |

The app probes this automatically on launch.

---

### 9.5 Emulator camera

- Device Manager → AVD settings → Camera: **Webcam0**
- For real pose tracking, a physical device works best

---

## 10. Running on a physical Android phone

### 10.1 Enable developer mode

1. Settings → About phone → tap **Build number** 7 times
2. Settings → Developer options → enable **USB debugging**
3. Connect USB → accept the debugging prompt on the phone

---

### 10.2 Same Wi‑Fi network

| Device | Requirement |
|--------|-------------|
| Laptop | Connected to Wi‑Fi |
| Phone | **Same** Wi‑Fi — not mobile data only |

---

### 10.3 Find the PC IP address

```powershell
ipconfig
```

Look for **IPv4 Address** under your Wi‑Fi adapter, e.g. `192.168.1.9`

---

### 10.4 Test from the phone browser

On Chrome on the phone, open:

```
http://192.168.1.9:8000/api/health
```

(Replace with your real IP.)

- JSON response → connection OK ✅  
- Page does not load → see [Section 16](#16-troubleshooting)

---

### 10.5 Windows Firewall

On first run, allow Python/Uvicorn on **private networks**.

Or manually allow inbound **TCP port 8000** on the private profile.

---

### 10.6 Run the app

```powershell
cd trainmate_app
flutter devices
flutter run
```

Select your device from the list.

---

### 10.7 Alternative: USB without Wi‑Fi (`adb reverse`)

```powershell
# Backend on PC
uvicorn app.main:app --host 127.0.0.1 --port 8000

# Another terminal — phone connected via USB
adb reverse tcp:8000 tcp:8000

cd trainmate_app
flutter run
```

Then in the app: **Settings → App settings → Server address:**

```
http://127.0.0.1:8000
```

Tap **Save address**.

---

## 11. Server URL in the app

The app **auto-discovers** the backend on launch. If that fails:

1. Open **Settings**
2. **App settings**
3. Under **Backend & AI status**:
   - Tap **Auto-find server**
   - Or enter: `http://<PC_IP>:8000`
   - **Test connection** → **Save address**

The URL is stored on the device — you do not need to re-enter it every time.

---

## 12. First use — register to workout

### 12.1 Create an account

1. Tap **Create account**
2. Enter email and password
3. Verification code appears **inside the app** when `EXPOSE_VERIFICATION_CODES=true`
4. Enter the code → account activated
5. Sign in

---

### 12.2 Onboarding

1. Age, sex, height, weight
2. Choose a plan template
3. Optional “before” body photo

---

### 12.3 Test a workout

1. **Workout** tab → start a session
2. Pick an exercise manually or enable auto-classify
3. Follow: Setup → Coaching tips → Live camera
4. End session and save

---

### 12.4 Chatbot

1. Open **Chat** / coach screen
2. Ask a fitness question
3. Requires `GROQ_API_KEY` in `.env` for full AI replies

---

## 13. Optional features

| Feature | Needs | Setup |
|---------|-------|-------|
| Full chatbot | Groq API | `GROQ_API_KEY` in `.env` |
| Real email verification | SMTP or Resend | See `README.md` email section |
| Server exercise classify | ML weights + `requirements-ml.txt` | Files in `ai/models/` |
| Body progress analysis | `requirements-ml.txt` | Before + after photos |
| Streamlit prototype | `ai/requirements.txt` | `streamlit run main.py` in `ai/` |

---

## 14. Building a release APK

```powershell
cd trainmate_app
flutter build apk --release
```

Output:

```
trainmate_app/build/app/outputs/flutter-apk/app-release.apk
```

Install on a phone. The user must still reach the backend — set the server URL in app settings after install.

---

## 15. Checklists

### Before submission (team)

- [ ] `README.md` and `REPRODUCIBILITY.md` in repo root
- [ ] `trainmate_backend/.env.example` present
- [ ] Three `ai/models/` weight files included or documented
- [ ] `export_for_flutter.py` produces TFLite assets
- [ ] Backend runs with `--host 0.0.0.0`
- [ ] `ai/training_cache/` and `.env` are **not** committed
- [ ] App connects on emulator and physical phone

### For evaluator / demo

- [ ] Python 3.10/3.11 installed
- [ ] Flutter + Android Studio installed
- [ ] `pip install -r requirements.txt` succeeded
- [ ] `/api/health` returns ok
- [ ] `flutter run` launches the app
- [ ] Register + login work
- [ ] Exercise camera screen works

---

## 16. Troubleshooting

| Problem | Likely cause | Fix |
|---------|--------------|-----|
| Connection timed out | Wrong IP or different network | Same Wi‑Fi + Auto-find in app settings |
| Phone cannot open `/api/health` | Firewall or `127.0.0.1` only | `uvicorn --host 0.0.0.0` + allow Python in firewall |
| USB only, no Wi‑Fi | USB does not route HTTP | `adb reverse` or use same Wi‑Fi |
| Registration 503 | Email not configured | `EXPOSE_VERIFICATION_CODES=true` |
| `pip install` fails | Wrong Python version | Use 3.10 or 3.11 |
| `mediapipe` fails | Python 3.12+ | Install Python 3.11 |
| Auto-classify not working | No TFLite and no server ML | Run `export_for_flutter.py` or use manual mode |
| Black camera | Emulator limitation | Use a physical device |
| Backend stops right after startup | Terminal closed, Ctrl+C, or `--reload` on OneDrive | Use `.\start-window.ps1 -HostAll`; avoid `--reload` unless needed |

---

## 17. Quick command reference

### Window 1 — Backend (every session)

```powershell
cd PP\trainmate_backend
.\start-window.ps1 -HostAll
```

Or manually:

```powershell
cd PP\trainmate_backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Window 2 — App

```powershell
cd PP\trainmate_app
flutter run
```

### Emulator (manual override)

```powershell
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

### Physical phone (manual override)

```powershell
flutter run --dart-define=API_BASE_URL=http://192.168.1.9:8000
```

(Replace IP with output of `ipconfig`)

---

## Project information

| | |
|--|--|
| **Team** | Ahmed Sameh, Adham Allam, Ahmed Wael, Ibrahim Mohamed, Amira Yasser |
| **Supervisor** | Associate Professor Mohamed Ghetas |
| **Stack** | Flutter · FastAPI · TensorFlow · MediaPipe · Groq |

---

*Last updated: June 2026 — includes automatic backend URL discovery in the mobile app.*
