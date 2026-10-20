"""Generate clean architecture / use-case diagrams for TrainMate presentation."""
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Arc, Circle, Ellipse, FancyArrowPatch, FancyBboxPatch, Rectangle

OUT_DIR = Path(__file__).resolve().parent / "report_images" / "diagrams"
OUT_DIR.mkdir(parents=True, exist_ok=True)

NAVY = "#1B3A5C"
TEAL = "#5BA89A"
TEAL_LIGHT = "#D4EDE8"
BLUE_LIGHT = "#D6EAF8"
GRAY_BG = "#F7F9FB"
WHITE = "#FFFFFF"


def _save(fig, name):
    path = OUT_DIR / name
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor=WHITE, pad_inches=0.15)
    plt.close(fig)
    print(f"  {path.name}")


def _rect(ax, x, y, w, h, text, fc=TEAL_LIGHT, ec=NAVY, fs=10, bold=False, radius=0.12):
    p = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.02,rounding_size={radius}",
        linewidth=1.5, edgecolor=ec, facecolor=fc,
    )
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, color=NAVY, weight="bold" if bold else "normal")


def _ellipse_uc(ax, cx, cy, w, h, text, fs=9):
    e = Ellipse((cx, cy), w, h, linewidth=1.3, edgecolor=NAVY, facecolor=WHITE)
    ax.add_patch(e)
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs, color=NAVY)


def _arrow(ax, x1, y1, x2, y2, dashed=False):
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>", mutation_scale=14,
        linewidth=1.6, color=NAVY,
        linestyle="--" if dashed else "-",
    ))


def _actor(ax, x, y, label="User"):
    ax.add_patch(Circle((x, y + 1.05), 0.28, fc=TEAL_LIGHT, ec=NAVY, lw=1.5))
    ax.plot([x, x], [y + 0.75, y + 0.15], color=NAVY, lw=2)
    ax.plot([x - 0.35, x + 0.35], [y + 0.55, y + 0.55], color=NAVY, lw=2)
    ax.plot([x, x - 0.3], [y + 0.15, y - 0.35], color=NAVY, lw=2)
    ax.plot([x, x + 0.3], [y + 0.15, y - 0.35], color=NAVY, lw=2)
    ax.text(x, y - 0.65, label, ha="center", va="top", fontsize=11, color=NAVY, weight="bold")


def _system_boundary(ax, x, y, w, h, title):
    ax.add_patch(Rectangle((x, y), w, h, linewidth=2, edgecolor=NAVY,
                           facecolor=GRAY_BG, alpha=0.35, linestyle="-"))
    ax.text(x + w / 2, y + h - 0.25, title, ha="center", va="top",
            fontsize=12, color=NAVY, weight="bold")


