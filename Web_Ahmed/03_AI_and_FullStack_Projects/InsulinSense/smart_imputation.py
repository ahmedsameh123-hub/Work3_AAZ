
# ── Typical population medians (NHANES-based, adults 18-65) ─────────────────
POPULATION_MEDIANS = {
    "Waist": 88.0,
    "SystolicBP": 120.0,
    "DiastolicBP": 78.0,

    "HbA1c": 5.4,
    "HDL": 50.0,
    "Triglycerides": 120.0,
}

# Fields that MUST come from lab results — cannot be estimated
REQUIRED_LAB_FIELDS = [
    "Glucose",
    "Insulin"
]


# Fields we can estimate from other available data
ESTIMABLE_FIELDS = ["BMI", "Waist", "SystolicBP", "DiastolicBP"]


def _estimate_bmi(height_cm: float, weight_kg: float) -> float | None:
    """BMI = weight(kg) / height(m)^2"""
    if height_cm and weight_kg and height_cm > 0:
        h_m = height_cm / 100.0
        bmi = weight_kg / (h_m ** 2)
        return round(bmi, 1)
    return None


def _estimate_waist_from_bmi(bmi: float, gender: str) -> float:
    """
    Rough waist estimate from BMI using regression approximations.
    Reference: Lean et al. (1996), adapted for population averages.
    Not used for diagnosis — just for model input when truly unavailable.
    """
    gender = (gender or "").lower()
    if gender in ("female", "f", "woman"):
        # Women: waist ≈ 2.05 × BMI + 27
        waist = 2.05 * bmi + 27.0
    else:
        # Men: waist ≈ 2.35 × BMI + 20
        waist = 2.35 * bmi + 20.0
    return round(min(max(waist, 55.0), 160.0), 1)  # clamp to sane range


def resolve_missing_fields(data: dict) -> tuple[dict, list[str], list[str]]:
    """
    Parameters
    ----------
    data : dict — raw request JSON from the frontend
        Expected keys (all optional except lab fields):
            Glucose, Insulin, HbA1c, BMI, Waist,
            Triglycerides, HDL, SystolicBP, DiastolicBP, Age,
            Height (cm), Weight (kg), Gender

    Returns
    -------
    filled   : dict  — complete set of values ready for model
    estimated: list  — field names that were estimated/defaulted
    missing  : list  — truly missing fields we couldn't resolve
                       (these will block prediction if they're lab fields)
    """
    filled    = dict(data)   # work on a copy
    estimated = []
    missing   = []

    def _get(key, cast=float):
        v = data.get(key)
        if v in (None, ""):
            return None
        try:
            return cast(v)
        except (ValueError, TypeError):
            return None

    # ── 1. BMI ─────────────────────────────────────────────────────────────
    if _get("BMI") is None:
        bmi = _estimate_bmi(_get("Height"), _get("Weight"))
        if bmi is not None:
            filled["BMI"] = bmi
            estimated.append("BMI (calculated from height & weight)")
        else:
            # Try to get from profile if passed separately
            missing.append("BMI")

    # ── 2. Waist ───────────────────────────────────────────────────────────
    if _get("Waist") is None:
        bmi_val = _get("BMI") or filled.get("BMI")
        if bmi_val:
            try:
                bmi_val = float(bmi_val)
                gender  = str(data.get("Gender", "male"))
                waist   = _estimate_waist_from_bmi(bmi_val, gender)
                filled["Waist"] = waist
                estimated.append("Waist (estimated from BMI — approximate)")
            except (TypeError, ValueError):
                filled["Waist"] = POPULATION_MEDIANS["Waist"]
                estimated.append("Waist (population average used — not in report)")
        else:
            filled["Waist"] = POPULATION_MEDIANS["Waist"]
            estimated.append("Waist (population average used — not in report)")

    # ── 3. Blood Pressure ──────────────────────────────────────────────────
    if _get("SystolicBP") is None:
        filled["SystolicBP"] = POPULATION_MEDIANS["SystolicBP"]
        estimated.append("Systolic BP (normal default 120 mmHg used)")

    if _get("DiastolicBP") is None:
        filled["DiastolicBP"] = POPULATION_MEDIANS["DiastolicBP"]
        estimated.append("Diastolic BP (normal default 78 mmHg used)")

    # ── 4. Optional Lab Defaults ─────────────────────────────

    if _get("HbA1c") is None:
        filled["HbA1c"] = POPULATION_MEDIANS["HbA1c"]
        estimated.append("HbA1c (population median used)")

    if _get("HDL") is None:
        filled["HDL"] = POPULATION_MEDIANS["HDL"]
        estimated.append("HDL (population median used)")

    if _get("Triglycerides") is None:
        filled["Triglycerides"] = POPULATION_MEDIANS["Triglycerides"]
        estimated.append("Triglycerides (population median used)")

    # ── 5. Check truly required lab fields ────────────────────────────────
    for field in REQUIRED_LAB_FIELDS:
        if _get(field) is None and filled.get(field) in (None, ""):
            missing.append(field)

    # ── 6. Age fallback ───────────────────────────────────────────────────
    if _get("Age") is None:
        filled["Age"] = 35.0   # population median fallback
        estimated.append("Age (defaulted to 35 — please update profile)")

    return filled, estimated, missing
