"""
meal_engine.py — InsulinSense Meal Plan Engine
Features:
  - Bad-food filtering + hard nutritional limits
  - Tiered calorie matching with variety randomisation
  - Meal history exclusion (cross-session variety)
  - Dietary preferences (omnivore / vegetarian / vegan / no-fish / no-dairy / no-eggs)
  - Feature-based "Why this meal" reasons
  - Water / hydration guidance
  - DB persistence (save + load + history tracking)
"""
import os, random, sqlite3, json
from datetime import datetime, timedelta

import pandas as pd

# ═══════════════════════════════════════════════════════════════════
# Dataset
# ═══════════════════════════════════════════════════════════════════
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_PATH = os.path.join(BASE_DIR, "processed_data", "final_food_dataset.csv")
_raw_df    = pd.read_csv(_DATA_PATH)

_rename = {
    "Glycemic_Index (GI)": "GI", "Calories (kcal)": "Calories",
    "Protein (g)": "Protein_g",  "Carbohydrates (g)": "Carbs_g",
    "Fat (g)": "Fat_g",          "Fiber (g)": "Fiber_g",
    "Sugars (g)": "Sugar_g",
}
_raw_df = _raw_df.rename(columns={k: v for k, v in _rename.items() if k in _raw_df.columns})

# ═══════════════════════════════════════════════════════════════════
# Block-list  (always excluded regardless of diet)
# ═══════════════════════════════════════════════════════════════════
_BLOCKED = [
    "smoothie (fruit", "chocolate milk", "chai latte", "matcha latte",
    "fruit cocktail", "french fries", "pretzels", "saltine", "graham cracker",
    "cereal bar", "water cracker", "crackers (5 whole", "dates (2 medium",
    "coffee (black)", "espresso", "mint tea", "turkish coffee", "vegetable broth",
    "pork floss", "century egg", "guanciale", "salami",
    "pickle (1 spear", "pickle (1 whole", "sauerkraut", "pepperoncini",
]
def _is_blocked(name):
    low = name.lower()
    return any(k in low for k in _BLOCKED)

_HARD_LIMITS = {
    "breakfast": dict(max_sugar=20, min_cal=70,  max_cal=550),
    "lunch":     dict(max_sugar=25, min_cal=150, max_cal=750),
    "dinner":    dict(max_sugar=20, min_cal=150, max_cal=750),
    "snack":     dict(max_sugar=20, min_cal=40,  max_cal=300),
}
def _passes_hard_limits(row, meal_type):
    lims = _HARD_LIMITS.get(meal_type.lower(), {})
    if row["Calories"] < lims.get("min_cal", 0):     return False
    if row["Calories"] > lims.get("max_cal", 9999):  return False
    if row["Sugar_g"]  > lims.get("max_sugar", 999): return False
    return True

def _clean_df(df):
    df = df[df["Calories"] > 0].copy()
    df = df[~df["Food_Item"].apply(_is_blocked)]
    df = df[~df["Food_Role"].str.lower().isin(["drink", "topping", "side"])]
    return df

_df = _clean_df(_raw_df)


# ═══════════════════════════════════════════════════════════════════
# Dietary Preference Filtering  ← NEW
# ═══════════════════════════════════════════════════════════════════
# Keyword sets for each food group
_MEAT_KW  = ["chicken","beef","pork","lamb","turkey","steak","bacon","ham",
              "veal","duck","bison","kebab","shish","chorizo","prosciutto",
              "pepperoni","ground beef","ground lamb","skirt steak","t-bone",
              "sirloin","fiorentina","osso buco","carbonara","meat"]
_FISH_KW  = ["salmon","tuna","cod","shrimp","tilapia","halibut","mackerel",
              "lobster","scallop","mussels","oyster","sashimi","seafood",
              "anchov","sardine","squid","paella","fish","crab","ceviche","mahi"]
_DAIRY_KW = ["cheese","yogurt","milk","cream","butter","whey","ricotta",
              "mozzarella","brie","feta","cheddar","provolone","goat cheese",
              "cottage","labneh","parmesan","pecorino","gorgonzola","swiss"]
