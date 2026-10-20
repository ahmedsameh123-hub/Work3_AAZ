"""Generate TrainMate graduation presentation matching reference outline."""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

BASE = Path(__file__).resolve().parent
SCREENS = BASE / "app_screens"
DIAGRAMS = BASE / "report_images" / "diagrams"
RESULTS = BASE / "report_images" / "results"
OUT = BASE / "TrainMate_Presentation_G6.pptx"

# Theme colors (professional blue, similar to reference)
DARK_BLUE = RGBColor(0x1B, 0x3A, 0x5C)
ACCENT_BLUE = RGBColor(0x2E, 0x75, 0xB6)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK_TEXT = RGBColor(0x33, 0x33, 0x33)
LIGHT_GRAY = RGBColor(0xF2, 0xF4, 0xF7)


def set_slide_bg(slide, color=WHITE):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_header_bar(slide, title: str, slide_num: int | None = None):
    shape = slide.shapes.add_shape(
        1, Inches(0), Inches(0), Inches(13.333), Inches(1.05)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = DARK_BLUE
    shape.line.fill.background()
    tf = shape.text_frame
    tf.text = title
    p = tf.paragraphs[0]
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.font.name = "Calibri"
    if slide_num is not None:
        box = slide.shapes.add_textbox(Inches(12.3), Inches(6.9), Inches(0.8), Inches(0.4))
        tf2 = box.text_frame
        tf2.text = str(slide_num)
        p2 = tf2.paragraphs[0]
        p2.font.size = Pt(14)
        p2.font.color.rgb = ACCENT_BLUE
        p2.alignment = PP_ALIGN.RIGHT


def add_bullets(slide, items: list[str], left=0.7, top=1.4, width=11.8, height=5.5, size=20):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = item
        p.level = 0
        p.font.size = Pt(size)
        p.font.name = "Calibri"
        p.font.color.rgb = DARK_TEXT
        p.space_after = Pt(10)


def add_title_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, DARK_BLUE)
    box = slide.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.5), Inches(3.2))
    tf = box.text_frame
    tf.word_wrap = True
    lines = [
        ("TrainMate", 40, True),
        ("AI-Powered Mobile Smart Gym Assistant", 24, False),
        ("", 12, False),
        ("Group 6", 20, True),
        ("222100081 Ahmed Sameh  |  222100194 Adham Allam", 16, False),
        ("B20000006 Ahmed Wael  |  A20000011 Ibrahim Mohamed", 16, False),
        ("222100305 Amira Yasser", 16, False),
        ("", 12, False),
        ("SUPERVISOR: Associate Professor Mohamed Ghetas", 18, True),
    ]
    for i, (text, sz, bold) in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = text
        p.font.size = Pt(sz)
        p.font.bold = bold
        p.font.color.rgb = WHITE
        p.font.name = "Calibri"
        p.alignment = PP_ALIGN.CENTER


def add_toc_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide)
    add_header_bar(slide, "Table of Contents", 2)
    items = [
        "Abstract",
        "System Architecture & functions",
        "Related work",
        "Features",
        "Results",
        "Tools",
        "Running",
        "Future works",
        "Key Challenges & Limitations",
    ]
    for i, item in enumerate(items):
        num_box = slide.shapes.add_textbox(
            Inches(1.0), Inches(1.6 + i * 0.58), Inches(0.5), Inches(0.45)
        )
        num_box.text_frame.text = str(i + 1)
        num_box.text_frame.paragraphs[0].font.size = Pt(22)
        num_box.text_frame.paragraphs[0].font.bold = True
        num_box.text_frame.paragraphs[0].font.color.rgb = ACCENT_BLUE

        txt_box = slide.shapes.add_textbox(
            Inches(1.6), Inches(1.6 + i * 0.58), Inches(9.5), Inches(0.45)
        )
        txt_box.text_frame.text = item
        txt_box.text_frame.paragraphs[0].font.size = Pt(22)
        txt_box.text_frame.paragraphs[0].font.color.rgb = DARK_TEXT


