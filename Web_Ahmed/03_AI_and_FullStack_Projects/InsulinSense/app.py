import os
from urllib import response
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
import sqlite3
import random
import time
import smtplib
from email.mime.text import MIMEText
from werkzeug.security import generate_password_hash, check_password_hash
from ocr_utils import run_ocr
from smart_imputation import resolve_missing_fields

# ================= OTP Storage =================
otp_storage = {}

# ================= Database Init =================
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    phone TEXT,
    gender TEXT,
    dob TEXT,
    address TEXT,
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
 """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        patient_name TEXT,
        patient_age REAL,
        patient_height REAL,
        patient_weight REAL,
        patient_gender TEXT,
        prediction TEXT,
        risk_score REAL,
        homa_ir REAL,
        activity_level TEXT,
        diet_pattern TEXT,
        sleep_quality TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
 """)
    conn.commit()
    # Migration: add columns for existing databases
    for col_def in ["phone TEXT", "gender TEXT", "dob TEXT", "address TEXT", "bio TEXT"]:
        try:
             cursor.execute(f"ALTER TABLE users ADD COLUMN {col_def}")
        except Exception:
             pass
    conn.commit()
    conn.close()

# ================= App Setup =================
app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = "insulinsense-secret-key"
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB limit for uploads
app.config['CORS_HEADERS'] = 'Content-Type'
init_db()
# ================= Send Email =================
def send_email(to_email, otp):
    sender_email = os.environ.get("GMAIL_USER", "jjanamahmoud3232@gmail.com")
    sender_password = os.environ.get("GMAIL_PASSWORD")
    if not sender_password:
        raise ValueError("GMAIL_PASSWORD environment variable is not set")
    msg = MIMEText(f"Your OTP is: {otp}\n\nThis OTP is valid for 5 minutes.")
    msg["Subject"] = "Reset Password OTP"
    msg["From"] = sender_email
    msg["To"] = to_email
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()

# ================= Load Model =================
try:
    model = joblib.load("insulin_model.pkl")
except FileNotFoundError as e:
    raise RuntimeError("Model file insulin_model.pkl not found.") from e

# ================= Register =================
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required"}), 400
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "This email is already registered"}), 409
    hashed_password = generate_password_hash(password)
    cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                   (name, email, hashed_password))
    conn.commit()
    conn.close()
    return jsonify({"message": "User registered successfully"}), 201

# ================= Login =================
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON request body"}), 400
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cursor.fetchone()
    conn.close()
    if user and check_password_hash(user[3], password):
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"error": "Invalid email or password"}), 401

# ================= Forgot Password =================
@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid JSON request body"}), 400
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cursor.fetchone()
    conn.close()
    if not user:
        return jsonify({"error": "Email not found"}), 404
    if email in otp_storage:
        elapsed = time.time() - otp_storage[email]["time"]
        if elapsed < 60:
            remaining = int(60 - elapsed)
            return jsonify({"error": f"Please wait {remaining} seconds before requesting a new OTP"}), 429
    otp = str(random.randint(100000, 999999))
    otp_storage[email] = {"otp": otp, "time": time.time(), "attempts": 0}
    send_email(email, otp)
    return jsonify({"message": "OTP sent"}), 200

# ================= Verify OTP =================
@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    email = data.get("email")
    otp = data.get("otp")

    if email not in otp_storage:
        return jsonify({"error": "No OTP found"}), 400

    if time.time() - otp_storage[email]["time"] > 300:
        del otp_storage[email]
        return jsonify({"error": "OTP expired"}), 400

    if otp_storage[email]["attempts"] >= 5:
        del otp_storage[email]
        return jsonify({"error": "Too many failed attempts. Please request a new OTP"}), 429

    if otp != otp_storage[email]["otp"]:
        otp_storage[email]["attempts"] += 1
        remaining = 5 - otp_storage[email]["attempts"]
        return jsonify({"error": f"Invalid OTP. {remaining} attempts remaining"}), 400

    otp_storage[email]["verified"] = True

    return jsonify({"message": "OTP verified"}), 200