_EGG_KW   = ["egg","omelette","shakshuka","benedict","frittata","poached egg",
              "scrambled egg","hard-boiled","egg white"]

def _has_ingredient(name, keywords):
    low = name.lower()
    return any(k in low for k in keywords)

# Dietary profiles → which groups to EXCLUDE
_DIET_EXCLUDES = {
    "omnivore":    [],                                        # eat everything
    "vegetarian":  ["meat", "fish"],                          # no meat/fish, dairy+eggs OK
    "vegan":       ["meat", "fish", "dairy", "eggs"],         # plant-only
    "no_fish":     ["fish"],
    "no_dairy":    ["dairy"],
    "no_eggs":     ["eggs"],
    "pescatarian": ["meat"],                                  # fish OK, no meat
}

_GROUP_MAP = {
    "meat":  (_MEAT_KW,  _has_ingredient),
    "fish":  (_FISH_KW,  _has_ingredient),
    "dairy": (_DAIRY_KW, _has_ingredient),
    "eggs":  (_EGG_KW,   _has_ingredient),
}

def apply_dietary_filter(df: pd.DataFrame, diet: str) -> pd.DataFrame:
    """Filter out foods that don't match the dietary preference."""
    diet = str(diet).lower().strip()
    exclude_groups = _DIET_EXCLUDES.get(diet, [])
    if not exclude_groups:
        return df

    mask = pd.Series([True] * len(df), index=df.index)
    for group in exclude_groups:
        kws, fn = _GROUP_MAP[group]
        mask &= ~df["Food_Item"].apply(lambda n: fn(n, kws))

    filtered = df[mask].copy()
    # Safety: if dietary filter makes a meal slot empty, return unfiltered
    return filtered if len(filtered) >= 5 else df