def add_text_slide(prs, title: str, bullets: list[str], slide_num: int, image_path: Path | None = None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide)
    add_header_bar(slide, title, slide_num)
    if image_path and image_path.exists():
        slide.shapes.add_picture(str(image_path), Inches(6.8), Inches(1.35), width=Inches(5.8))
        add_bullets(slide, bullets, left=0.6, top=1.35, width=6.0, height=5.6, size=17)
    else:
        add_bullets(slide, bullets, size=19)


def add_screenshot_slide(prs, label: str, image_path: Path, slide_num: int):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide)
    add_header_bar(slide, label, slide_num)
    if image_path.exists():
        slide.shapes.add_picture(str(image_path), Inches(3.8), Inches(1.25), height=Inches(5.8))
    else:
        box = slide.shapes.add_textbox(Inches(2), Inches(3), Inches(9), Inches(1))
        box.text_frame.text = f"[Screenshot: {image_path.name}]"


def add_related_works_table(prs, slide_num: int):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide)
    add_header_bar(slide, "Related Works", slide_num)

    rows, cols = 9, 5
    table = slide.shapes.add_table(rows, cols, Inches(0.35), Inches(1.25), Inches(12.6), Inches(5.6)).table

    headers = ["Feature", "TrainMate\n(Our Project)", "Freeletics", "Nike Training Club", "Fitbod"]
    data = [
        ["Real-time Pose Tracking", "Yes", "Limited", "No", "No"],
        ["Auto Exercise Classification", "Yes (BiLSTM)", "No", "No", "Limited"],
        ["Rep Counting & Form Feedback", "Yes", "No", "No", "No"],
        ["AI Fitness Chatbot", "Yes (context-aware)", "No", "No", "No"],
        ["Body Progress Analysis", "Yes (Before/After)", "No", "No", "No"],
        ["Personalized Workout Plans", "Yes", "Yes", "Yes", "Yes"],
        ["On-device ML Inference", "Yes (TFLite)", "No", "No", "No"],
        ["Bilingual UI (EN/AR)", "Yes", "No", "Partial", "No"],
    ]

    for c, h in enumerate(headers):
        cell = table.cell(0, c)
        cell.text = h
        for p in cell.text_frame.paragraphs:
            p.font.bold = True
            p.font.size = Pt(11)
            p.font.color.rgb = WHITE
        cell.fill.solid()
        cell.fill.fore_color.rgb = DARK_BLUE

    for r, row in enumerate(data, start=1):
        for c, val in enumerate(row):
            cell = table.cell(r, c)
            cell.text = val
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(11)
                p.font.color.rgb = DARK_TEXT
            if c == 0:
                for p in cell.text_frame.paragraphs:
                    p.font.bold = True
            if c == 1:
                cell.fill.solid()
                cell.fill.fore_color.rgb = LIGHT_GRAY


def add_tools_table(prs, slide_num: int):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide)
    add_header_bar(slide, "Tools", slide_num)

    rows, cols = 9, 2  # header + 8 tools
    table = slide.shapes.add_table(rows, cols, Inches(0.8), Inches(1.35), Inches(11.8), Inches(5.5)).table
    tools = [
        ("Flutter / Dart", "Mobile app UI, camera integration, on-device TFLite inference, bilingual interface."),
        ("FastAPI / Python", "REST API backend: authentication, plans, workouts, chatbot, and ML endpoints."),
        ("SQLite / SQLAlchemy", "Database for users, workout plans, sessions, and progress history."),
        ("TensorFlow / Keras", "BiLSTM exercise classifier training and optional server-side inference."),
        ("Google ML Kit Pose", "Real-time 33-landmark body pose detection from the phone camera."),
        ("TFLite", "On-device exercise classification for low-latency auto-detect mode."),
        ("MediaPipe / OpenCV", "Body progress analysis from before/after photos on the server."),
        ("Groq API (LLM)", "AI fitness chatbot, session reports, and optional vision narrative."),
    ]
    table.cell(0, 0).text = "Technology"
    table.cell(0, 1).text = "Purpose"
    for c in range(2):
        cell = table.cell(0, c)
        cell.fill.solid()
        cell.fill.fore_color.rgb = DARK_BLUE
        for p in cell.text_frame.paragraphs:
            p.font.bold = True
            p.font.size = Pt(14)
            p.font.color.rgb = WHITE

    for r, (tech, purpose) in enumerate(tools, start=1):
        table.cell(r, 0).text = tech
        table.cell(r, 1).text = purpose
        for c in range(2):
            for p in table.cell(r, c).text_frame.paragraphs:
                p.font.size = Pt(12)
                p.font.color.rgb = DARK_TEXT
            if c == 0:
                for p in table.cell(r, c).text_frame.paragraphs:
                    p.font.bold = True


