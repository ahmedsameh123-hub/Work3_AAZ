import joblib
import pandas as pd

model = joblib.load("insulin_model.pkl")

print("=" * 45)
print("   InsulinSense — Insulin Resistance Test")
print("=" * 45)
print("Note: Insulin must be in uIU/mL units\n")

# ================= Clinical Inputs =================
glucose = float(input("Enter Glucose (mg/dL): "))
insulin = float(input("Enter Insulin (uIU/mL): "))
hba1c   = float(input("Enter HbA1c (%): "))
bmi     = float(input("Enter BMI: "))
waist   = float(input("Enter Waist (cm): "))
tg      = float(input("Enter Triglycerides (mg/dL): "))
hdl     = float(input("Enter HDL (mg/dL): "))
sbp     = float(input("Enter Systolic BP (mmHg): "))
dbp     = float(input("Enter Diastolic BP (mmHg): "))
age     = float(input("Enter Age (years): "))

# Age warning
if age < 18:
    print("\n  Warning: Results may be less accurate for individuals under 18.")

# ================= Lifestyle Inputs =================
def get_choice(prompt, options):
    while True:
        print("\n" + prompt)
        for key, value in options.items():
            print(f"  {key} - {value}")
        choice = input("Choose number: ")
        if choice in options:
            return options[choice]
        print("Invalid choice, try again.")

print("\n--- Lifestyle Questions ---")

activity = get_choice("Physical activity level:",
    {"1": "low", "2": "moderate", "3": "high"})

diet = get_choice("Diet quality:",
    {"1": "healthy", "2": "average", "3": "bad"})

family = get_choice("Family history of diabetes or insulin resistance:",
    {"1": "yes", "2": "no"})

sleep = get_choice("Sleep quality:",
    {"1": "good", "2": "poor"})

pcos = get_choice("Do you have PCOS?",
    {"1": "yes", "2": "no"})

constant_hunger = get_choice("Do you experience constant hunger?",
    {"1": "yes", "2": "no"})

post_meal_sleepiness = get_choice("Do you feel sleepy after meals?",
    {"1": "yes", "2": "no"})

neck_darkening = get_choice("Do you have darkening around the neck (Acanthosis Nigricans)?",
    {"1": "yes", "2": "no"})

# ================= Calculations =================
tg_hdl_ratio = tg / hdl if hdl != 0 else 0
homa_ir      = (glucose * insulin) / 405

# ================= Prepare Data (matches model feature order) =================
data = pd.DataFrame([{
    "Glucose":       glucose,
    "Insulin":       insulin,
    "HbA1c":         hba1c,
    "BMI":           bmi,
    "Waist":         waist,
    "Triglycerides": tg,
    "HDL":           hdl,
    "TG_HDL_ratio":  tg_hdl_ratio,
    "SystolicBP":    sbp,
    "DiastolicBP":   dbp,
    "Age":           age
}])

# ================= Model Prediction =================
prediction = model.predict(data)[0]

# ================= HOMA Classification (3 levels — matches model) =================
if homa_ir < 2:
    homa_status = "Normal"
elif homa_ir <= 5:
    homa_status = "Mild"
else:
    homa_status = "Severe"

# ================= Key Factors =================
def explain(homa_ir):
    reasons = []

    if homa_ir >= 2:
        reasons.append("Reduced sensitivity to insulin detected (HOMA-IR elevated)")
    if insulin > 25:
        reasons.append("High insulin levels detected")
    if glucose >= 100:
        reasons.append("Elevated fasting blood sugar")
    if hba1c > 5.7:
        reasons.append("Elevated long-term blood sugar (HbA1c)")
    if bmi > 30:
        reasons.append("High BMI may affect insulin response")
    if tg_hdl_ratio > 3:
        reasons.append("Unhealthy TG/HDL ratio — metabolic syndrome marker")
    if hdl < 40:
        reasons.append("Low HDL cholesterol")
    if constant_hunger == "yes":
        reasons.append("Frequent hunger may indicate insulin imbalance")
    if post_meal_sleepiness == "yes":
        reasons.append("Sleepiness after meals suggests glucose spikes")
    if neck_darkening == "yes":
        reasons.append("Skin darkening (Acanthosis Nigricans) linked to insulin resistance")
    if pcos == "yes":
        reasons.append("PCOS is strongly associated with insulin resistance")
    if family == "yes":
        reasons.append("Family history increases risk")

    if not reasons:
        reasons = ["No significant risk factors detected — healthy metabolic profile"]

    return reasons[:4]

reasons = explain(homa_ir)

# ================= Lifestyle Score =================
def lifestyle_score():
    score = 0

    if activity == "low":          score += 1
    if diet == "bad":              score += 1
    if sleep == "poor":            score += 1
    if family == "yes":            score += 1
    if pcos == "yes":              score += 2
    if constant_hunger == "yes":   score += 1
    if post_meal_sleepiness == "yes": score += 1
    if neck_darkening == "yes":    score += 2

    if score <= 2:   return "Excellent Lifestyle"
    elif score <= 5: return "Needs Improvement"
    else:            return "Needs Urgent Changes"

life_result = lifestyle_score()

# ================= Summary =================
if homa_status == "Normal":
    summary = "Your results indicate normal insulin sensitivity."
elif homa_status == "Mild":
    summary = "Your results suggest early to moderate insulin resistance."
else:
    summary = "Severe insulin resistance detected. Please consult a healthcare professional."

# ================= OUTPUT =================
print("\n" + "=" * 45)
print("               RESULTS")
print("=" * 45)
print(f"HOMA-IR Value:      {round(homa_ir, 2)}")
print(f"HOMA-IR Level:      {homa_status}")
print(f"Model Prediction:   {prediction}")
print(f"\nSummary: {summary}")

print("\nKey Risk Factors:")
for r in reasons:
    print(f"  - {r}")

print(f"\nLifestyle Status:   {life_result}")
print("=" * 45)