# ═══════════════════════════════════════════════════════════════════
# Meal History Exclusion  ← NEW
# ═══════════════════════════════════════════════════════════════════
def get_recent_food_names(email: str, days: int = 7, limit: int = 28) -> set:
    """
    Returns food item names used in the last `days` days for this user.
    Used to exclude repetition across sessions.
    """
    _init_tables()
    try:
        conn = sqlite3.connect(_DB)
        cur  = conn.cursor()
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        cur.execute("""
            SELECT plan_json FROM meal_plans
            WHERE user_email = ? AND created_at >= ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (email, cutoff, limit))
        rows = cur.fetchall()
        conn.close()

        used = set()
        for (plan_json,) in rows:
            try:
                plan = json.loads(plan_json)
                for md in plan.get("meals", {}).values():
                    f = md.get("food")
                    if f and f.get("food_item"):
                        used.add(f["food_item"].lower())
            except Exception:
                pass
        return used
    except Exception:
        return set()

def exclude_recent(df: pd.DataFrame, used_names: set) -> pd.DataFrame:
    """Remove recently used foods; fallback to full df if too few remain."""
    if not used_names:
        return df
    filtered = df[~df["Food_Item"].str.lower().isin(used_names)].copy()
    return filtered if len(filtered) >= 5 else df


# ═══════════════════════════════════════════════════════════════════
# GI / Severity Filters
# ═══════════════════════════════════════════════════════════════════
_GI_LIMITS = {"Normal": 70, "Mild": 55, "Severe": 45}

def filter_by_severity(df, severity):
    limit = _GI_LIMITS.get(severity, 55)
    return df[(df["GI"] <= limit) | (df["GI"] == 0)].copy()

def keep_main_foods(df):
    return df[df["Food_Role"] == "Main"].copy()

def get_meal_candidates(df, meal_type):
    cands = df[df["Meal_Type"].str.contains(meal_type, case=False, na=False)].copy()
    cands = cands[cands.apply(lambda r: _passes_hard_limits(r, meal_type), axis=1)]
    return cands


# ═══════════════════════════════════════════════════════════════════
# Calorie Math
# ═══════════════════════════════════════════════════════════════════
def calculate_daily_calories(weight, height, age, gender, activity_level):
    w = max(30, min(300, float(weight)))
    h = max(100, min(250, float(height)))
    a = max(10, min(120, float(age)))
    g = str(gender).lower().strip()
    bmr  = (10 * w) + (6.25 * h) - (5 * a) + (5 if g == "male" else -161)
    mult = {"low": 1.2, "moderate": 1.55, "high": 1.725}
    return round(bmr * mult.get(str(activity_level).lower(), 1.2))


# ── IR-aware calorie cap ────────────────────────────────────────────────────
# Insulin resistance management requires a therapeutic deficit.
# The dataset's single-item foods max out at ~550 kcal — exceeding 2 200 kcal/day
# with realistic portions causes large calorie gaps in the summary card.
# This cap is both clinically appropriate AND matches dataset coverage capacity.
_IR_CAL_CAP = {
    "Normal": 2500,   # mild deficit, generous range
    "Mild":   2200,   # standard therapeutic target
    "Severe": 1900,   # stricter deficit for significant IR
}

def apply_ir_cap(raw_calories: int, severity: str) -> tuple[int, bool]:
    """
    Returns (capped_calories, was_capped).
    Calories are capped to the IR therapeutic ceiling for the given severity.
    """
    cap = _IR_CAL_CAP.get(severity, 2200)
    if raw_calories > cap:
        return cap, True
    return raw_calories, False


def distribute_calories(total):
    return {
        "breakfast": round(total * 0.25),
        "lunch":     round(total * 0.35),
        "dinner":    round(total * 0.25),
        "snack":     round(total * 0.15),
    }

# ═══════════════════════════════════════════════════════════════════
# Ranking
# ═══════════════════════════════════════════════════════════════════
def rank_foods(df):
    r = df.copy()
    r["Effective_GI"] = r["GI"].clip(lower=10)
    r["Score"] = (
          r["Protein_g"] * 3.5 + r["Fiber_g"] * 4.5
        - r["Effective_GI"] * 0.45 - r["Sugar_g"] * 1.5 - r["Fat_g"] * 0.3
    )
    return r.sort_values("Score", ascending=False).reset_index(drop=True)

# ═══════════════════════════════════════════════════════════════════
# Food Selection  (tiered match + portion scaling + variety)
# ═══════════════════════════════════════════════════════════════════
_MAX_PORTION_SCALE = 1.5   # max 1.5× listed serving — clinically reasonable

def select_food(ranked_df, target_calories, meal_type="", top_n=5):
    """
    1. Try ±20% → ±40% → any calorie range (tiered).
    2. If best match is still < 65% of target, scale the portion up (max 1.5×).
    3. All macros scale proportionally with the portion.
    4. Samples randomly from top_n candidates for daily variety.
    """
    if ranked_df.empty:
        return None

    pool = pd.DataFrame()
    for tol in (0.20, 0.40, 1.0):
        lo = target_calories * (1 - tol)
        hi = target_calories * (1 + tol)
        pool = ranked_df[(ranked_df["Calories"] >= lo) & (ranked_df["Calories"] <= hi)]
        if not pool.empty:
            break
    if pool.empty:
        pool = ranked_df

    chosen   = pool.head(top_n).sample(1).iloc[0]
    base_cal = float(chosen["Calories"])

    # Scale up only when the gap is meaningful (> 35% below target)
    if base_cal < target_calories * 0.65:
        scale = min(target_calories / base_cal, _MAX_PORTION_SCALE)
    else:
        scale = 1.0
    scale = round(scale, 2)

    portion_note = ""
    if scale > 1.05:
        portion_note = f"×{scale} serving (scaled to meet your calorie target)"

    return {
        "food_item":     str(chosen["Food_Item"]),
        "calories":      round(base_cal * scale),
        "base_calories": round(base_cal),
        "portion_scale": scale,
        "portion_note":  portion_note,
        "gi":            int(chosen["GI"]),
        "protein_g":     round(float(chosen["Protein_g"]) * scale, 1),
        "fiber_g":       round(float(chosen["Fiber_g"])   * scale, 1),
        "fat_g":         round(float(chosen["Fat_g"])     * scale, 1),
        "carbs_g":       round(float(chosen["Carbs_g"])   * scale, 1),
        "sugar_g":       round(float(chosen["Sugar_g"])   * scale, 1),
        "water_ml":      int(chosen.get("Water_Intake (ml)", 0) or 0),
        "score":         round(float(chosen.get("Score", 0)), 2),
        "category":      str(chosen.get("Category", "")),
    }


# ═══════════════════════════════════════════════════════════════════
# GI Tier
# ═══════════════════════════════════════════════════════════════════
def _gi_tier(gi):
    if gi == 0:  return ("zero",     "GI-Free",     "gi-zero")
    if gi <= 25: return ("very_low", "Very Low GI", "gi-vlow")
    if gi <= 40: return ("low",      "Low GI",      "gi-low")
    if gi <= 55: return ("medium",   "Medium GI",   "gi-med")
    return           ("high",      "High GI",     "gi-high")


# ═══════════════════════════════════════════════════════════════════
# Why-This-Meal Reasons
# ═══════════════════════════════════════════════════════════════════
def build_selection_reasons(food, meal_type, target_calories, severity):
    reasons = []
    gi, protein, fiber = food["gi"], food["protein_g"], food["fiber_g"]
    sugar, cal          = food["sugar_g"], food["calories"]
    tier, _, _          = _gi_tier(gi)

    # GI reason
    gi_texts = {
        "zero":     ("🔬", "positive", f"GI-free (pure protein/fat) — zero direct glycemic impact on blood sugar."),
        "very_low": ("✅", "positive", f"Very low GI ({gi}) — minimal blood sugar spike, ideal for insulin resistance."),
        "low":      ("✅", "positive", f"Low GI ({gi}) — slow, sustained glucose rise that keeps insulin stable."),
        "medium":   ("⚠️", "neutral",  f"Moderate GI ({gi}) — within your limit; pair with protein to blunt the response."),
        "high":     ("⚠️", "warning",  f"Higher GI ({gi}) — consume in small portion alongside fiber-rich foods."),
    }
    icon, typ, text = gi_texts.get(tier, gi_texts["medium"])
    reasons.append({"icon": icon, "type": typ, "text": text})

    # Protein
    if protein >= 20:
        reasons.append({"icon": "💪", "type": "positive",
            "text": f"High protein ({protein} g) — reduces post-meal glucose spikes and supports lean mass."})
    elif protein >= 10:
        reasons.append({"icon": "💪", "type": "positive",
            "text": f"Good protein ({protein} g) — slows carb absorption and improves insulin sensitivity."})

    # Fiber
    if fiber >= 6:
        reasons.append({"icon": "🌿", "type": "positive",
            "text": f"Excellent fiber ({fiber} g) — significantly slows glucose absorption."})
    elif fiber >= 3:
        reasons.append({"icon": "🌿", "type": "positive",
            "text": f"Good fiber ({fiber} g) — moderates the glycemic response of this meal."})

    # Sugar
    if sugar <= 3:
        reasons.append({"icon": "🍬", "type": "positive",
            "text": f"Very low sugar ({sugar} g) — minimises direct glucose load."})
    elif sugar <= 8:
        reasons.append({"icon": "🍬", "type": "positive",
            "text": f"Low sugar ({sugar} g) — safe range for insulin resistance management."})
    elif sugar > 15:
        reasons.append({"icon": "⚠️", "type": "warning",
            "text": f"Moderate sugar ({sugar} g) — eat mindfully; fiber context helps buffer impact."})

    # Calorie match
    pct = abs(cal - target_calories) / max(target_calories, 1) * 100
    if pct <= 10:
        reasons.append({"icon": "🎯", "type": "positive",
            "text": f"Excellent calorie match — {cal} kcal within 10% of {meal_type} target ({target_calories} kcal)."})
    elif pct <= 25:
        reasons.append({"icon": "📊", "type": "neutral",
            "text": f"Good calorie fit — {cal} kcal vs {target_calories} kcal {meal_type} target."})
    else:
        reasons.append({"icon": "📊", "type": "neutral",
            "text": f"Best available option within GI + nutrition constraints for {meal_type} ({cal} kcal)."})

    # Meal timing
    _timing = {
        "breakfast": "Starting with a protein-rich, low-GI breakfast stabilises morning insulin and curbs cravings.",
        "lunch":     "A balanced midday meal maintains steady energy without the afternoon glucose crash.",
        "dinner":    "A low-carb evening meal supports overnight metabolic repair and lowers fasting glucose.",
        "snack":     "A smart snack bridges meals, preventing hypoglycaemia and hunger-driven overeating.",
    }
    if meal_type.lower() in _timing:
        reasons.append({"icon": "⏰", "type": "neutral", "text": _timing[meal_type.lower()]})

    if severity == "Severe" and tier in ("zero", "very_low", "low"):
        reasons.append({"icon": "🩺", "type": "positive",
            "text": "Meets strict low-GI threshold for Severe insulin resistance management protocol."})

    return reasons


# ═══════════════════════════════════════════════════════════════════
# Water / Hydration Guidance  ← NEW
# ═══════════════════════════════════════════════════════════════════
_MEAL_WATER = {
    "breakfast": 400,
    "lunch":     600,
    "dinner":    500,
    "snack":     300,
}
_SEVERITY_BONUS = {"Normal": 0, "Mild": 200, "Severe": 300}

def build_water_guidance(meals: dict, severity: str, weight: float) -> dict:
    """
    Calculate total daily water recommendation.
    Base: 35 ml per kg bodyweight
    Meal-specific: from dataset Water_Intake (ml) column
    Clinical bonus: extra for higher severity (reduces insulin resistance)
    """
    base_ml     = round(weight * 35)
    severity_b  = _SEVERITY_BONUS.get(severity, 0)
    meal_water  = {}
    total_from_meals = 0

    for mt, md in meals.items():
        food    = md.get("food")
        food_ml = food.get("water_ml", 0) if food else 0
        slot_ml = _MEAL_WATER.get(mt, 300) + food_ml
        meal_water[mt] = slot_ml
        total_from_meals += slot_ml

    total_recommended = max(base_ml + severity_b, 2000)

    return {
        "total_ml":       total_recommended,
        "total_L":        round(total_recommended / 1000, 1),
        "per_meal":       meal_water,
        "clinical_note":  (
            f"Drink at least {round(total_recommended/1000,1)} L/day. "
            f"Adequate hydration improves insulin receptor sensitivity and "
            f"helps kidneys clear excess glucose. "
            + ("Severe IR patients benefit most from consistent hydration." if severity == "Severe" else
               "Spread intake evenly across the day for best results.")
        ),
        "tips": [
            "Drink a glass of water 15–20 min before each meal to moderate appetite.",
            "Choose plain water, herbal tea, or sparkling water — avoid sweetened drinks.",
            "Urine colour guide: pale yellow = well hydrated; dark = drink more.",
        ],
    }


# ═══════════════════════════════════════════════════════════════════
# Foods to Avoid
# ═══════════════════════════════════════════════════════════════════
_AVOID = {
    "Normal": ["White rice", "Soft drinks", "Candy & sweets", "White bread",
               "Pastries & cakes", "Fried snacks"],
    "Mild":   ["White rice", "Soft drinks", "Candy & sweets", "White bread",
               "Pastries", "Fruit juice", "Cornflakes", "Instant oatmeal",
               "Fried snacks", "Sports drinks"],
    "Severe": ["White rice", "Soft drinks", "Candy & sweets", "White bread",
               "Pastries", "Fruit juice", "Cornflakes", "Instant oatmeal",
               "Potatoes & chips", "Sports drinks", "Honey & syrups",
               "Dried fruit", "Bagels", "Pretzels", "Sweetened yogurt", "Ice cream"],
}


# ═══════════════════════════════════════════════════════════════════
# Main Generator
# ═══════════════════════════════════════════════════════════════════
def generate_meal_plan(
    weight, height, age, gender, activity_level, severity,
    diet="omnivore",       # ← dietary preference
    email="",             # ← for history exclusion
) -> dict:

    sev = {"normal": "Normal", "mild": "Mild", "severe": "Severe"}.get(
        str(severity).lower(), "Mild"
    )
    diet = str(diet).lower().strip()

    raw_cal              = calculate_daily_calories(weight, height, age, gender, activity_level)
    daily_cal, was_capped = apply_ir_cap(raw_cal, sev)
    meal_targets         = distribute_calories(daily_cal)

    # Base pool: severity filter → dietary filter
    filtered   = filter_by_severity(_df, sev)
    filtered   = apply_dietary_filter(filtered, diet)
    main_foods = keep_main_foods(filtered)

    # History exclusion (cross-session variety)
    recent_names = get_recent_food_names(email, days=7) if email else set()

    meals = {}
    for mt in ("breakfast", "lunch", "dinner", "snack"):
        # Build candidates
        cands = get_meal_candidates(main_foods, mt)
        cands = exclude_recent(cands, recent_names)

        if mt == "snack":
            snack_pool = apply_dietary_filter(filter_by_severity(_df, sev), diet)
            snack_role = snack_pool[snack_pool["Food_Role"].str.lower() == "snack"]
            snack_role = snack_role[snack_role.apply(lambda r: _passes_hard_limits(r, "snack"), axis=1)]
            snack_role = exclude_recent(snack_role, recent_names)
            cands = pd.concat([cands, snack_role]).drop_duplicates(subset="Food_Item")

        if cands.empty:
            cands = main_foods if not main_foods.empty else filtered

        ranked = rank_foods(cands)
        target = meal_targets[mt]
        food   = select_food(ranked, target, mt)

        if food:
            food["selection_reasons"] = build_selection_reasons(food, mt, target, sev)
            tier, gi_label, gi_css    = _gi_tier(food["gi"])
            food["gi_label"]          = gi_label
            food["gi_css"]            = gi_css

        meals[mt] = {"target_calories": target, "food": food}

    total_cal     = sum(m["food"]["calories"]  for m in meals.values() if m["food"])
    total_protein = sum(m["food"]["protein_g"] for m in meals.values() if m["food"])
    total_fiber   = sum(m["food"]["fiber_g"]   for m in meals.values() if m["food"])
    total_sugar   = sum(m["food"]["sugar_g"]   for m in meals.values() if m["food"])

    water = build_water_guidance(meals, sev, float(weight))

    return {
        "severity":       sev,
        "diet":           diet,
        "daily_calories": daily_cal,
        "tdee":           raw_cal,
        "calorie_capped": was_capped,
        "cal_cap_reason": (
            f"Capped from {raw_cal} kcal (TDEE) to {daily_cal} kcal — "
            f"a therapeutic deficit is recommended for {sev} insulin resistance."
        ) if was_capped else "",
        "meal_targets":   meal_targets,
        "meals":          meals,
        "hydration":      water,
        "daily_summary": {
            "total_calories_selected": total_cal,
            "total_protein_g":         round(total_protein, 1),
            "total_fiber_g":           round(total_fiber, 1),
            "total_sugar_g":           round(total_sugar, 1),
            "calorie_gap":             daily_cal - total_cal,
            "coverage_pct":            min(round(total_cal / max(daily_cal, 1) * 100), 100),
        },
        "foods_to_avoid": _AVOID.get(sev, _AVOID["Mild"]),
    }


# ═══════════════════════════════════════════════════════════════════
# Dashboard Widget Data  ← NEW
# ═══════════════════════════════════════════════════════════════════
def get_dashboard_meal_summary(email: str) -> dict | None:
    """
    Returns a compact summary of the latest meal plan
    suitable for embedding in the Dashboard widget.
    """
    plan = get_latest_meal_plan(email)
    if not plan:
        return None

    meals = plan.get("meals", {})
    summary = plan.get("daily_summary", {})

    meal_previews = {}
    for mt, md in meals.items():
        f = md.get("food")
        if f:
            meal_previews[mt] = {
                "food_item": f["food_item"],
                "calories":  f["calories"],
                "gi":        f["gi"],
                "gi_label":  f.get("gi_label", ""),
                "gi_css":    f.get("gi_css", ""),
            }

    return {
        "severity":         plan.get("severity"),
        "diet":             plan.get("diet", "omnivore"),
        "daily_calories":   plan.get("daily_calories"),
        "coverage_pct":     summary.get("coverage_pct", 0),
        "total_protein_g":  summary.get("total_protein_g", 0),
        "total_fiber_g":    summary.get("total_fiber_g", 0),
        "meal_previews":    meal_previews,
        "water_L":          plan.get("hydration", {}).get("total_L", 0),
        "saved_at":         plan.get("saved_at", ""),
        "has_plan":         True,
    }


# ═══════════════════════════════════════════════════════════════════
# DB Layer
# ═══════════════════════════════════════════════════════════════════
_DB = os.path.join(os.path.dirname(__file__), "users.db")

def _init_tables():
    conn = sqlite3.connect(_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS meal_plans (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            severity   TEXT,
            diet       TEXT DEFAULT 'omnivore',
            plan_json  TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Add diet column if upgrading from old schema
    try:
        conn.execute("ALTER TABLE meal_plans ADD COLUMN diet TEXT DEFAULT 'omnivore'")
    except Exception:
        pass
    conn.commit()
    conn.close()

def save_meal_plan(email: str, plan: dict):
    _init_tables()
    conn = sqlite3.connect(_DB)
    conn.execute(
        "INSERT INTO meal_plans (user_email, severity, diet, plan_json) VALUES (?,?,?,?)",
        (email, plan.get("severity",""), plan.get("diet","omnivore"),
         json.dumps(plan, ensure_ascii=False))
    )
    conn.commit()
    conn.close()

def get_latest_meal_plan(email: str) -> dict | None:
    _init_tables()
    conn = sqlite3.connect(_DB)
    cur  = conn.cursor()
    cur.execute("""
        SELECT plan_json, created_at FROM meal_plans
        WHERE user_email=? ORDER BY created_at DESC LIMIT 1
    """, (email,))
    row = cur.fetchone()
    conn.close()
    if row:
        plan = json.loads(row[0])
        plan["saved_at"] = row[1]
        return plan
    return None

def save_user_diet_preference(email: str, diet: str):
    """Persist dietary preference to users table (adds column if missing)."""
    try:
        conn = sqlite3.connect(_DB)
        try:
            conn.execute("ALTER TABLE users ADD COLUMN diet_preference TEXT DEFAULT 'omnivore'")
        except Exception:
            pass
        conn.execute("UPDATE users SET diet_preference=? WHERE email=?", (diet, email))
        conn.commit()
        conn.close()
    except Exception:
        pass

def get_user_diet_preference(email: str) -> str:
    """Retrieve saved dietary preference for a user."""
    try:
        conn = sqlite3.connect(_DB)
        cur  = conn.cursor()
        try:
            conn.execute("ALTER TABLE users ADD COLUMN diet_preference TEXT DEFAULT 'omnivore'")
            conn.commit()
        except Exception:
            pass
        cur.execute("SELECT diet_preference FROM users WHERE email=?", (email,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row and row[0] else "omnivore"
    except Exception:
        return "omnivore"


# ═══════════════════════════════════════════════════════════════════
# CLI Test
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n── Omnivore / Mild ──")
    plan = generate_meal_plan(80, 175, 30, "male", "moderate", "Mild",
                              diet="omnivore", email="")
    for mt, md in plan["meals"].items():
        f = md["food"]
        print(f"  {mt:10s}: {f['food_item']:50s} {f['calories']} kcal  GI={f['gi']}" if f else f"  {mt}: NONE")

    print("\n── Vegan / Severe ──")
    plan = generate_meal_plan(65, 162, 28, "female", "low", "Severe",
                              diet="vegan", email="")
    for mt, md in plan["meals"].items():
        f = md["food"]
        print(f"  {mt:10s}: {f['food_item']:50s} {f['calories']} kcal  GI={f['gi']}" if f else f"  {mt}: NONE")

    print("\n── Vegetarian / Normal ──")
    plan = generate_meal_plan(70, 168, 35, "female", "high", "Normal",
                              diet="vegetarian", email="")
    for mt, md in plan["meals"].items():
        f = md["food"]
        print(f"  {mt:10s}: {f['food_item']:50s} {f['calories']} kcal" if f else f"  {mt}: NONE")

    print(f"\n  Hydration: {plan['hydration']['total_L']} L/day")
    print(f"  Water per meal: {plan['hydration']['per_meal']}")
