def add_results_slide(prs, slide_num: int):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide)
    add_header_bar(slide, "Results", slide_num)

    bullets = [
        "Functional end-to-end mobile application developed (Flutter + FastAPI)",
        "100% BiLSTM exercise classification accuracy on validation set (4 exercises)",
        "Live rep counting validated on physical Android device (94 reps across 10 sessions)",
        "Real-time form fault detection (partial reps, hip sag, shallow squat, etc.)",
        "AI chatbot with user plan and workout context integration",
        "Body progress analysis with regional scores and plan alignment",
    ]
    add_bullets(slide, bullets, left=0.7, top=1.35, width=5.8, height=5.5, size=17)

    chart = RESULTS / "rep_counter_validation_chart.png"
    if chart.exists():
        slide.shapes.add_picture(str(chart), Inches(6.5), Inches(1.55), width=Inches(6.0))


def add_running_intro(prs, slide_num: int):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, DARK_BLUE)
    box = slide.shapes.add_textbox(Inches(1.2), Inches(2.2), Inches(10.8), Inches(3.5))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Running"
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER

    p2 = tf.add_paragraph()
    p2.text = (
        "The following screenshots demonstrate the complete workflow of TrainMate, "
        "from user registration to live exercise tracking, AI coaching, "
        "and body progress analysis."
    )
    p2.font.size = Pt(22)
    p2.font.color.rgb = WHITE
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(24)

    num = slide.shapes.add_textbox(Inches(12.3), Inches(6.9), Inches(0.8), Inches(0.4))
    num.text_frame.text = str(slide_num)
    num.text_frame.paragraphs[0].font.size = Pt(14)
    num.text_frame.paragraphs[0].font.color.rgb = ACCENT_BLUE


def add_section_title_slide(prs, title: str, slide_num: int):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, DARK_BLUE)
    box = slide.shapes.add_textbox(Inches(0.8), Inches(2.6), Inches(11.7), Inches(1.5))
    tf = box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER
    num = slide.shapes.add_textbox(Inches(12.3), Inches(6.9), Inches(0.8), Inches(0.4))
    num.text_frame.text = str(slide_num)
    num.text_frame.paragraphs[0].font.size = Pt(14)
    num.text_frame.paragraphs[0].font.color.rgb = ACCENT_BLUE


