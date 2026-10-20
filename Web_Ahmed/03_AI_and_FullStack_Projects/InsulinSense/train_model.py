import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.utils.class_weight import compute_class_weight
import joblib

# ================= Load Data =================
df = pd.read_csv("final_dataset.csv")

print("Class distribution:")
print(df["Target"].value_counts())
print()
print("Age range:", df["Age"].min(), "-", df["Age"].max(), "(adults only)")
print()

# ================= Features =================

FEATURES = [
    "Glucose",        # Fasting blood glucose (mg/dL)
    "Insulin",        # Fasting insulin (uIU/mL)
    "HbA1c",          # Glycated hemoglobin (%)
    "BMI",            # Body mass index
    "Waist",          # Waist circumference (cm)
    "Triglycerides",  # Triglycerides (mg/dL)
    "HDL",            # HDL cholesterol (mg/dL)
    "TG_HDL_ratio",   # TG/HDL ratio
    "SystolicBP",     # Systolic blood pressure (mmHg)
    "DiastolicBP",    # Diastolic blood pressure (mmHg)
    "Age"             # Age in years
]

X = df[FEATURES]
y = df["Target"]

print("Features used:", FEATURES)
print()

# ================= Handle Class Imbalance =================
classes = np.unique(y)
weights = compute_class_weight(class_weight="balanced", classes=classes, y=y)
class_weight_dict = dict(zip(classes, weights))
print("Class weights:", {k: round(v, 3) for k, v in class_weight_dict.items()})

# ================= Split =================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ================= Train =================
model = RandomForestClassifier(
    n_estimators=300,
    max_depth=10,
    min_samples_split=10,
    min_samples_leaf=5,
    class_weight="balanced",
    random_state=42
)
model.fit(X_train, y_train)

# ================= Cross Validation =================
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(model, X, y, cv=cv, scoring="accuracy")
print(f"\nCross-Validation Accuracy: {cv_scores.mean():.4f} +/- {cv_scores.std():.4f}")

# ================= Evaluation =================
y_pred = model.predict(X_test)
print(f"Train Accuracy: {model.score(X_train, y_train):.4f}")
print(f"Test  Accuracy: {accuracy_score(y_test, y_pred):.4f}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# ================= Feature Importance =================
feat_imp = pd.DataFrame({
    "Feature": FEATURES,
    "Importance": model.feature_importances_
}).sort_values("Importance", ascending=False)

print("\nFeature Importance:")
print(feat_imp.to_string(index=False))

print(f"\nModel classes: {model.classes_}")
print(f"Model feature order: {list(model.feature_names_in_)}")

# ================= Save =================
joblib.dump(model, "insulin_model.pkl")
print("\nModel saved as insulin_model.pkl")
