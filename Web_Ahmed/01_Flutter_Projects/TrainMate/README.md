# TrainMate

**Graduation Project — AI-Powered Mobile Smart Gym Assistant**

> **Full setup from zero:** see **[REPRODUCIBILITY.md](REPRODUCIBILITY.md)** — install every dependency, run backend + app on emulator and physical Android, step by step.

TrainMate is a full-stack fitness application that combines **real-time pose-based exercise tracking**, **personalized workout plans**, **body-progress analysis** (before/after photos), and an **AI fitness chatbot**. The system consists of a **Flutter mobile app**, a **FastAPI backend**, and an **AI/ML pipeline** (model training, TFLite export, body analyzer, and an original Streamlit prototype).

---

## Team

| ID | Name | Main responsibility |
|----|------|---------------------|
| 222100081 | Ahmed Sameh | Flutter app + exercise classifier (ML training & on-device inference) |
| 222100194 | Adham Allam | Flutter app + exercise classifier (ML training & on-device inference) |
| B20000006 | Ahmed Wael | AI fitness chatbot (Groq / OpenRouter integration) |
| A20000011 | Ibrahim Mohamed | Live form feedback & rep counting + body before/after comparison |
| 222100305 | Amira Yasser | FastAPI backend (auth, plans, workouts, API, database) |

**Supervisor:** Associate Professor Mohamed Ghetas

---

## Table of contents