def add_architecture_diagram_slide(
    prs,
    subtitle: str,
    image_path: Path,
    bullets: list[str],
    slide_num: int,
):
    """Diagram on the left, explanation bullets on the right."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide)
    add_header_bar(slide, "System Architecture & functions", slide_num)

    sub = slide.shapes.add_textbox(Inches(0.55), Inches(1.12), Inches(12.2), Inches(0.4))
    stf = sub.text_frame
    stf.text = subtitle
    stf.paragraphs[0].font.size = Pt(17)
    stf.paragraphs[0].font.bold = True
    stf.paragraphs[0].font.color.rgb = ACCENT_BLUE

    if image_path.exists():
        slide.shapes.add_picture(
            str(image_path), Inches(0.45), Inches(1.65), width=Inches(6.35)
        )
    else:
        box = slide.shapes.add_textbox(Inches(1.5), Inches(3.5), Inches(4), Inches(1))
        box.text_frame.text = f"[Diagram: {image_path.name}]"

    add_bullets(slide, bullets, left=7.0, top=1.75, width=5.8, height=5.3, size=15)


class SlideCounter:
    def __init__(self, start: int = 1):
        self.n = start

    def next(self) -> int:
        current = self.n
        self.n += 1
        return current


def add_thank_you(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, DARK_BLUE)
    box = slide.shapes.add_textbox(Inches(0), Inches(2.8), Inches(13.333), Inches(1.5))
    tf = box.text_frame
    p = tf.paragraphs[0]
    p.text = "Thank You"
    p.font.size = Pt(54)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER


def main():
    # Ensure architecture diagrams exist before building slides
    import generate_architecture_diagrams as arch_gen
    arch_gen.main()

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    s = SlideCounter()

    add_title_slide(prs)
    s.next()
    add_toc_slide(prs)
    s.next()

    add_text_slide(
        prs,
        "Abstract",
        [
            "TrainMate is an intelligent mobile fitness assistant that helps users "
            "exercise correctly without needing a personal trainer at all times.",
            "It uses real-time pose estimation and a BiLSTM model to classify exercises, "
            "count repetitions, and provide instant form feedback through the phone camera.",
            "The platform includes personalized workout plans, session tracking, "
            "before/after body progress analysis, and a context-aware AI fitness chatbot.",
            "By combining on-device ML, live coaching, and cloud-based AI services "
            "in one mobile app, TrainMate helps users train safely and track progress "
            "through a simple, interactive, and bilingual (English/Arabic) interface.",
        ],
        s.next(),
    )

    # System Architecture section — one diagram per team member area
    add_section_title_slide(prs, "System Architecture & functions", s.next())

    arch_diagrams = [
        (
            "Use Case Diagram — Full Application",
            DIAGRAMS / "arch_use_case_overview.png",
            [
                "The user interacts with TrainMate through one mobile app.",
                "Account module: registration, email verification, and secure login.",
                "Workout module: create plans, start sessions, and save results.",
                "Live exercise module: auto-detect movement and count reps with form feedback.",
                "AI coaching module: chatbot answers and optional session reports.",
                "Body progress module: upload before/after photos and view analysis scores.",
            ],
        ),
        (
            "Exercise Detection System",
            DIAGRAMS / "arch_detection_clean.png",
            [
                "The phone camera captures live video during each workout.",
                "ML Kit detects 33 body landmarks on every processed frame.",
                "22 numeric features are extracted and grouped into 30-frame windows.",
                "A BiLSTM model classifies the exercise in real time on the device.",
                "If TFLite is unavailable, the same request falls back to the server.",
                "Supported classes: squat, push-up, shoulder press, and biceps curl.",
            ],
        ),
        (
            "Backend System",
            DIAGRAMS / "arch_backend_clean.png",
            [
                "The Flutter app communicates with a FastAPI REST backend using JWT tokens.",
                "Separate routers handle auth, users, plans, workouts, chat, and ML endpoints.",
                "Business logic validates requests, sends emails, and estimates calories.",
                "SQLAlchemy stores users, profiles, workout plans, and session history in SQLite.",
                "External services provide email delivery and LLM-powered AI features.",
                "This layer connects all mobile features to persistent data and cloud AI.",
            ],
        ),
        (
            "Chatbot System",
            DIAGRAMS / "arch_chatbot_clean.png",
            [
                "The user opens the in-app chatbot and sends text, voice, or an image.",
                "The mobile app forwards the message to POST /api/chat with the JWT token.",
                "The backend loads the user's profile, active plan, and recent workouts.",
                "A system prompt is built so the AI knows the user's training context.",
                "Groq LLM generates a personalized coach reply in English or Arabic.",
                "The response is returned to the app and displayed in the chat UI.",
            ],
        ),
        (
            "Form Feedback & Body Progress",
            DIAGRAMS / "arch_feedback_clean.png",
            [
                "Live feedback runs on the phone: pose → angles → rep counter → HUD.",
                "A finite-state machine counts reps when the user completes each movement.",
                "Form faults such as partial reps or hip sag are detected in parallel.",
                "Instant messages guide the user to correct their technique during the set.",
                "After plan completion, before/after photos are analyzed on the server.",
                "MediaPipe extracts body metrics and returns regional progress scores.",
            ],
        ),
    ]
    for subtitle, img, bullets in arch_diagrams:
        add_architecture_diagram_slide(prs, subtitle, img, bullets, s.next())

    # Related works
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide)
    add_header_bar(slide, "Related Works", s.next())
    add_related_works_table(prs, s.next())

    add_text_slide(
        prs,
        "Features",
        [
            "Live Pose-Based Exercise Tracking: Real-time body landmark detection via camera.",
            "AI Exercise Classification: Auto-detect squat, push-up, shoulder press, biceps curl.",
            "Rep Counting & Form Feedback: FSM-based counting with fault messages.",
            "Personalized Workout Plans: Built-in templates with session targets and completion flow.",
            "User Authentication System: Secure registration, email verification, JWT login.",
            "Body Progress Analysis: Before/after photo comparison with regional scores.",
            "AI Fitness Chatbot: Context-aware coaching using plan and workout history.",
            "Bilingual Interface: Full English and Arabic UI support.",
            "Session Reports: Optional AI-generated summary after each workout.",
        ],
        s.next(),
    )

    add_tools_table(prs, s.next())
    add_results_slide(prs, s.next())

    screenshots = [
        ("HOME PAGE", SCREENS / "03_home.png"),
        ("USER REGISTRATION", SCREENS / "01_login.png"),
        ("EXERCISE SETUP", SCREENS / "05_exercise_setup.png"),
        ("LIVE EXERCISE TRACKING", SCREENS / "07_exercise_live.png"),
        ("FORM FEEDBACK HUD", SCREENS / "08_exercise_hud.png"),
        ("PROFILE MANAGEMENT", SCREENS / "09_profile.png"),
    ]
    for label, path in screenshots:
        add_screenshot_slide(prs, label, path, s.next())

    add_running_intro(prs, s.next())

    running_shots = [
        ("WORKOUT HUB", SCREENS / "04_workout_hub.png"),
        ("EXERCISE COACHING", SCREENS / "06_exercise_coaching.png"),
        ("AI CHATBOT", SCREENS / "15_chatbot.png"),
        ("BODY PROGRESS ANALYSIS", SCREENS / "12_plan_form.png"),
    ]
    for label, path in running_shots:
        add_screenshot_slide(prs, label, path, s.next())

    add_text_slide(
        prs,
        "Key Challenges & Limitations",
        [
            "Support tool only — not a replacement for professional fitness coaching.",
            "Pose detection accuracy varies with lighting, camera angle, and clothing.",
            "Classifier trained on 4 exercises only — other movements are not supported.",
            "Rep counting depends on clear full-body visibility in the camera frame.",
            "Body progress analysis requires valid before/after full-body photos.",
            "Complex multi-module integration (mobile ML + backend + LLM APIs).",
        ],
        s.next(),
    )

    add_text_slide(
        prs,
        "Future Work",
        [
            "Expanding support to additional exercises and equipment types.",
            "Training on larger and more diverse real-world pose datasets.",
            "Improving form feedback with deeper learning-based analysis.",
            "Adding wearable sensor integration (heart rate, calories).",
            "iOS release and cross-platform optimization.",
            "Enhanced offline mode for workouts without network connectivity.",
        ],
        s.next(),
    )

    add_thank_you(prs)

    prs.save(str(OUT))
    print(f"Saved: {OUT} ({s.n - 1} slides)")


if __name__ == "__main__":
    main()