# 🧠 AI & Full-Stack Projects — Ahmed Sameh

---

## 🩺 Featured Project: InsulinSense — Intelligent System for Insulin Resistance Diagnosis & Nutritional Management

An end-to-end intelligent healthcare solution designed to empower diabetic patients through **machine learning predictive models**, **automated optical character recognition (OCR) for clinical lab reports**, and a **personalized dietary recommendation engine**.

---

## 🌟 Core Technical Features

1. **AI Insulin Dose & Resistance Prediction**:
   - Machine learning model trained on real clinical and diagnostic datasets (`insulin_model.pkl`).
   - Automated handling of missing data via specialized imputation algorithms (`smart_imputation.py`).

2. **Automated Clinical Lab Analysis (OCR Vision)**:
   - Automated parsing of lab test images to extract vital markers (fasting blood glucose, HbA1c, etc.) directly into digital health profiles (`ocr_utils.py`).

3. **Personalized Meal Planning Engine**:
   - Precise dietary suggestions calculated dynamically based on user biomarkers and target glucose levels (`meal_engine.py`).

4. **Modern React Frontend**:
   - Single-page application built with React, featuring user authentication, interactive analytics charts, and dark/light mode support.

5. **RESTful Flask Backend**:
   - Secure RESTful APIs for user sessions, model predictions, and SQLite data persistence (`app.py`).

---

## 🛠️ Technology Stack
- **Frontend**: React.js, Modern CSS3, Charting & Analytics Components.
- **Backend**: Python Flask, SQLite (`users.db`), RESTful API architecture.
- **Machine Learning & Data**: Scikit-Learn, Pandas, NumPy, Joblib, OpenCV/Tesseract OCR.
- **Presentation**: Final project slides available in `InsulinSense/Presentation/InsulinSense_Final_Presentation.pptx`.

---

## 🚀 Quick Start Guide

### 1. Run the Backend (Flask):
```bash
cd InsulinSense
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix:
source venv/bin/activate

pip install -r requirements.txt
python app.py
```
The API server runs on: `http://localhost:5000`

### 2. Run the Frontend (React):
```bash
cd InsulinSense/insulin-frontend
npm install
npm start
```
The web dashboard opens at: `http://localhost:3000`