# ================= Reset Password =================
@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.json


    if not data:
        return jsonify({"error": "Invalid JSON request body"}), 400

    email = data.get("email")
    new_password = data.get("new_password")
    otp = data.get("otp")

    if not email or not otp or not new_password:
        return jsonify({"error": "Email, OTP, and new password are required"}), 400

    if email not in otp_storage:
        return jsonify({"error": "No OTP request found"}), 400

    if time.time() - otp_storage[email]["time"] > 300:
        del otp_storage[email]
        return jsonify({"error": "OTP expired"}), 400

    if not otp_storage[email].get("verified"):
        return jsonify({"error": "OTP not verified"}), 400

    if otp_storage[email]["otp"] != otp:
        return jsonify({"error": "Invalid OTP"}), 400

    if len(new_password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    hashed_password = generate_password_hash(new_password)

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password=? WHERE email=?",
        (hashed_password, email)
    )
    conn.commit()
    conn.close()

    del otp_storage[email]

    return jsonify({"message": "Password reset successful"}), 200
# ================= Predict =================
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request data."}), 400

    patient_name   = str(data.get("PatientName", "")).strip()
    patient_age    = data.get("Age", "")
    patient_height = data.get("Height", "")
    patient_weight = data.get("Weight", "")
    patient_gender = str(data.get("Gender", "")).strip().lower()

    # ── Smart Imputation ──────────────────────────────────────────────────────
    filled, estimated_fields, missing_fields = resolve_missing_fields(data)

    LAB_REQUIRED = ["Glucose", "Insulin", "HbA1c", "HDL", "Triglycerides"]

    truly_missing = [f for f in missing_fields if f in LAB_REQUIRED]

    if truly_missing:
        return jsonify({
            "error": "Some lab values are required and could not be estimated.",
            "missing_fields": truly_missing,
            "hint": "Please enter these values manually: " + ", ".join(truly_missing)
        }), 400

    try:
        try:
            glucose = float(filled["Glucose"])
            insulin = float(filled["Insulin"])
            hba1c   = float(filled["HbA1c"])
            bmi     = float(filled["BMI"])
            waist   = float(filled["Waist"])
            sbp     = float(filled["SystolicBP"])
            dbp     = float(filled["DiastolicBP"])
            tg      = float(filled["Triglycerides"])
            hdl     = float(filled["HDL"])
            age     = float(filled["Age"])
        except (ValueError, TypeError) as exc:
            return jsonify({"error": f"Numeric conversion error: {exc}"}), 400

        age_warning = None
        if age < 18:
            age_warning = "Results may be less accurate for individuals under 18. Please consult a healthcare professional."

        tg_hdl_ratio = tg / hdl if hdl != 0 else 0
        homa_ir      = (glucose * insulin) / 405

        input_data = pd.DataFrame([[
            glucose, insulin, hba1c, bmi,
            waist, tg, hdl, tg_hdl_ratio, sbp, dbp, age
        ]], columns=[
            "Glucose", "Insulin", "HbA1c", "BMI", "Waist",
            "Triglycerides", "HDL", "TG_HDL_ratio",
            "SystolicBP", "DiastolicBP", "Age"
        ])

        prediction = model.predict(input_data)[0]

        # ── Risk Score ────────────────────────────────────────────────────────
        risk_score = 0
        if homa_ir > 5:        risk_score += 35
        elif homa_ir > 3:      risk_score += 25
        elif homa_ir > 2:      risk_score += 12
        if insulin > 50:       risk_score += 10
        elif insulin > 25:     risk_score += 5
        if bmi > 35:           risk_score += 15
        elif bmi > 30:         risk_score += 10
        if glucose > 140:      risk_score += 12
        elif glucose > 100:    risk_score += 6
        if hba1c > 6.5:        risk_score += 12
        elif hba1c > 5.7:      risk_score += 6
        if hdl < 40:           risk_score += 8
        elif hdl < 50:         risk_score += 4
        if tg_hdl_ratio > 5:   risk_score += 8
        elif tg_hdl_ratio > 3: risk_score += 4
        if sbp > 140:          risk_score += 5
        risk_score = min(risk_score, 100)

        # ── HOMA Classification ───────────────────────────────────────────────
        if homa_ir < 2:    homa_level = "Normal"
        elif homa_ir <= 5: homa_level = "Mild"
        else:              homa_level = "Severe"

        # ── Lifestyle ─────────────────────────────────────────────────────────
        activity = str(data.get("activity", "moderate")).lower().strip()
        diet     = str(data.get("diet",     "average")).lower().strip()
        family   = str(data.get("family",   "no")).lower().strip()
        sleep    = str(data.get("sleep",    "good")).lower().strip()
        pcos     = str(data.get("pcos",     "no")).lower().strip()
        hunger   = str(data.get("hunger",   "no")).lower().strip()
        sleepy   = str(data.get("sleepy",   "no")).lower().strip()
        neck     = str(data.get("neck",     "no")).lower().strip()

        score = 0
        if activity == "low":  score += 1
        if diet == "poor":     score += 1
        if family == "yes":    score += 1
        if sleep == "poor":    score += 1
        if pcos == "yes":      score += 2
        if hunger == "yes":    score += 1
        if sleepy == "yes":    score += 1
        if neck == "yes":      score += 2

        if score <= 2:
            lifestyle_status  = "Excellent Lifestyle"
            lifestyle_message = "Your lifestyle appears healthy. Keep it up!"
        elif score <= 5:
            lifestyle_status  = "Needs Improvement"
            lifestyle_message = "Your lifestyle is fairly good, but some improvements are recommended."
        else:
            lifestyle_status  = "Needs Urgent Changes"
            lifestyle_message = "Your lifestyle may be negatively affecting your condition and needs immediate improvement."

        if risk_score >= 70:
            lifestyle_status  = "Needs Urgent Changes"
            lifestyle_message = "Even if your lifestyle seems good, your clinical data indicates serious risk. Immediate action is needed."
        elif risk_score >= 40 and lifestyle_status == "Excellent Lifestyle":
            lifestyle_status  = "Needs Improvement"
            lifestyle_message = "Your lifestyle is good, but your health indicators suggest some improvements are needed."

        # ── Reasons ───────────────────────────────────────────────────────────
        reasons = []
        if homa_ir >= 2:     reasons.append("Reduced sensitivity to insulin detected")
        if insulin > 25:     reasons.append("High insulin levels")
        if glucose >= 100:   reasons.append("Elevated blood sugar")
        if bmi > 30:         reasons.append("High BMI affecting insulin sensitivity")
        if tg_hdl_ratio > 3: reasons.append("Unhealthy lipid profile")
        if hba1c > 5.7:      reasons.append("Elevated long-term blood sugar (HbA1c)")
        if hdl < 40:         reasons.append("Low HDL cholesterol")
        if family == "yes":  reasons.append("Family history increases risk")
        if hunger == "yes":  reasons.append("Frequent hunger (possible insulin imbalance)")
        if sleepy == "yes":  reasons.append("Sleepiness after meals (glucose spikes)")
        if neck == "yes":    reasons.append("Dark neck linked to insulin resistance")
        if pcos == "yes":    reasons.append("PCOS linked to insulin resistance")
        if sbp > 140:        reasons.append("High blood pressure")
        reasons = reasons[:4]

        # ── Summary ───────────────────────────────────────────────────────────
        if str(prediction) == "Normal":
            summary = "Your results indicate normal insulin sensitivity."
        elif str(prediction) == "Mild":
            summary = "Your results suggest early to moderate insulin resistance."
        else:
            summary = "Severe insulin resistance detected. Please consult a healthcare professional."

        # ── Save to DB ────────────────────────────────────────────────────────
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO predictions (
                user_email, patient_name, patient_age,
                patient_height, patient_weight, patient_gender,
                prediction, risk_score, homa_ir,
                activity_level, diet_pattern, sleep_quality
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("email"), patient_name, patient_age,
            patient_height, patient_weight, patient_gender,
            prediction, risk_score, homa_ir,
            activity, diet, sleep,
        ))
        conn.commit()
        conn.close()

        # ── Response ──────────────────────────────────────────────────────────
        response = {
            "status":           str(prediction) + " Insulin Resistance",
            "homa_level":       homa_level,
            "risk_score":       risk_score,
            "summary":          summary,
            "lifestyle": {
                "status":       lifestyle_status,
                "message":      lifestyle_message,
            },
            "key_factors":      reasons,
            "homa_ir":          round(homa_ir, 2),
            "model_prediction": str(prediction),
        }

        if estimated_fields:
            response["estimated_fields"] = estimated_fields
            response["imputation_note"] = (
                "Some values were not found in your report and were estimated or "
                "set to typical defaults. Results may be slightly less precise — "
                "consider entering these values manually for better accuracy."
            )

        if age_warning:
            response["warning"] = age_warning

        return jsonify(response)

    except KeyError as e:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ================= User History =================