def draw_use_case():
    fig, ax = plt.subplots(figsize=(8.5, 6.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")

    _actor(ax, 1.0, 3.8)
    _system_boundary(ax, 2.2, 0.4, 7.4, 7.0, "TrainMate System")

    packages = [
        (2.5, 5.6, 3.3, 1.55, "Account & Security", [
            (4.15, 6.35, "Register &\nVerify Email"),
            (4.15, 5.85, "Login / JWT"),
        ]),
        (6.0, 5.6, 3.4, 1.55, "Workout & Plans", [
            (7.7, 6.35, "Create &\nManage Plan"),
            (7.7, 5.85, "Save\nWorkout"),
        ]),
        (2.5, 3.5, 3.3, 1.55, "Live Exercise", [
            (4.15, 4.25, "Auto-Detect\nExercise"),
            (4.15, 3.75, "Rep Count &\nForm Feedback"),
        ]),
        (6.0, 3.5, 3.4, 1.55, "AI Coaching", [
            (7.7, 4.25, "AI Chatbot"),
            (7.7, 3.75, "Session\nReport"),
        ]),
        (2.5, 1.4, 3.3, 1.55, "Body Progress", [
            (4.15, 2.15, "Upload Before/\nAfter Photos"),
            (4.15, 1.65, "View Progress\nAnalysis"),
        ]),
        (6.0, 1.4, 3.4, 1.55, "Profile", [
            (7.7, 2.15, "Edit Profile"),
            (7.7, 1.65, "App Settings\n(EN / AR)"),
        ]),
    ]

    for px, py, pw, ph, title, cases in packages:
        ax.add_patch(FancyBboxPatch(
            (px, py), pw, ph,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            linewidth=1.2, edgecolor=TEAL, facecolor=TEAL_LIGHT, alpha=0.5,
        ))
        ax.text(px + pw / 2, py + ph - 0.18, title, ha="center", va="top",
                fontsize=9, color=NAVY, weight="bold")
        for cx, cy, txt in cases:
            _ellipse_uc(ax, cx, cy, 2.0, 0.72, txt, fs=8)
        # One association line per package (cleaner than lines to every use case)
        _arrow(ax, 1.35, 4.0, px, py + ph / 2)

    _save(fig, "arch_use_case_overview.png")


def draw_detection():
    fig, ax = plt.subplots(figsize=(7.5, 6.5))
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 9)
    ax.axis("off")

    steps = [
        (1.2, 7.8, 5.6, 0.85, "Camera Frame"),
        (1.2, 6.6, 5.6, 0.85, "ML Kit Pose\n33 landmarks"),
        (1.2, 5.4, 5.6, 0.85, "Feature Extractor\n22 values / frame"),
        (1.2, 4.2, 5.6, 0.85, "Window of 30 frames\n+ normalize"),
        (1.2, 3.0, 2.5, 0.85, "TFLite\nBiLSTM"),
        (4.3, 3.0, 2.5, 0.85, "Server\nfallback"),
        (1.2, 1.8, 5.6, 0.85, "Exercise Label\nsquat · push-up · press · curl"),
    ]
    for x, y, w, h, t in steps:
        fc = BLUE_LIGHT if "Server" in t else TEAL_LIGHT
        _rect(ax, x, y, w, h, t, fc=fc, fs=10)

    ys = [7.8, 6.6, 5.4, 4.2, 3.0, 1.8]
    for i in range(len(ys) - 1):
        _arrow(ax, 4.0, ys[i], 4.0, ys[i + 1] + 0.85)
    _arrow(ax, 2.45, 3.0, 2.45, 2.65)
    _arrow(ax, 5.55, 3.0, 5.55, 2.65, dashed=True)
    _arrow(ax, 2.45, 2.65, 4.0, 2.65)
    _arrow(ax, 5.55, 2.65, 4.0, 2.65, dashed=True)
    _arrow(ax, 4.0, 3.0, 4.0, 2.65)

    ax.text(4.0, 0.7, "4 supported exercises", ha="center", fontsize=9,
            color=NAVY, style="italic")
    _save(fig, "arch_detection_clean.png")


def draw_backend():
    fig, ax = plt.subplots(figsize=(7.5, 6.5))
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 9)
    ax.axis("off")

    _rect(ax, 1.0, 7.7, 6.0, 0.9, "Flutter Mobile App", fc=BLUE_LIGHT, fs=11, bold=True)
    _arrow(ax, 4.0, 7.7, 4.0, 7.25, )
    ax.text(4.65, 7.45, "REST + JWT", fontsize=9, color=NAVY)

    _rect(ax, 0.6, 5.8, 6.8, 1.35, "", fc=GRAY_BG, ec=NAVY)
    ax.text(4.0, 6.95, "FastAPI Backend", ha="center", fontsize=11, color=NAVY, weight="bold")
    routers = ["/auth", "/users", "/plans", "/workouts", "/chat", "/ml"]
    for i, r in enumerate(routers):
        _rect(ax, 0.85 + i * 1.05, 6.05, 0.95, 0.55, r, fs=8)

    _arrow(ax, 4.0, 5.8, 4.0, 5.35)
    _rect(ax, 1.0, 4.5, 6.0, 0.75, "Business Logic  ·  JWT Auth  ·  Email Service", fs=9)
    _arrow(ax, 4.0, 4.5, 4.0, 4.05)

    _rect(ax, 0.6, 2.7, 6.8, 1.25, "", fc=TEAL_LIGHT, ec=NAVY)
    ax.text(4.0, 3.7, "SQLite Database (SQLAlchemy ORM)", ha="center", fontsize=10, color=NAVY, weight="bold")
    tables = ["Users", "Profiles", "Plans", "Sessions"]
    for i, t in enumerate(tables):
        _rect(ax, 1.0 + i * 1.45, 2.9, 1.25, 0.55, t, fs=9)

    _arrow(ax, 4.0, 2.7, 4.0, 2.25)
    _rect(ax, 1.0, 1.4, 2.6, 0.75, "Email\nSMTP / Resend", fc=BLUE_LIGHT, fs=9)
    _rect(ax, 4.7, 1.4, 2.3, 0.75, "Groq / OpenRouter\nLLM + Vision", fc=BLUE_LIGHT, fs=9)

    _arrow(ax, 2.3, 1.4, 2.3, 2.7, dashed=True)
    _arrow(ax, 5.85, 1.4, 5.85, 2.7, dashed=True)
    _save(fig, "arch_backend_clean.png")