1. [Overview](#overview)
2. [Main features](#main-features)
3. [Supported exercises](#supported-exercises)
4. [Technology stack](#technology-stack)
5. [System architecture](#system-architecture)
6. [ML model pipeline](#ml-model-pipeline)
7. [Project structure](#project-structure)
8. [Prerequisites](#prerequisites)
9. [Setup — step by step](#setup--step-by-step)
10. [Running on Android emulator](#running-on-android-emulator)
11. [Running on a physical Android phone](#running-on-a-physical-android-phone)
12. [Building a release APK](#building-a-release-apk)
13. [Backend configuration (`.env`)](#backend-configuration-env)
14. [Email verification & password reset](#email-verification--password-reset)
15. [ML model files & TFLite export](#ml-model-files--tflite-export)
16. [API reference](#api-reference)
17. [Plan templates](#plan-templates)
18. [What runs on-device vs on the server](#what-runs-on-device-vs-on-the-server)
19. [Streamlit prototype (`ai/`)](#streamlit-prototype-ai)
20. [Graduation report folder](#graduation-report-folder)
21. [Documentation links](#documentation-links)
22. [What is not included in the repo](#what-is-not-included-in-the-repo)
23. [Troubleshooting](#troubleshooting)

---

## Overview

TrainMate helps users:

1. Register, verify email, and set up a fitness profile.
2. Create a workout plan from built-in templates (Strength, Muscle Gain, Weight Loss, Endurance, Mobility).
3. Perform exercises in front of the phone camera — the app detects pose, classifies the exercise, counts reps, and gives **instant form feedback**.
4. Save workout sessions to the backend (reps, duration, calories, optional AI session report).
5. Chat with an AI coach that knows the user’s plan and workout history.
6. Upload **before** and **after** body photos when completing a plan; the server analyzes progress with MediaPipe + optional vision LLM.

The mobile app talks to the backend over **REST + JWT**. Live camera tracking runs **on the phone** for low latency; chatbot, email, body analysis, and optional server-side classification run on the **backend**.

---

## Main features

| Feature | Description |
|---------|-------------|
| **Authentication** | Register, email verification, login, forgot/reset password (JWT) |
| **Onboarding** | Age, sex, height, weight, fitness goal, initial plan |
| **Workout plans** | Create/edit plans, activate one plan, track sessions vs target, completion flow |
| **Live exercise tracking** | Camera + Google ML Kit pose → rep counter + form faults |
| **Auto exercise classification** | BiLSTM model (TFLite on device, or Keras fallback on server) |
| **Form analysis** | Partial reps, hip sag/pike, shallow squat, torso lean, swinging, elbow flare, lockout, back arch |
| **Session reports** | Optional Groq-generated summary after each workout |
| **Body progress** | Before/after photo comparison with regional scores |
| **AI chatbot** | Fitness Q&A with user context (plan, sessions, body analysis) |
| **Coach insight** | Short progress tip on home screen |
| **Bilingual UI** | English and Arabic |
| **Notifications** | Local reminders (optional in settings) |
| **Speech input** | Voice-to-text in chatbot (device speech API) |

---

## Supported exercises

Only **four** exercises are supported end-to-end (training data, classifier, rep logic, backend, and app UI):

| Exercise | Label in model |
|----------|----------------|
| Squat | `squat` |
| Push-up | `push-up` |
| Shoulder press | `shoulder press` |
| Barbell biceps curl | `barbell biceps curl` |

---

## Technology stack

| Layer | Technologies |
|-------|----------------|
| **Mobile app** | Flutter 3.11+, Dart, Camera, Google ML Kit Pose Detection, TFLite Flutter |
| **Backend** | Python 3.10–3.11, FastAPI, Uvicorn, SQLAlchemy 2, SQLite, JWT |
| **ML training** | TensorFlow/Keras, BiLSTM, MediaPipe, scikit-learn (scaler, label encoder) |
| **On-device inference** | TFLite (`exercise_classifier.tflite`) |
| **Server ML (optional)** | TensorFlow/Keras `.h5` in `ai/models/` |
| **Body analysis** | MediaPipe Pose, OpenCV, optional OpenRouter vision LLM |
| **Chatbot & reports** | Groq API (`llama-3.1-8b-instant`), optional OpenRouter |
| **Email** | SMTP (Gmail, Outlook, etc.) or Resend |
| **Prototype** | Streamlit (`ai/main.py`) |

---

## System architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Flutter app (trainmate_app)                    │
│  UI · Camera · ML Kit Pose · TFLite classifier · Rep counter   │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS/HTTP REST + JWT Bearer
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  FastAPI backend (trainmate_backend)               │
│  Auth · Users · Plans · Workouts · Chat · ML · Body progress    │
│  SQLite (trainmate.db)                                           │
└────────────────────────────┬────────────────────────────────────┘
                             │ loads scripts / model weights
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         ai/ folder                               │
│  Model training · TFLite export · body_progress_analyzer.py     │
│  Streamlit demo · chatbot prototype                              │
└─────────────────────────────────────────────────────────────────┘
```

### Live workout flow (on the phone)

1. **Setup** — choose manual exercise or auto-classify; set load, sets, AI report toggle.
2. **Coaching** — static form tips before the camera opens.
3. **Live** — camera stream → ML Kit extracts 33 body landmarks every few frames.
4. **Two parallel paths from the same pose:**
   - **Classification:** 22 features per frame × 30 frames → BiLSTM → exercise label.
   - **Rep counting & feedback:** joint angles → finite-state machine → rep count + form fault messages.
5. **End session** — app sends summary to `POST /api/workouts`; backend may generate an AI report.

---

## ML model pipeline

### 1. Dataset

Training videos come from public Kaggle datasets, for example:

- [Workout/Fitness Video](https://www.kaggle.com/datasets/hasyimabdillah/workoutfitness-video)
- [Gym Workout Exercises Video](https://www.kaggle.com/datasets/philosopher0808/gym-workoutexercises-video)

### 2. Preprocessing (`ai/dataset_preprocessing.py`)

- Extract pose landmarks from videos using **MediaPipe**.
- Build sequences of **30 timesteps × 22 features** per sample.
- Save `X.npy`, `y.npy`, and label map for training.

### 3. Training (`ai/model_training.py`)

- **Architecture:** Bidirectional LSTM (3 stacked BiLSTM blocks + dense head).
- **Input shape:** `(30, 22)` — 30 frames, 22 joint-angle features per frame.
- **Output:** one of 4 exercise classes.
- **Saved artifacts** in `ai/models/`:
  - `final_forthesis_bidirectionallstm_and_encoders_exercise_classifier_model.h5`
  - `thesis_bidirectionallstm_scaler.pkl`
  - `thesis_bidirectionallstm_label_encoder.pkl`

### 4. Export for Flutter (`ai/export_for_flutter.py`)

Converts Keras + scaler + encoder to mobile assets:

```
trainmate_app/assets/models/
├── exercise_classifier.tflite   ← on-device inference
├── scaler_params.json           ← normalization (mean/scale, window size)
└── classes.json                 ← class names (already in repo)
```

> **Note:** `classes.json` and `scaler_params.json` are in the repo. Run `export_for_flutter.py` locally to generate `exercise_classifier.tflite`. Without TFLite, use **manual exercise selection** or enable **server fallback** (backend must run with ML weights in `ai/models/`).

### 5. Inference modes

| Mode | When | Where |
|------|------|-------|
| **TFLite (preferred)** | `exercise_classifier.tflite` exists in assets | Phone — no network needed during classify |
| **Server Keras** | TFLite missing but `.h5` on server | `POST /api/ml/classify` |
| **Manual** | User picks exercise in setup | No classifier needed |

The app probes `GET /api/ml/status` to decide if server ML is available.

---

## Project structure

```
PP/                                    ← repository root
├── README.md                          ← this file
├── ai/                                ← ML training, export, body analyzer, Streamlit demo
│   ├── dataset_preprocessing.py
│   ├── model_training.py
│   ├── export_for_flutter.py
│   ├── ExerciseAiTrainer.py
│   ├── body_progress_analyzer.py
│   ├── chatbot.py
│   ├── main.py                        ← Streamlit prototype entry
│   ├── models/                        ← trained weights (.h5, .pkl)
│   └── requirements.txt
├── trainmate_backend/                 ← FastAPI REST API
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/                   ← auth, users, plans, workouts, chat, ml
│   │   ├── models.py                  ← SQLAlchemy ORM
│   │   └── ...
│   ├── .env.example
│   ├── requirements.txt               ← core backend deps
│   ├── requirements-ml.txt            ← TensorFlow, MediaPipe (heavy, optional)
│   ├── start.ps1                      ← quick Windows start (use -HostAll for phone)
│   ├── start-window.ps1               ← opens backend in a new PowerShell window
│   ├── BACKEND_DOCUMENTATION.md
│   └── BACKEND_DOCUMENTATION_AR.md
├── trainmate_app/                     ← Flutter mobile client
│   ├── lib/
│   │   ├── screens/                   ← UI screens
│   │   ├── services/                  ← API, auth, chatbot, workouts, plans
│   │   ├── ml/                        ← pose features, rep counter
│   │   └── ...
│   ├── assets/models/                 ← TFLite + JSON (after export)
│   └── pubspec.yaml
└── Document/                          ← graduation report + screenshots + diagrams
```

| Folder | Role |
|--------|------|
| `ai/` | Train BiLSTM classifier, export TFLite, body progress analyzer, original Streamlit app |
| `trainmate_backend/` | JWT auth, profiles, plans, sessions, chatbot, optional server ML |
| `trainmate_app/` | Full mobile UX: onboarding, live workout, chatbot UI, settings, Arabic/English |
| `Document/` | Final GP report (`GP_Report_Semester2_G6.docx`), app screenshots, ML/backend diagrams |

---

## Prerequisites

### Required

| Tool | Version | Used for |
|------|---------|----------|
| **Python** | 3.10 or 3.11 | Backend + AI scripts |
| **Flutter SDK** | 3.11+ | Mobile app |
| **Android Studio** | Latest stable | Android SDK, emulator, optional device debugging |
| **Git** | Any recent | Clone repo |

### Android development

- Install **Android SDK** and **Android SDK Command-line Tools** via Android Studio → SDK Manager.
- Accept licenses: `flutter doctor --android-licenses`
- Verify: `flutter doctor` (Android toolchain should be OK).

### Optional but recommended

| Tool | Purpose |
|------|---------|
| **Groq API key** | Chatbot + AI session reports + coach insight |
| **Gmail App Password or Resend** | Email verification codes to real inbox |
| **OpenRouter API key** | Vision-enhanced body progress & chatbot image analysis |

---

## Setup — step by step

Run these in order on a **Windows** PC (PowerShell). Adjust paths for macOS/Linux (`source .venv/bin/activate` instead of `Activate.ps1`).

### Step 1 — Clone the repository

```powershell
git clone <your-repo-url>
cd PP
```

### Step 2 — Backend

```powershell
cd trainmate_backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` — at minimum set a strong `JWT_SECRET_KEY`. See [Backend configuration](#backend-configuration-env).

**Start the server** (must listen on all interfaces for phone access):

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Quick start (Windows only):**

```powershell
cd trainmate_backend
.\start.ps1 -HostAll          # phone on same Wi‑Fi — binds 0.0.0.0
.\start-window.ps1 -HostAll   # same, but in a separate window (recommended)
```

By default, `start.ps1` binds to `127.0.0.1` and **does not** use `--reload` (safer on OneDrive). Add `-Reload` only if you need auto-restart during backend development.

**Verify:**

- Health: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)
- Swagger docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

**Optional — ML on server** (body photo analysis + server-side classify fallback):

```powershell
pip install -r requirements-ml.txt
```

> Do **not** cancel `pip install` midway — it can break the virtual environment. Core install ~1–2 min; ML install ~10–20 min (~500 MB).

### Step 3 — ML model (TFLite for on-device classify)

If `ai/models/` contains the `.h5` and `.pkl` files:

```powershell
cd ai
pip install -r requirements-tflite-export.txt
python export_for_flutter.py
```

This writes `exercise_classifier.tflite` and `scaler_params.json` into `trainmate_app/assets/models/`.

### Step 4 — Flutter app

```powershell
cd trainmate_app
flutter pub get
flutter doctor
```

Then run for your target — see [Android emulator](#running-on-android-emulator) or [physical phone](#running-on-a-physical-android-phone).

---

## Running on Android emulator

The Android emulator maps the host machine’s `localhost` to **`10.0.2.2`**.

### 1. Start the backend on your PC

```powershell
cd trainmate_backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Create / start an AVD

- Android Studio → **Device Manager** → create a virtual device (API 30+ recommended).
- Start the emulator.

### 3. Run the Flutter app

```powershell
cd trainmate_app
flutter devices
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

### 4. Test connection

- Open the app → register or login.
- If registration works and home screen loads data, the emulator reaches the backend.

### Emulator tips

| Topic | Detail |
|-------|--------|
| **API URL** | Always `http://10.0.2.2:8000` (not `127.0.0.1`) |
| **Camera** | Emulator can use webcam as back camera; enable in AVD settings |
| **Verification code** | With `EXPOSE_VERIFICATION_CODES=true`, code appears in app + server terminal |
| **Auto URL fallback** | App auto-discovers the backend via `BackendUrlService` on launch; override in Settings → App settings |

---

## Running on a physical Android phone

The phone must reach your PC’s backend over the network. Two reliable methods:

---

### Method A — Same Wi‑Fi (recommended for demo)

#### 1. Connect phone and PC to the same Wi‑Fi

Avoid guest/isolated networks that block device-to-device traffic.

#### 2. Find your PC’s local IP

**Windows:**

```powershell
ipconfig
```

Look for **IPv4 Address** under your active adapter (e.g. `192.168.1.105` or `172.20.10.3` on iPhone hotspot).

**Example:** `192.168.1.105`

#### 3. Allow Windows Firewall (one-time)

When Windows asks to allow Python/Uvicorn on **Private networks**, click **Allow**.

Or manually allow inbound **TCP port 8000** for Private profile.

#### 4. Start backend bound to all interfaces

```powershell
cd trainmate_backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

> `--host 0.0.0.0` is **required** — `127.0.0.1` only accepts connections from the PC itself.

#### 5. Test from the phone browser

On the phone, open:

```
http://<YOUR_PC_IP>:8000/api/health
```

Example: `http://192.168.1.105:8000/api/health`

You should see JSON with `"status": "ok"`. If not, fix Wi‑Fi/firewall before running the app.

#### 6. Enable USB debugging & run Flutter

On the phone:

- **Settings → About phone** → tap Build number 7 times → Developer options.
- Enable **USB debugging**.
- Connect USB cable; accept the debugging prompt.

On PC:

```powershell
cd trainmate_app
flutter devices
flutter run --dart-define=API_BASE_URL=http://192.168.1.105:8000
```

Replace `192.168.1.105` with **your** IP.

#### 7. Wireless debugging (optional)

After first USB run:

```powershell
adb tcpip 5555
adb connect <PHONE_IP>:5555
flutter run --dart-define=API_BASE_URL=http://<PC_IP>:8000
```

---

### Method B — USB with `adb reverse` (no Wi‑Fi needed)

Forwards the phone’s localhost port 8000 to the PC’s port 8000.

```powershell
# Backend on PC (localhost is fine here)
uvicorn app.main:app --host 127.0.0.1 --port 8000

# Forward port (phone connected via USB, USB debugging on)
adb reverse tcp:8000 tcp:8000

# Run app pointing to device localhost
cd trainmate_app
flutter run --dart-define=API_BASE_URL=http://127.0.0.1:8000
```

---

### Physical device tips

| Topic | Detail |
|-------|--------|
| **Cleartext HTTP** | Enabled in `AndroidManifest.xml` (`usesCleartextTraffic=true`) for local dev |
| **Permissions** | App requests Camera, Internet, Microphone (chatbot voice) at runtime |
| **Changing network** | If you switch Wi‑Fi, your PC IP changes — update `API_BASE_URL` and rebuild/run |
| **Auto-discovery** | `BackendUrlService` scans saved URL, subnet, `10.0.2.2`, and Settings → **Auto-find server** |
| **Hotspot** | If PC shares internet via hotspot, phone uses gateway IP (often `192.168.137.1` on Windows) |

---

## Building a release APK

For submission/demo without a USB cable:

```powershell
cd trainmate_app
flutter build apk --release --dart-define=API_BASE_URL=http://YOUR_PC_OR_SERVER_IP:8000
```

Output:

```
trainmate_app/build/app/outputs/flutter-apk/app-release.apk
```

Install on phone (USB or share APK). **The phone must still reach the backend URL** baked into the build unless you deploy the backend to a public server.

For production, deploy backend to a cloud host with HTTPS and build with:

```powershell
flutter build apk --release --dart-define=API_BASE_URL=https://your-domain.com
```

---

## Backend configuration (`.env`)

Copy `trainmate_backend/.env.example` to `.env`.

| Variable | Required | Description |
|----------|----------|-------------|
| `JWT_SECRET_KEY` | **Yes** | Long random string for signing tokens |
| `DATABASE_URL` | No | Default `sqlite:///./trainmate.db` |
| `GROQ_API_KEY` | For chatbot | Groq API key for chat + session reports |
| `GROQ_MODEL` | No | Default `llama-3.1-8b-instant` |
| `EXPOSE_VERIFICATION_CODES` | Dev | `true` = show email codes in API response + terminal |
| `RESEND_API_KEY` | Email option | Resend.com API key |
| `RESEND_FROM` | Email option | Sender address |
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` / `SMTP_PASSWORD` | Email option | Gmail, Outlook, etc. |
| `SMTP_USE_TLS` | Email option | `true` for port 587 |
| `ML_MODELS_DIR` | No | Override path to `ai/models/` if not auto-detected |

Example minimal `.env` for local demo:

```env
JWT_SECRET_KEY=replace-with-a-long-random-secret-string
EXPOSE_VERIFICATION_CODES=true
GROQ_API_KEY=gsk_xxxxxxxx
```

---

## Email verification & password reset

### Development (no inbox needed)

With `EXPOSE_VERIFICATION_CODES=true` (default in `.env.example`):

- Verification / reset codes appear **inside the app** after register/forgot-password.
- The same code is printed in the **backend terminal**.

### Production / real inbox (Gmail SMTP)

1. Enable 2-Step Verification: [Google Account Security](https://myaccount.google.com/security)
2. Create App Password: [App Passwords](https://myaccount.google.com/apppasswords) → Mail → copy 16 characters.
3. In `.env`:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USER=your@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
SMTP_FROM=your@gmail.com
EXPOSE_VERIFICATION_CODES=false
```

4. Restart backend.

**Delivery order:** SMTP first → Resend → fallback to in-app/terminal codes.

> **Resend free tier** (`onboarding@resend.dev`) only delivers to the Resend account owner unless you verify your own domain.

---

## ML model files & TFLite export

### Files in `ai/models/`

| File | Purpose |
|------|---------|
| `final_forthesis_bidirectionallstm_and_encoders_exercise_classifier_model.h5` | Trained Keras model |
| `thesis_bidirectionallstm_scaler.pkl` | Feature normalization |
| `thesis_bidirectionallstm_label_encoder.pkl` | Class name encoding |

See `ai/models/REQUIRED_FILES.txt` for the checklist.

### Export command

```powershell
cd ai
pip install -r requirements-tflite-export.txt
python export_for_flutter.py
```

### After export — verify in app

1. Confirm files exist in `trainmate_app/assets/models/`.
2. Run app → Exercise screen → enable **Auto classify**.
3. If TFLite loaded, classification runs on-device without calling `/api/ml/classify`.

---

## API reference

Base URL: `http://<host>:8000/api`

Interactive docs: `http://<host>:8000/docs`

Protected routes require header: `Authorization: Bearer <JWT>`

### Auth — `/api/auth`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/register` | Create account |
| POST | `/login` | Login → JWT |
| POST | `/verify-email` | Verify with code |
| POST | `/resend-verification` | Resend code |
| POST | `/forgot-password` | Request reset code |
| POST | `/reset-password` | Set new password |

### Users — `/api/users`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/me` | Profile + plans |
| PATCH | `/me/profile` | Update age, sex, height, weight |
| PATCH | `/me/account` | Email / password |
| PATCH | `/me/plan` | Legacy plan fields |

### Plans — `/api/users/me/plans`

| Method | Path | Description |
|--------|------|-------------|
| GET | `` | List plans |
| GET | `/completed` | Completed plans |
| POST | `` | Create plan |
| PATCH | `/{plan_id}` | Update plan |
| POST | `/{plan_id}/activate` | Set active plan |
| POST | `/{plan_id}/analyze-body` | Run body comparison |
| POST | `/{plan_id}/complete` | Complete plan + after photo |
| GET | `/{plan_id}/completion` | Completion summary |
| DELETE | `/{plan_id}` | Delete plan |

### Workouts — `/api/workouts`

| Method | Path | Description |
|--------|------|-------------|
| POST | `` | Save session |
| GET | `` | List sessions |

### ML — `/api/ml`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/status` | Model files available? |
| POST | `/classify` | Server-side exercise classification |
| POST | `/body-comparison` | Before/after photo analysis |

### Chat — `/api/chat`

| Method | Path | Description |
|--------|------|-------------|
| POST | `` | Send chat message |
| POST | `/progress-feedback` | Home screen coach insight |

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Server status, email/ML flags |

Full details: `trainmate_backend/BACKEND_DOCUMENTATION.md` (English) and `BACKEND_DOCUMENTATION_AR.md` (Arabic).

---

## Plan templates

Built-in templates in `trainmate_app/lib/core/plan_templates.dart`:

| Template | Focus |
|----------|-------|
| **Strength** | Squat, shoulder press, push-up |
| **Muscle Gain** | Push-up, biceps curl, shoulder press, squat |
| **Weight Loss** | Squat, push-up |
| **Endurance** | Push-up, squat, shoulder press |
| **Mobility** | Squat, push-up |

Each plan has a **target session count**; completing sessions advances progress toward plan completion and the after-photo analysis step.

---

## What runs on-device vs on the server

| Component | Device | Server |
|-----------|--------|--------|
| Camera capture | ✅ | — |
| Pose detection (ML Kit) | ✅ | — |
| 22-feature extraction | ✅ | — |
| Rep counting & form faults | ✅ | — |
| Coaching hint strings | ✅ | — |
| Exercise classification (TFLite) | ✅ | — |
| Exercise classification (Keras fallback) | — | ✅ |
| Auth, plans, workout storage | — | ✅ |
| AI session report | — | ✅ |
| Chatbot | — | ✅ |
| Body before/after analysis | — | ✅ |
| Email verification | — | ✅ |
| Chat history storage | ✅ (local JSON) | — |

---

## Streamlit prototype (`ai/`)

The original research/demo app before Flutter:

```powershell
cd ai
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Optional: create .env with GROQ_API_KEY=...
streamlit run main.py
```

Open [http://localhost:8501](http://localhost:8501) — supports webcam/video modes, auto-classify, and chatbot. **Not required** to run the production Flutter app.

---

## Graduation report folder

`Document/` contains:

- Final report: `GP_Report_Semester2_G6.docx`
- App screenshots (`app_screens/`)
- Report diagrams and ML validation charts (`report_images/`)

Keep this folder for academic submission alongside the code repos.

---

## Documentation links

| Document | Location |
|----------|----------|
| **Reproducibility (setup A–Z)** | `REPRODUCIBILITY.md` |
| Backend (English) | `trainmate_backend/BACKEND_DOCUMENTATION.md` |
| Backend (Arabic) | `trainmate_backend/BACKEND_DOCUMENTATION_AR.md` |
| AI / Streamlit setup | `ai/README.md` |
| Model assets readme | `trainmate_app/assets/models/README.txt` |
| Env template | `trainmate_backend/.env.example` |

---

## What is not included in the repo

Generated locally — recreate with setup steps above:

| Item | Location |
|------|----------|
| Python virtual environments | `.venv/`, `ai/.venv/` |
| Flutter build cache | `trainmate_app/build/`, `.dart_tool/` |
| Gradle cache | `trainmate_app/android/.gradle/` |
| SQLite database | `trainmate_backend/trainmate.db` |
| Secrets | `trainmate_backend/.env` |
| TFLite export (optional) | `trainmate_app/assets/models/exercise_classifier.tflite` — run `export_for_flutter.py` |
| Training cache (generated) | `ai/training_cache/` — from `run_offline_training.py` |
| ML weights in repo | `ai/models/*.h5`, `*.pkl` (~3 MB total) — included for reproducibility |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **App cannot reach API** | Backend running? `--host 0.0.0.0`? Correct IP? Emulator uses `10.0.2.2`, phone uses PC LAN IP. Test `/api/health` in phone browser. |
| **Windows Firewall blocks phone** | Allow Python on Private network or open TCP 8000. |
| **Registration returns 503** | Set `EXPOSE_VERIFICATION_CODES=true` or configure SMTP/Resend in `.env`. |
| **Auto classify not working** | Run `export_for_flutter.py` OR start backend with ML weights and network reachable. |
| **Manual mode always works** | Pick exercise in setup screen — no model required. |
| **`mediapipe` install fails** | Use Python 3.10–3.11; try `pip install mediapipe==0.10.9`. |
| **Camera black screen on emulator** | Enable webcam in AVD camera settings; use a physical device for best results. |
| **Chatbot empty / error** | Set `GROQ_API_KEY` in `.env` and restart backend. |
| **Body analysis fails** | Install `requirements-ml.txt` on backend; ensure photos show full body. |
| **Wrong API URL after Wi‑Fi change** | Re-run with updated `--dart-define=API_BASE_URL=...` |
| **Backend stops immediately** | Terminal closed, Ctrl+C, or `--reload` on OneDrive sync | Use `.\start-window.ps1 -HostAll`; avoid `--reload` unless needed |
| **`pip install` corrupted venv** | Interrupted install | Delete `.venv` folder and recreate from Step 2 |

### Quick connectivity checklist (physical phone)

1. ☐ Backend terminal shows `Uvicorn running on http://0.0.0.0:8000`
2. ☐ Phone browser opens `http://<PC_IP>:8000/api/health`
3. ☐ `flutter run --dart-define=API_BASE_URL=http://<PC_IP>:8000`
4. ☐ Register → verification code visible in app or terminal

---

## License & academic use

Graduation project — Faculty submission. Do not commit `.env`, API keys, or personal data.

---

**TrainMate** · Graduation Project · FastAPI + Flutter + TensorFlow + MediaPipe + Groq