@app.route("/user-history/<email>", methods=["GET"])
def user_history(email):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT prediction, risk_score, homa_ir, created_at,
        activity_level, diet_pattern, sleep_quality
        FROM predictions WHERE user_email = ? ORDER BY created_at DESC
    """, (email,))
    rows = cursor.fetchall()
    conn.close()
    history = [{"prediction": r[0], "risk_score": r[1], "homa_ir": r[2], "created_at": r[3]}
               for r in rows]
    return jsonify({
        "history": history,
        "total_predictions": len(history),
        "latest_prediction": history[0] if history else None
    })

# ================= Dashboard =================
@app.route("/dashboard/<email>", methods=["GET"])
def dashboard(email):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT prediction, risk_score, homa_ir, created_at,
               patient_name, patient_age, patient_height, patient_weight,
               activity_level, diet_pattern, sleep_quality
        FROM predictions WHERE user_email = ? ORDER BY created_at ASC
    """, (email,))
    rows = cursor.fetchall()
    cursor.execute("SELECT name FROM users WHERE email = ?", (email,))
    user_row = cursor.fetchone()
    conn.close()

    user_name = user_row[0] if user_row else "User"

    if not rows:
        return jsonify({
            "user_name": user_name, "total_assessments": 0,
            "latest_prediction": None, "latest_risk_score": None,
            "latest_homa_ir": None, "risk_change": None,
            "homa_trend": [], "risk_trend": [], "history": []
        })

    history = [{
        "prediction": r[0], "risk_score": r[1], "homa_ir": r[2], "created_at": r[3],
        "patient_name": r[4], "patient_age": r[5], "patient_height": r[6],
        "patient_weight": r[7], "activity_level": r[8], "diet_pattern": r[9], "sleep_quality": r[10]
    } for r in rows]

    latest = history[-1]
    risk_change = None
    if len(history) >= 2:
        risk_change = round(latest["risk_score"] - history[-2]["risk_score"], 1)

    latest_lifestyle = {
        "activity": latest.get("activity_level", "moderate"),
        "diet": latest.get("diet_pattern", "average"),
        "sleep": latest.get("sleep_quality", "good")
    }

    return jsonify({
        "patient_name": latest["patient_name"],
        "patient_age": latest["patient_age"],
        "patient_height": latest["patient_height"],
        "patient_weight": latest["patient_weight"],
        "lifestyle_data": latest_lifestyle,
        "user_name": user_name,
        "total_assessments": len(history),
        "latest_prediction": latest["prediction"],
        "latest_risk_score": latest["risk_score"],
        "latest_homa_ir": round(latest["homa_ir"], 2),
        "risk_change": risk_change,
        "homa_trend": [{"week": r["created_at"][:10], "value": round(r["homa_ir"], 2)}
                       for r in history[-4:]],
        "risk_trend": [{"label": f"Assessment {i+1}", "value": r["risk_score"]}
                       for i, r in enumerate(history[-6:])],
        "history": list(reversed(history))
    })