def draw_chatbot():
    fig, ax = plt.subplots(figsize=(7.5, 6.5))
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 9)
    ax.axis("off")

    flow = [
        (2.4, 7.5, 3.2, 0.8, "User sends message\n(text / voice / image)"),
        (2.4, 6.3, 3.2, 0.8, "Flutter Chatbot UI"),
        (2.4, 5.1, 3.2, 0.8, "POST /api/chat\n(JWT token)"),
        (2.4, 3.9, 3.2, 0.8, "Load user context\nfrom database"),
        (2.4, 2.7, 3.2, 0.8, "Build system prompt\nprofile · plan · workouts"),
        (2.4, 1.5, 3.2, 0.8, "Groq LLM inference"),
        (2.4, 0.3, 3.2, 0.8, "Return coach reply\nto mobile app"),
    ]
    for x, y, w, h, t in flow:
        fc = BLUE_LIGHT if "Groq" in t else TEAL_LIGHT
        _rect(ax, x, y, w, h, t, fc=fc, fs=9.5)

    for y in (7.5, 6.3, 5.1, 3.9, 2.7, 1.5):
        _arrow(ax, 4.0, y, 4.0, y - 0.45)

    ctx = ["Profile", "Active plan", "Workouts", "Body scores"]
    for i, c in enumerate(ctx):
        _rect(ax, 6.0, 3.2 - i * 0.55, 1.6, 0.45, c, fs=8)
        _arrow(ax, 5.6, 4.3, 6.0, 3.95 - i * 0.55, dashed=True)

    _save(fig, "arch_chatbot_clean.png")


def draw_feedback():
    fig, ax = plt.subplots(figsize=(7.5, 6.5))
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 9)
    ax.axis("off")

    ax.text(2.0, 8.5, "Live Form Feedback", ha="center", fontsize=11, color=NAVY, weight="bold")
    live = [
        (0.4, 7.4, 3.2, 0.75, "Camera + Pose"),
        (0.4, 6.3, 3.2, 0.75, "Joint Angles"),
        (0.4, 5.2, 3.2, 0.75, "FSM Rep Counter"),
        (0.4, 4.1, 3.2, 0.75, "Form Fault Check"),
        (0.4, 3.0, 3.2, 0.75, "HUD Feedback"),
    ]
    for x, y, w, h, t in live:
        _rect(ax, x, y, w, h, t, fs=9.5)
    for y in (7.4, 6.3, 5.2, 4.1):
        _arrow(ax, 2.0, y, 2.0, y - 0.55)

    faults = "partial rep · hip sag · shallow squat · swinging · lockout"
    ax.text(2.0, 2.55, faults, ha="center", fontsize=7.5, color=NAVY, wrap=True)

    ax.text(6.0, 8.5, "Body Progress", ha="center", fontsize=11, color=NAVY, weight="bold")
    body = [
        (4.4, 7.4, 3.2, 0.75, "Before + After\nPhotos"),
        (4.4, 6.3, 3.2, 0.75, "MediaPipe Pose"),
        (4.4, 5.2, 3.2, 0.75, "Body Metrics"),
        (4.4, 4.1, 3.2, 0.75, "Regional Scores"),
        (4.4, 3.0, 3.2, 0.75, "Overall Score"),
    ]
    for x, y, w, h, t in body:
        _rect(ax, x, y, w, h, t, fc=BLUE_LIGHT, fs=9.5)
    for y in (7.4, 6.3, 5.2, 4.1):
        _arrow(ax, 6.0, y, 6.0, y - 0.55)

    _rect(ax, 1.0, 0.5, 6.0, 0.85, "Saved to backend  ·  shown in profile & chatbot context", fc=GRAY_BG, fs=9)
    _save(fig, "arch_feedback_clean.png")


def main():
    print("Generating clean architecture diagrams...")
    draw_use_case()
    draw_detection()
    draw_backend()
    draw_chatbot()
    draw_feedback()
    print("Done.")


if __name__ == "__main__":
    main()
