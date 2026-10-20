# TrainMate Mobile App (Flutter)

Flutter client for the **TrainMate** graduation project — live exercise tracking, workout plans, AI chatbot UI, body progress, and bilingual (EN/AR) interface.

> **Full setup from zero:** see **[../REPRODUCIBILITY.md](../REPRODUCIBILITY.md)** (emulator + physical device).

## Quick run

1. Start backend (from repo root):

```powershell
cd trainmate_backend
.\start.ps1
```

2. Run app:

```powershell
cd trainmate_app
flutter pub get
# Android emulator:
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
# Physical phone (same Wi‑Fi — replace with your PC IP):
flutter run --dart-define=API_BASE_URL=http://192.168.1.105:8000
```

See root README for USB `adb reverse`, release APK build, and TFLite model export.

## Key folders

| Path | Purpose |
|------|---------|
| `lib/screens/` | UI screens |
| `lib/services/` | API, auth, chatbot, workouts, plans |
| `lib/ml/` | Pose features, rep counter, form feedback |
| `assets/models/` | TFLite classifier (after `ai/export_for_flutter.py`) |