# ================= Meal Plan =================
from meal_engine import (
    generate_meal_plan, save_meal_plan, get_latest_meal_plan,
    get_dashboard_meal_summary,
    save_user_diet_preference, get_user_diet_preference,
)

def _resolve_patient(email):
    if not email:
        return {}
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT patient_weight, patient_height, patient_age,
                   patient_gender, activity_level, prediction
            FROM predictions WHERE user_email = ?
            ORDER BY created_at DESC LIMIT 1
        """, (email,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {"weight": row[0], "height": row[1], "age": row[2],
                    "gender": row[3], "activity_level": row[4] or "moderate",
                    "severity": row[5] or "Mild"}
    except Exception:
        pass
    return {}

@app.route("/meal-plan", methods=["POST", "GET"])
def meal_plan():
    if request.method == "GET":
        email  = request.args.get("email", "")
        data   = {}
        cached = request.args.get("cached", "false").lower() == "true"
    else:
        data   = request.get_json() or {}
        email  = data.get("email", "")
        cached = bool(data.get("cached", False))

    if cached and email:
        saved = get_latest_meal_plan(email)
        patient = _resolve_patient(email)
        if saved and patient:
            if saved.get("severity") == patient.get("severity"):
                return jsonify(saved), 200

    patient    = _resolve_patient(email)
    saved_diet = get_user_diet_preference(email) if email else "omnivore"
    diet = str(data.get("diet", saved_diet) or "omnivore").lower()

    if email and data.get("diet"):
        try:
            save_user_diet_preference(email, diet)
        except Exception:
            pass

    _sev_map = {"normal": "Normal", "mild": "Mild", "severe": "Severe",
                "Normal": "Normal", "Mild": "Mild",  "Severe": "Severe"}

    weight   = float(data.get("weight",       patient.get("weight",       80)))
    height   = float(data.get("height",       patient.get("height",       170)))
    age      = float(data.get("age",          patient.get("age",          30)))
    gender   = str(data.get("gender",         patient.get("gender",       "male")))
    activity = str(data.get("activity_level", patient.get("activity_level","moderate")))
    severity = _sev_map.get(str(data.get("severity", patient.get("severity", "Mild"))), "Mild")

    try:
        plan = generate_meal_plan(
            weight=weight, height=height, age=age,
            gender=gender, activity_level=activity, severity=severity,
            diet=diet, email=email,
        )
        if email:
            try:
                save_meal_plan(email, plan)
            except Exception:
                pass
        return jsonify(plan), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/meal-plan/latest", methods=["GET"])
def meal_plan_latest():
    email = request.args.get("email", "")
    if not email:
        return jsonify({"error": "email required"}), 400
    saved = get_latest_meal_plan(email)
    if saved:
        return jsonify(saved), 200
    return jsonify({"error": "No saved plan found"}), 404

@app.route("/meal-plan/dashboard-summary", methods=["GET"])
def meal_plan_dashboard_summary():
    email = request.args.get("email", "")
    if not email:
        return jsonify({"has_plan": False}), 200
    summary = get_dashboard_meal_summary(email)
    if summary:
        return jsonify(summary), 200
    return jsonify({"has_plan": False}), 200

@app.route("/user/diet-preference", methods=["GET", "POST"])
def diet_preference():
    if request.method == "GET":
        email = request.args.get("email", "")
        pref  = get_user_diet_preference(email) if email else "omnivore"
        return jsonify({"diet": pref}), 200
    else:
        data  = request.get_json() or {}
        email = data.get("email", "")
        diet  = str(data.get("diet", "omnivore")).lower()
        if email:
            save_user_diet_preference(email, diet)
        return jsonify({"diet": diet, "saved": True}), 200

# ================= OCR Upload =================
@app.route("/ocr-upload", methods=["POST"])
def ocr_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    allowed_types = {"image/jpeg", "image/jpg", "image/png",
                     "image/tiff", "image/bmp", "application/pdf"}
    mime_type = file.content_type or ""
    if mime_type not in allowed_types:
        name = file.filename.lower()
        if name.endswith(".pdf"):              mime_type = "application/pdf"
        elif name.endswith((".jpg", ".jpeg")): mime_type = "image/jpeg"
        elif name.endswith(".png"):            mime_type = "image/png"
        elif name.endswith((".tif", ".tiff")): mime_type = "image/tiff"
        elif name.endswith(".bmp"):            mime_type = "image/bmp"
        else:
            return jsonify({"error": "Unsupported file type. Please upload an image or PDF."}), 400

    try:
        file_bytes = file.read()
        results    = run_ocr(file_bytes, mime_type)
        return jsonify(results), 200
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"OCR processing failed: {str(e)}"}), 500

# ================= Get Profile =================
@app.route('/profile/<email>', methods=['GET'])
def get_profile(email):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, email, phone, gender, dob, address, bio, created_at FROM users WHERE email=?", (email,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "name": row[0], "email": row[1], "phone": row[2] or "",
        "gender": row[3] or "", "dob": row[4] or "",
        "address": row[5] or "", "bio": row[6] or "",
        "created_at": row[7] or ""
    })

# ================= Update Profile =================
@app.route('/profile/update', methods=['POST'])
def update_profile():
    data = request.json
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email required"}), 400
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users SET name=?, phone=?, gender=?, dob=?, address=?, bio=?
        WHERE email=?
    """, (
        data.get("name", ""),
        data.get("phone", ""),
        data.get("gender", ""),
        data.get("dob", ""),
        data.get("address", ""),
        data.get("bio", ""),
        email
    ))
    conn.commit()
    conn.close()
    return jsonify({"message": "Profile updated successfully"})

# ================= Delete Account =================
@app.route('/profile/delete', methods=['POST'])
def delete_account():
    data = request.json
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email required"}), 400
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM predictions WHERE user_email=?", (email,))
    cursor.execute("DELETE FROM users WHERE email=?", (email,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Account deleted"})
# ================= Run =================
if __name__ == "__main__":
    app.run(debug=True)
