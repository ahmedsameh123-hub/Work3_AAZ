import pandas as pd
import numpy as np

# ================= Load Files =================
labs = pd.read_csv("labs.csv")
exam = pd.read_csv("examination.csv")
demo = pd.read_csv("demographic.csv")

# ================= Select Columns =================
labs = labs[["SEQN", "LBXSGL", "LBDINSI", "LBXTR", "LBDHDD", "LBXGH"]]
exam = exam[["SEQN", "BMXBMI", "BMXWAIST", "BPXSY1", "BPXDI1"]]
demo = demo[["SEQN", "RIDAGEYR"]]

# ================= Merge =================
df = labs.merge(exam, on="SEQN").merge(demo, on="SEQN")

df.columns = ["SEQN", "Glucose", "Insulin", "Triglycerides", "HDL",
              "HbA1c", "BMI", "Waist", "SystolicBP", "DiastolicBP", "Age"]

# ================= Convert Insulin Units =================
# NHANES: pmol/L → uIU/mL (divide by 6.945)
df["Insulin"] = df["Insulin"] / 6.945

# ================= Clean =================
df = df.dropna()
df = df[(df["Glucose"] > 0) & (df["Insulin"] > 0) & (df["HDL"] > 0) & (df["BMI"] > 0)]
df = df[(df["Insulin"] < 150) & (df["Glucose"] < 500)]
df = df[df["Age"] >= 18]   # Adults only — HOMA-IR thresholds differ for children

print("Shape after cleaning:", df.shape)

# ================= Feature Engineering =================
df["TG_HDL_ratio"] = df["Triglycerides"] / df["HDL"].replace(0, 1)

# ================= Medical Multi-Criteria Classification =================
def medical_classify(row):
    score = 0
    homa = (row["Glucose"] * row["Insulin"]) / 405

    # HOMA-IR (weight: 4 pts)
    if homa > 5:       score += 4
    elif homa > 3:     score += 3
    elif homa >= 2:    score += 2

    # Fasting glucose (weight: 2 pts) — ADA cutoffs
    if row["Glucose"] >= 126:    score += 2
    elif row["Glucose"] >= 100:  score += 1

    # HbA1c (weight: 2 pts) — ADA cutoffs
    if row["HbA1c"] >= 6.5:     score += 2
    elif row["HbA1c"] >= 5.7:   score += 1

    # BMI (weight: 1 pt)
    if row["BMI"] >= 30:         score += 1

    # TG/HDL ratio (weight: 1 pt) — metabolic syndrome marker
    tg_hdl = row["Triglycerides"] / row["HDL"] if row["HDL"] > 0 else 0
    if tg_hdl >= 3:              score += 1

    # HDL (weight: 1 pt)
    if row["HDL"] < 40:          score += 1

    # Waist circumference (weight: 1 pt)
    if row["Waist"] > 95:        score += 1

    if score <= 2:   return "Normal"
    elif score <= 6: return "Mild"
    else:            return "Severe"

df["Target"] = df.apply(medical_classify, axis=1)

print("\nClass distribution:")
print(df["Target"].value_counts())

# ================= Save =================
df.to_csv("final_dataset.csv", index=False)
print("\nColumns:", list(df.columns))
print("\nDone! final_dataset.csv saved.")
