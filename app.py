import os
import time
import re
import base64
from urllib.parse import quote_plus
import streamlit as st
from dotenv import load_dotenv
from core.llm_client import DEFAULT_MODEL, TASK_MODEL_DEFAULTS

# Load environment variables from .env
load_dotenv()

# Initialize theme state
if "theme" not in st.session_state:
    st.session_state.theme = "light"

def load_file_base64(path: str) -> str | None:
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


WALLPAPER_B64 = load_file_base64("wallpaper.jpg")
WALLPAPER_CSS_URL = (
    f"url('data:image/jpeg;base64,{WALLPAPER_B64}')"
    if WALLPAPER_B64
    else "none"
)

# Inject theme CSS dynamically based on light/dark mode selection
if st.session_state.theme == "light":
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600&family=Inter:wght@300;400;500;600;700&display=swap');
        :root {
            --nova-bg: linear-gradient(135deg, #F8FAFC 0%, #EEF2F7 100%);
            --nova-surface: #FFFFFF;
            --nova-surface-alt: #F1F5F9;
            --nova-border: #D8E1EC;
            --nova-text: #0F172A;
            --nova-muted: #475569;
            --nova-button-bg: #DBEAFE;
            --nova-button-text: #111827;
            --nova-button-border: #BFDBFE;
            --nova-accent: #64748B;
        }
        
        .stApp {
            background-color: #F4F7FB;
            background-image:
                linear-gradient(rgba(255,255,255,0.66), rgba(255,255,255,0.66)),
                __WALLPAPER__,
                radial-gradient(circle at 18% 16%, rgba(191,219,254,0.42), transparent 24%),
                radial-gradient(circle at 84% 14%, rgba(196,181,253,0.18), transparent 20%),
                radial-gradient(circle at 60% 82%, rgba(148,163,184,0.12), transparent 24%),
                linear-gradient(90deg, rgba(148,163,184,0.08) 1px, transparent 1px),
                linear-gradient(rgba(148,163,184,0.08) 1px, transparent 1px);
            background-size: cover, cover, auto, auto, auto, 26px 26px, 26px 26px;
            background-position: center center, center center, center, center, center, center, center;
            background-repeat: no-repeat, no-repeat, no-repeat, no-repeat, no-repeat, repeat, repeat;
            font-family: 'Inter', sans-serif;
            color: var(--nova-text);
        }
        
        /* Overrides for Light Mode */
        .stApp p, .stApp span, .stApp label, .stApp li {
            color: var(--nova-muted) !important;
        }
        .stApp button, .stApp input, .stApp textarea, .stApp select {
            font-family: 'Inter', sans-serif !important;
        }
        
        .main-title {
            font-size: 3.2rem;
            font-weight: 800;
            background: linear-gradient(90deg, #0F172A 0%, #475569 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            font-family: 'Playfair Display', serif;
        }
        
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #E2E8F0 !important;
        }
        div[data-testid="stAppViewContainer"] .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        section[data-testid="stSidebar"] .stMarkdown h1,
        section[data-testid="stSidebar"] .stMarkdown h2,
        section[data-testid="stSidebar"] .stMarkdown h3,
        section[data-testid="stSidebar"] .stMarkdown h4 {
            color: #0F172A !important;
        }
        section[data-testid="stSidebar"] .stMarkdown p {
            color: #334155 !important;
        }
        .badge {
            padding: 5px 12px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            display: inline-block;
        }
        .badge-beginner {
            background-color: #F8FAFC !important;
            color: #334155 !important;
            border: 1px solid #CBD5E1 !important;
        }
        .badge-intermediate {
            background-color: #EEF2F7 !important;
            color: #334155 !important;
            border: 1px solid #CBD5E1 !important;
        }
        
        .lesson-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-left: 5px solid #475569;
            border-radius: 16px;
            padding: 26px;
            margin-bottom: 24px;
            box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.08);
        }
        .lesson-card h4, .lesson-card h1, .lesson-card h2, .lesson-card h3 {
            font-family: 'Playfair Display', serif;
            color: #111827 !important;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .lesson-card p, .lesson-card li, .lesson-card div {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 1.05rem;
            line-height: 1.65;
            color: #334155 !important;
        }
        
        .quiz-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-left: 5px solid #334155;
            border-radius: 16px;
            padding: 26px;
            margin-bottom: 24px;
            box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.08);
        }
        
        .evaluator-card {
            background: #F8FAFC;
            border: 1px dashed #CBD5E1;
            border-radius: 12px;
            padding: 18px;
            margin-top: 15px;
        }
        
        .stTextInput>div>div>input {
            background-color: #FFFFFF !important;
            color: #111827 !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 10px !important;
        }
        .stSelectbox>div>div>div {
            background-color: #FFFFFF !important;
            color: #111827 !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 10px !important;
        }
        .stForm {
            background: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 16px !important;
            padding: 24px !important;
            box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05);
        }
        
        .stButton>button,
        .stDownloadButton>button,
        button[kind="primary"] {
            background: var(--nova-button-bg) !important;
            color: var(--nova-button-text) !important;
            -webkit-text-fill-color: var(--nova-button-text) !important;
            border: 1px solid var(--nova-button-border) !important;
            border-radius: 9999px !important;
            padding: 10px 24px !important;
            font-weight: 700 !important;
            font-family: 'Inter', sans-serif !important;
            text-transform: uppercase !important;
            letter-spacing: 0.06em !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 14px rgba(59, 130, 246, 0.14) !important;
        }
        .stButton>button:hover,
        .stDownloadButton>button:hover,
        button[kind="primary"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.22) !important;
        }
        
        div[data-testid="stMarkdownContainer"] p {
            color: var(--nova-muted) !important;
        }
    </style>
    """.replace("__WALLPAPER__", WALLPAPER_CSS_URL), unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600&family=Inter:wght@300;400;500;600;700&display=swap');
        :root {
            --nova-bg: linear-gradient(135deg, #0B1120 0%, #111827 100%);
            --nova-surface: #0F172A;
            --nova-surface-alt: #111827;
            --nova-border: #243044;
            --nova-text: #E5E7EB;
            --nova-muted: #CBD5E1;
            --nova-button-bg: #DBEAFE;
            --nova-button-text: #111827;
            --nova-button-border: #BFDBFE;
            --nova-accent: #94A3B8;
        }
        
        .stApp {
            background-color: #0B1120;
            background-image:
                linear-gradient(rgba(11,17,32,0.42), rgba(11,17,32,0.42)),
                __WALLPAPER__,
                radial-gradient(circle at 16% 18%, rgba(96,165,250,0.12), transparent 24%),
                radial-gradient(circle at 84% 10%, rgba(167,139,250,0.12), transparent 18%),
                radial-gradient(circle at 70% 82%, rgba(148,163,184,0.10), transparent 20%),
                linear-gradient(90deg, rgba(148,163,184,0.08) 1px, transparent 1px),
                linear-gradient(rgba(148,163,184,0.08) 1px, transparent 1px);
            background-size: cover, cover, auto, auto, auto, 26px 26px, 26px 26px;
            background-position: center center, center center, center, center, center, center, center;
            background-repeat: no-repeat, no-repeat, no-repeat, no-repeat, no-repeat, repeat, repeat;
            font-family: 'Inter', sans-serif;
            color: var(--nova-text);
        }
        
        /* Overrides for Night Eye Mode */
        .stApp p, .stApp span, .stApp label, .stApp li {
            color: var(--nova-muted) !important;
        }
        .stApp button, .stApp input, .stApp textarea, .stApp select {
            font-family: 'Inter', sans-serif !important;
        }
        
        .main-title {
            font-size: 3.2rem;
            font-weight: 800;
            background: linear-gradient(90deg, #E5E7EB 0%, #94A3B8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            font-family: 'Playfair Display', serif;
        }
        
        section[data-testid="stSidebar"] {
            background-color: #0F172A !important;
            border-right: 1px solid #1F2937 !important;
        }
        div[data-testid="stAppViewContainer"] .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        section[data-testid="stSidebar"] .stMarkdown h1,
        section[data-testid="stSidebar"] .stMarkdown h2,
        section[data-testid="stSidebar"] .stMarkdown h3,
        section[data-testid="stSidebar"] .stMarkdown h4 {
            color: #F8FAFC !important;
        }
        section[data-testid="stSidebar"] .stMarkdown p {
            color: #CBD5E1 !important;
        }
        .badge {
            padding: 5px 12px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            display: inline-block;
        }
        .badge-beginner {
            background-color: rgba(148,163,184,0.12) !important;
            color: #E5E7EB !important;
            border: 1px solid rgba(148,163,184,0.22) !important;
        }
        .badge-intermediate {
            background-color: rgba(100,116,139,0.12) !important;
            color: #E5E7EB !important;
            border: 1px solid rgba(100,116,139,0.22) !important;
        }
        
        .lesson-card {
            background: #0F172A;
            border: 1px solid #1F2937;
            border-left: 5px solid #475569;
            border-radius: 16px;
            padding: 26px;
            margin-bottom: 24px;
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.35);
        }
        .lesson-card h4, .lesson-card h1, .lesson-card h2, .lesson-card h3 {
            font-family: 'Playfair Display', serif;
            color: #F8FAFC !important;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .lesson-card p, .lesson-card li, .lesson-card div {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 1.05rem;
            line-height: 1.65;
            color: #CBD5E1 !important;
        }
        
        .quiz-card {
            background: #0F172A;
            border: 1px solid #1F2937;
            border-left: 5px solid #334155;
            border-radius: 16px;
            padding: 26px;
            margin-bottom: 24px;
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.35);
        }
        
        .evaluator-card {
            background: rgba(148,163,184,0.08);
            border: 1px dashed rgba(148,163,184,0.26);
            border-radius: 12px;
            padding: 18px;
            margin-top: 15px;
        }
        
        .stTextInput>div>div>input {
            background-color: #0F172A !important;
            color: #F8FAFC !important;
            border: 1px solid #1F2937 !important;
            border-radius: 10px !important;
        }
        .stSelectbox>div>div>div {
            background-color: #0F172A !important;
            color: #F8FAFC !important;
            border: 1px solid #1F2937 !important;
            border-radius: 10px !important;
        }
        .stForm {
            background: #0F172A !important;
            border: 1px solid #1F2937 !important;
            border-radius: 16px !important;
            padding: 24px !important;
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.3);
        }
        
        .stButton>button,
        .stDownloadButton>button,
        button[kind="primary"] {
            background: var(--nova-button-bg) !important;
            color: var(--nova-button-text) !important;
            -webkit-text-fill-color: var(--nova-button-text) !important;
            border: 1px solid var(--nova-button-border) !important;
            border-radius: 9999px !important;
            padding: 10px 24px !important;
            font-weight: 700 !important;
            font-family: 'Inter', sans-serif !important;
            text-transform: uppercase !important;
            letter-spacing: 0.06em !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 14px rgba(59, 130, 246, 0.14) !important;
        }
        .stButton>button:hover,
        .stDownloadButton>button:hover,
        button[kind="primary"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.22) !important;
        }
        
        div[data-testid="stMarkdownContainer"] p {
            color: var(--nova-muted) !important;
        }
    </style>
    """.replace("__WALLPAPER__", WALLPAPER_CSS_URL), unsafe_allow_html=True)

# Safety check for Groq API key
api_key = os.getenv("GROQ_API_KEY")
model_name = os.getenv("LLM_MODEL", DEFAULT_MODEL)
_is_placeholder = not api_key or not api_key.strip().startswith("gsk_")


def save_env_value(key: str, value: str) -> None:
    env_path = ".env"
    lines = []
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

    updated = False
    for idx, line in enumerate(lines):
        if line.strip().startswith(f"{key}="):
            lines[idx] = f"{key}={value}\n"
            updated = True
            break

    if not updated:
        lines.append(f"{key}={value}\n")

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)


if _is_placeholder:
    st.warning("⚠️ A valid Groq API key was not found. Enter your `gsk_...` key to continue.")
    api_key_input = st.text_input("Enter your Groq API Key:", type="password", placeholder="gsk_...")
    model_input = st.text_input("Global fallback model ID:", value=model_name, help="Used only if no task-specific default is set.")
    if api_key_input and api_key_input.strip().startswith("gsk_"):
        try:
            save_env_value("GROQ_API_KEY", api_key_input.strip())
            save_env_value("LLM_MODEL", (model_input or DEFAULT_MODEL).strip())
            for task_name, task_model in TASK_MODEL_DEFAULTS.items():
                save_env_value(f"LLM_MODEL_{task_name.upper()}", task_model)
            os.environ["GROQ_API_KEY"] = api_key_input.strip()
            os.environ["LLM_MODEL"] = (model_input or DEFAULT_MODEL).strip()
            for task_name, task_model in TASK_MODEL_DEFAULTS.items():
                os.environ[f"LLM_MODEL_{task_name.upper()}"] = task_model
            st.success("✅ Groq API key and model saved to .env and loaded successfully!")
        except Exception:
            os.environ["GROQ_API_KEY"] = api_key_input.strip()
            os.environ["LLM_MODEL"] = (model_input or DEFAULT_MODEL).strip()
            for task_name, task_model in TASK_MODEL_DEFAULTS.items():
                os.environ[f"LLM_MODEL_{task_name.upper()}"] = task_model
            st.success("✅ Groq API key loaded successfully for this session!")
        st.rerun()
    elif api_key_input:
        st.error("❌ That doesn't look like a valid Groq API key. It should start with `gsk_`.")
    st.info("💡 Create a Groq key at [console.groq.com/keys](https://console.groq.com/keys)")
    st.stop()

# Now import orchestrator and guardrails safely
from agents.orchestrator import StudyBuddyOrchestrator
from core.guardrails import is_educational_and_safe, sanitize_input

# Initialize the orchestrator
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = StudyBuddyOrchestrator()

orchestrator = st.session_state.orchestrator

# Initialize session states
if "state" not in st.session_state:
    st.session_state.state = None
if "explanation" not in st.session_state:
    st.session_state.explanation = None
if "question" not in st.session_state:
    st.session_state.question = None
if "graded" not in st.session_state:
    st.session_state.graded = None
if "exam_questions" not in st.session_state:
    st.session_state.exam_questions = None
if "exam_graded" not in st.session_state:
    st.session_state.exam_graded = None
if "exam_score" not in st.session_state:
    st.session_state.exam_score = None
if "slides_html" not in st.session_state:
    st.session_state.slides_html = None
if "quiz_round" not in st.session_state:
    st.session_state.quiz_round = None
if "quiz_round_idx" not in st.session_state:
    st.session_state.quiz_round_idx = 0
if "quiz_round_results" not in st.session_state:
    st.session_state.quiz_round_results = []
if "flashcards_html" not in st.session_state:
    st.session_state.flashcards_html = None
if "smart_flashcards" not in st.session_state:
    st.session_state.smart_flashcards = []
if "concept_stage" not in st.session_state:
    st.session_state.concept_stage = "lesson"
if "review_concept" not in st.session_state:
    st.session_state.review_concept = None
if "focus_mode" not in st.session_state:
    st.session_state.focus_mode = None
if "focus_started_at" not in st.session_state:
    st.session_state.focus_started_at = None
if "focus_ends_at" not in st.session_state:
    st.session_state.focus_ends_at = None
if "focus_duration_minutes" not in st.session_state:
    st.session_state.focus_duration_minutes = None
if "focus_label" not in st.session_state:
    st.session_state.focus_label = None
if "focus_paused_remaining" not in st.session_state:
    st.session_state.focus_paused_remaining = None

def reset_session():
    st.session_state.state = None
    st.session_state.explanation = None
    st.session_state.question = None
    st.session_state.graded = None
    st.session_state.exam_questions = None
    st.session_state.exam_graded = None
    st.session_state.exam_score = None
    st.session_state.slides_html = None
    st.session_state.quiz_round = None
    st.session_state.quiz_round_idx = 0
    st.session_state.quiz_round_results = []
    st.session_state.flashcards_html = None
    st.session_state.smart_flashcards = []
    st.session_state.concept_stage = "lesson"
    st.session_state.review_concept = None
    st.session_state.focus_mode = None
    st.session_state.focus_started_at = None
    st.session_state.focus_ends_at = None
    st.session_state.focus_duration_minutes = None
    st.session_state.focus_label = None
    st.session_state.focus_paused_remaining = None

def reset_concept_flow(clear_explanation: bool = True):
    if clear_explanation:
        st.session_state.explanation = None
    st.session_state.question = None
    st.session_state.graded = None
    st.session_state.quiz_round = None
    st.session_state.quiz_round_idx = 0
    st.session_state.quiz_round_results = []
    st.session_state.flashcards_html = None
    st.session_state.smart_flashcards = []
    st.session_state.concept_stage = "lesson"
    st.session_state.review_concept = None
    st.session_state.focus_mode = None
    st.session_state.focus_started_at = None
    st.session_state.focus_ends_at = None
    st.session_state.focus_duration_minutes = None
    st.session_state.focus_label = None
    st.session_state.focus_paused_remaining = None

def start_focus_session(minutes: int, label: str) -> None:
    now = time.time()
    st.session_state.focus_mode = "active"
    st.session_state.focus_started_at = now
    st.session_state.focus_ends_at = now + (minutes * 60)
    st.session_state.focus_duration_minutes = minutes
    st.session_state.focus_label = label
    st.session_state.focus_paused_remaining = None

def pause_focus_session() -> None:
    if st.session_state.get("focus_mode") != "active":
        return
    remaining = remaining_focus_seconds()
    st.session_state.focus_mode = "paused"
    st.session_state.focus_paused_remaining = remaining
    st.session_state.focus_ends_at = None

def resume_focus_session() -> None:
    if st.session_state.get("focus_mode") != "paused":
        return
    remaining = int(st.session_state.get("focus_paused_remaining") or 0)
    if remaining <= 0:
        st.session_state.focus_mode = None
        st.session_state.focus_paused_remaining = None
        return
    now = time.time()
    st.session_state.focus_mode = "active"
    st.session_state.focus_started_at = now
    st.session_state.focus_ends_at = now + remaining
    st.session_state.focus_paused_remaining = None

def reset_focus_session() -> None:
    st.session_state.focus_mode = None
    st.session_state.focus_started_at = None
    st.session_state.focus_ends_at = None
    st.session_state.focus_duration_minutes = None
    st.session_state.focus_label = None
    st.session_state.focus_paused_remaining = None

def remaining_focus_seconds() -> int:
    if st.session_state.get("focus_mode") == "paused":
        return int(st.session_state.get("focus_paused_remaining") or 0)
    if not st.session_state.get("focus_ends_at"):
        return 0
    return max(0, int(st.session_state.focus_ends_at - time.time()))

def aura_status(completed: int, total: int) -> tuple[str, str]:
    if total <= 0 or completed <= 0:
        return "Initiation", "Starting point"
    ratio = completed / total
    if ratio < 0.25:
        return "Spark", "Momentum building"
    if ratio < 0.5:
        return "Flow", "Steady progress"
    if ratio < 0.8:
        return "Orbit", "Strong rhythm"
    if ratio < 1:
        return "Zenith", "Near mastery"
    return "Crown", "Topic complete"

def build_focus_timer_html(remaining_seconds: int, total_seconds: int, label: str, paused: bool = False) -> str:
    minutes = max(0, remaining_seconds // 60)
    seconds = max(0, remaining_seconds % 60)
    progress = 0 if total_seconds <= 0 else max(0, min(100, ((total_seconds - remaining_seconds) / total_seconds) * 100))
    status = "Paused" if paused else "In focus"
    ring = "#94A3B8" if paused else "#0F766E"
    fill = "#E2E8F0" if paused else "#DBEAFE"
    bg = "#FFFFFF" if st.session_state.theme == "light" else "#0F172A"
    text = "#0F172A" if st.session_state.theme == "light" else "#F8FAFC"
    muted = "#64748B" if st.session_state.theme == "light" else "#94A3B8"
    return f"""
    <div style="font-family: Inter, sans-serif; background: {bg}; border: 1px solid {'#E2E8F0' if st.session_state.theme == 'light' else '#243044'}; border-radius: 22px; padding: 18px; box-shadow: 0 18px 36px rgba(15,23,42,0.10);">
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom: 10px;">
            <div>
                <div style="font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: {muted}; margin-bottom: 4px;">Kairu</div>
                <div style="font-size: 15px; color: {text}; font-weight: 700;">{label}</div>
            </div>
            <div style="padding: 6px 10px; border-radius: 999px; background: {fill}; color: {ring}; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .08em;">{status}</div>
        </div>
        <div style="display:flex; justify-content:center;">
            <div style="width: 168px; height: 168px; border-radius: 50%; border: 10px solid {fill}; box-shadow: inset 0 0 0 6px {ring}; display:flex; flex-direction:column; align-items:center; justify-content:center;">
                <div style="font-size: 13px; color: {muted}; margin-bottom: 4px;">Focus</div>
                <div id="kairu-time" style="font-size: 42px; line-height: 1; color: {text}; font-weight: 800; letter-spacing: -0.06em;">{minutes:02d}:{seconds:02d}</div>
            </div>
        </div>
        <div style="margin-top: 14px; height: 8px; background: {'#E2E8F0' if st.session_state.theme == 'light' else '#1F2937'}; border-radius: 999px; overflow: hidden;">
            <div id="kairu-bar" style="height: 100%; width: {progress}%; background: {ring}; border-radius: 999px;"></div>
        </div>
        <div id="kairu-status" style="margin-top: 12px; font-size: 12px; color: {muted}; text-align:center;">{'Timer paused.' if paused else 'Stay focused. One session at a time.'}</div>
    </div>
    <script>
      let remaining = {remaining_seconds};
      const timeEl = document.getElementById('kairu-time');
      const barEl = document.getElementById('kairu-bar');
      const statusEl = document.getElementById('kairu-status');
      const total = {total_seconds};
      const paused = {str(paused).lower()};
      function render() {{
        const mins = String(Math.floor(Math.max(0, remaining) / 60)).padStart(2, '0');
        const secs = String(Math.max(0, remaining) % 60).padStart(2, '0');
        timeEl.textContent = `${{mins}}:${{secs}}`;
        const pct = total <= 0 ? 0 : Math.max(0, Math.min(100, ((total - Math.max(0, remaining)) / total) * 100));
        barEl.style.width = pct + '%';
        if (remaining <= 0) {{
          statusEl.textContent = 'Session complete. Take a short break.';
          clearInterval(timer);
        }}
        if (!paused) {{
          remaining -= 1;
        }}
      }}
      render();
      const timer = setInterval(render, 1000);
    </script>
    """

def load_music_bytes(path: str) -> bytes | None:
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return f.read()

def normalize_lesson_math(text: str) -> str:
    if not text:
        return text
    text = text.replace("\\[", "$$").replace("\\]", "$$")
    text = text.replace("\\(", "$").replace("\\)", "$")
    text = re.sub(r"\\{2}([A-Za-z]+)", r"\\\1", text)
    return text

def build_resource_recommendations(topic: str, subconcept: str) -> dict:
    query = quote_plus(f"{topic} {subconcept}".strip())
    video_query = quote_plus(f"{topic} {subconcept} explained")
    return {
        "reading": [
            {"label": "Wikipedia", "url": f"https://en.wikipedia.org/wiki/Special:Search?search={query}"},
            {"label": "Britannica", "url": f"https://www.britannica.com/search?query={query}"},
            {"label": "Khan Academy", "url": f"https://www.khanacademy.org/search?page_search_query={query}"},
        ],
        "videos": [
            {"label": "YouTube search", "url": f"https://www.youtube.com/results?search_query={video_query}"},
            {"label": "YouTube deep dive", "url": f"https://www.youtube.com/results?search_query={quote_plus(topic + ' ' + subconcept + ' lesson')}"},
        ],
    }

def parse_flashcards(text: str):
    """Extracts flashcards from tutor's output based on [FLASHCARD] tags."""
    if not text:
        return "", []
        
    parts = re.split(r'\[FLASHCARD\]', text)
    clean_explanation = parts[0].strip()
    clean_explanation = clean_explanation.replace("[FLASHCARD]", "").strip()
    return normalize_lesson_math(clean_explanation), []

# Sidebar Design
st.sidebar.markdown(
    "<h2 style='margin-top: 5px; margin-bottom: 0px;'>🐉 NOVA</h2>",
    unsafe_allow_html=True
)
st.sidebar.caption("Adaptive study workspace")
st.sidebar.write("---")

# Theme selector button (Night Eye / Light Mode)
theme_btn_label = "👁️ Night Eye Mode" if st.session_state.theme == "light" else "☀️ Light Mode"
if st.sidebar.button(theme_btn_label, key="theme_toggle_btn"):
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
    st.rerun()
st.sidebar.write("---")

music_bytes = load_music_bytes("liecio-calming-rain-257596.mp3")
if music_bytes:
    st.sidebar.markdown("### Cozy Study Music")
    st.sidebar.audio(music_bytes, format="audio/mp3", loop=True)
    st.sidebar.caption("Use the built-in controls to play or pause the loop.")
    st.sidebar.write("---")
else:
    st.sidebar.caption("Music file not found: `liecio-calming-rain-257596.mp3`")

st.sidebar.markdown("### Kairu Focus")
focus_col_a, focus_col_b = st.sidebar.columns(2)
with focus_col_a:
    if st.button("30 min", key="focus_30_min"):
        start_focus_session(30, "Focused 30")
        st.rerun()
with focus_col_b:
    if st.button("5 min", key="focus_5_min"):
        start_focus_session(5, "Quick 5")
        st.rerun()

focus_active_or_paused = st.session_state.get("focus_mode") in {"active", "paused"}
if focus_active_or_paused:
    remaining = remaining_focus_seconds()
    total_seconds = int((st.session_state.focus_duration_minutes or 0) * 60)
    focus_label = st.session_state.focus_label or "Focus Session"
    is_paused = st.session_state.get("focus_mode") == "paused"
    if remaining <= 0:
        st.success("Kairu session complete. Take a short break.")
    else:
        import streamlit.components.v1 as components
        components.html(
            build_focus_timer_html(remaining, total_seconds, focus_label, paused=is_paused),
            height=280,
        )
    stop_col_a, stop_col_b = st.sidebar.columns(2)
    with stop_col_a:
        if is_paused:
            if st.button("Resume", key="focus_resume"):
                resume_focus_session()
                st.rerun()
        else:
            if st.button("Pause", key="focus_pause"):
                pause_focus_session()
                st.rerun()
    with stop_col_b:
        if st.button("Reset", key="focus_reset"):
            reset_focus_session()
            st.rerun()
else:
    st.sidebar.caption("Start a 30 minute deep-work block or a 5 minute sprint.")

if st.session_state.state:
    state = st.session_state.state
    
    # Visualizing current difficulty level
    level = state["level"]
    level_class = "badge-beginner" if level == "beginner" else "badge-intermediate"
    st.sidebar.markdown(f"**Current Level:** <span class='badge {level_class}'>{level.upper()}</span>", unsafe_allow_html=True)
    st.sidebar.write(f"**Topic:** {state['topic']}")
    st.sidebar.write("---")

    completed_count = len(state.get("completed", []))
    total_count = len(state.get("subconcepts", []))
    aura_name, aura_note = aura_status(completed_count, total_count)
    aura_pct = completed_count / total_count if total_count else 0.0

    st.sidebar.markdown("### Aura Tracker")
    st.sidebar.metric("Topics completed", f"{completed_count}/{total_count}")
    st.sidebar.progress(aura_pct)
    st.sidebar.caption(f"**Aura:** {aura_name} - {aura_note}")
    st.sidebar.write("---")
    
    # Progress path rendering
    st.sidebar.markdown("### 🗺️ Learning Path")
    subconcepts = state["subconcepts"]
    current_idx = state["current_index"]
    
    for i, concept in enumerate(subconcepts):
        if concept in state["completed"]:
            st.sidebar.write(f"✅ {concept}")
        elif i == current_idx:
            st.sidebar.write(f"👉 **{concept}** *(Learning)*")
        else:
            st.sidebar.write(f"⚪ {concept}")
            
    st.sidebar.write("---")

    st.sidebar.caption(f"Session: `{state['session_id']}`")
    if st.sidebar.button("🔄 Study New Topic"):
        reset_session()
        st.rerun()

# Main Panel Design
    st.markdown("<h1 class='main-title' style='margin-top: 5px;'>NOVA: Adaptive Learning</h1>", unsafe_allow_html=True)

if not st.session_state.state:
    # Setup Page
    intro_text = "Welcome to NOVA, a calm study space for one concept at a time."
    sub_text = "Choose a topic or upload a chapter. NOVA will guide you through a lesson, a short quiz, and a clean review flow."
    muted = "#64748B" if st.session_state.theme == "light" else "#94A3B8"
    title_color = "#0F172A" if st.session_state.theme == "light" else "#F8FAFC"
    st.markdown(
        f"""
        <div style="max-width: 900px; margin: 0 0 1.25rem 0;">
            <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.14em; color: {muted}; margin-bottom: 0.35rem;">NOVA</div>
            <div style="font-family: 'Playfair Display', serif; font-size: 2.1rem; line-height: 1.15; color: {title_color}; font-weight: 800; margin-bottom: 0.55rem;">{intro_text}</div>
            <div style="font-size: 1rem; line-height: 1.75; color: {muted}; max-width: 760px;">{sub_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Mode Selection
    mode = st.radio("Choose how you want to learn:", ["Study by Topic Name", "Study from an uploaded PDF Document"])
    
    if mode == "Study by Topic Name":
        # Main Form for Topic Name
        with st.form("setup_form_topic"):
            topic_input = st.text_input("What academic topic do you want to learn?", value="Fractions", max_chars=100)
            start_level = st.selectbox(
                "Starting difficulty level:",
                options=["intermediate", "beginner"],
                index=0,
                help="Select 'intermediate' to easily test the difficulty-dropping adaptive loop."
            )
            submit_btn = st.form_submit_button("🚀 Generate Personalized Path")
            
        st.markdown("### Quick topics")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🍰 Fractions"):
                topic_input = "Fractions"
        with col2:
            if st.button("🌱 Photosynthesis"):
                topic_input = "Photosynthesis"
        with col3:
            if st.button("📐 Basic Algebra"):
                topic_input = "Basic Algebra"
                
        if submit_btn or (topic_input != "Fractions" and (st.session_state.get("last_topic") != topic_input)):
            st.session_state.last_topic = topic_input
            
            # 1. Input Sanitization
            sanitized_topic = sanitize_input(topic_input)
            
            with st.spinner("Evaluating topic safety and relevance..."):
                # 2. Topic Safety Guardrails
                is_safe, message = is_educational_and_safe(sanitized_topic)
                
            if not is_safe:
                st.error(f"❌ Safety Refusal: {message}")
            else:
                with st.spinner("Planner agent designing your learning path..."):
                    # 3. Create Session State & Generate Path
                    new_state = orchestrator.start_new_session(sanitized_topic, start_level)
                    st.session_state.state = new_state
                    st.success("Custom curriculum planned successfully!")
                    st.rerun()
    else:
        # Form for PDF Upload
        with st.form("setup_form_pdf"):
            topic_input = st.text_input("Enter a name for this study session (e.g. History Chapter 1):", value="My PDF Lesson", max_chars=100)
            uploaded_file = st.file_uploader("Upload a PDF document to learn from:", type=["pdf"])
            start_level = st.selectbox(
                "Starting difficulty level:",
                options=["intermediate", "beginner"],
                index=0,
                help="Select 'intermediate' to easily test the difficulty-dropping adaptive loop."
            )
            submit_pdf_btn = st.form_submit_button("🚀 Generate Path from PDF")
            
        if submit_pdf_btn:
            if not uploaded_file:
                st.error("Please upload a PDF file first.")
            else:
                # 1. Extract PDF Text in-memory
                with st.spinner("Extracting text from PDF..."):
                    from core.pdf_processor import extract_text_from_pdf
                    pdf_bytes = uploaded_file.read()
                    pdf_text = extract_text_from_pdf(pdf_bytes)
                
                if not pdf_text.strip():
                    st.error("❌ Failed to extract text from the PDF. Make sure it contains readable text.")
                else:
                    # 2. Input Sanitization & Safety Check
                    sanitized_topic = sanitize_input(topic_input)
                    with st.spinner("Evaluating safety of session topic..."):
                        is_safe, message = is_educational_and_safe(sanitized_topic)
                        
                    if not is_safe:
                        st.error(f"❌ Safety Refusal: {message}")
                    else:
                        # 3. Planner designs curriculum and creates session
                        with st.spinner("Planner agent analyzing PDF and designing learning path..."):
                            new_state = orchestrator.start_new_session(sanitized_topic, start_level, pdf_text=pdf_text)
                            st.session_state.state = new_state
                            st.success("Custom curriculum planned from PDF successfully!")
                            st.rerun()

else:
    state = st.session_state.state
    subconcepts = state["subconcepts"]
    current_idx = state["current_index"]
    
    # Calculate progress
    completed_count = len(state["completed"])
    total_count = len(subconcepts)
    progress_percentage = min(completed_count / total_count, 1.0) if total_count > 0 else 0.0
    
    st.caption(f"Course progress: {completed_count}/{total_count} concepts complete ({int(progress_percentage * 100)}%).")
    st.write("---")
    
    # Check if curriculum is fully completed
    if current_idx >= len(subconcepts):
        st.balloons()
        st.markdown("""
        <div style='text-align: center; padding: 25px; background: rgba(255, 111, 32, 0.1); border: 1px solid rgba(255, 111, 32, 0.3); border-radius: 16px; border-left: 5px solid #FF6F20; margin-bottom: 20px; backdrop-filter: blur(12px);'>
            <h2 style='color: #FF6F20; margin: 0;'>🎉 Curriculum Lessons Completed!</h2>
            <p style='color: #4A2E18; margin-top: 5px; margin-bottom: 0;'>Amazing job! You have successfully mastered all lessons. Now, complete the Final Course Exam to receive your Certificate.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🎓 Final Exam Check (10 Multiple Choice Questions)")
        
        if not st.session_state.exam_questions:
            if st.button("📝 Start Final Course Exam", type="primary"):
                with st.spinner("Quiz agent preparing your 10-question final exam..."):
                    st.session_state.exam_questions = orchestrator.get_final_exam(state)
                    st.rerun()
        else:
            questions = st.session_state.exam_questions
            
            if st.session_state.exam_score is None:
                # Display 10 questions in a form
                with st.form("final_exam_form"):
                    user_selections = []
                    for q_idx, q in enumerate(questions):
                        sel = st.radio(
                            label=f"**Question {q_idx+1}:** {q['question']}", 
                            options=q['options'], 
                            index=None, 
                            key=f"exam_radio_q_{q_idx}"
                        )
                        user_selections.append(sel)
                        st.write("---")
                        
                    submit_exam = st.form_submit_button("Submit Exam answers")
                    if submit_exam:
                        if None in user_selections:
                            st.warning("Please answer all 10 questions before submitting.")
                        else:
                            # Grade exam
                            score = 0
                            graded_results = []
                            for q_idx, q in enumerate(questions):
                                correct_idx = q["correct_index"]
                                correct_ans = q["options"][correct_idx]
                                user_ans = user_selections[q_idx]
                                is_correct = (user_ans == correct_ans)
                                if is_correct:
                                    score += 1
                                graded_results.append({
                                    "question": q["question"],
                                    "user_answer": user_ans,
                                    "correct_answer": correct_ans,
                                    "is_correct": is_correct,
                                    "explanation": q.get("explanation", "")
                                })
                            st.session_state.exam_score = score
                            st.session_state.exam_graded = graded_results
                            st.rerun()
            else:
                score = st.session_state.exam_score
                graded = st.session_state.exam_graded
                
                st.markdown(f"## 🏆 Your Final Exam Score: **{score} / 10**")
                if score >= 7:
                    st.success("🎉 Congratulations! You passed the course!")
                    
                    st.markdown("### Answer Key")
                    for idx, r in enumerate(graded):
                        with st.expander(f"Answer {idx+1}: {r['question']}", expanded=False):
                            st.write(f"**Correct Answer:** {r['correct_answer']}")
                            st.caption(f"*Rationale: {r['explanation']}*")
                    
                    # Generate Certificate HTML
                    cert_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Certificate of Completion</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;800&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Outfit', sans-serif;
            background-color: #f3f4f6;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }}
        .certificate-container {{
            width: 800px;
            height: 550px;
            background: white;
            border: 15px solid #4f46e5;
            border-image: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%) 15;
            padding: 40px;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            position: relative;
        }}
        .title {{
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(90deg, #4f46e5 0%, #06b6d4 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        .subtitle {{
            font-size: 1.25rem;
            color: #4b5563;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 40px;
        }}
        .presented-to {{
            font-size: 1.1rem;
            color: #6b7280;
            margin-bottom: 10px;
        }}
        .student-name {{
            font-size: 2.25rem;
            font-weight: 700;
            color: #111827;
            border-bottom: 2px solid #e5e7eb;
            display: inline-block;
            padding-bottom: 5px;
            margin-bottom: 30px;
        }}
        .course-name {{
            font-size: 1.5rem;
            color: #374151;
            margin-bottom: 40px;
        }}
        .date-signature {{
            display: flex;
            justify-content: space-between;
            margin-top: 50px;
            padding: 0 50px;
        }}
        .item {{
            border-top: 1px solid #d1d5db;
            padding-top: 10px;
            width: 200px;
            color: #6b7280;
            font-size: 0.9rem;
        }}
        .badge {{
            position: absolute;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            background: #eff6ff;
            color: #1e40af;
            padding: 8px 16px;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 700;
            border: 1px solid #bfdbfe;
        }}
    </style>
</head>
<body>
    <div class="certificate-container">
        <div class="title">NOVA</div>
        <div class="subtitle">Certificate of Completion</div>
        <div class="presented-to">This is proudly presented to the scholar who mastered</div>
        <div class="student-name">NOVA Graduate</div>
        <div class="course-name">Course Topic: <strong>{state['topic']}</strong></div>
        <div class="badge">Final Score: {score}/10 (Passed)</div>
        <div class="date-signature">
            <div class="item">Date Issued</div>
            <div class="item">NOVA Adaptive Agent</div>
        </div>
    </div>
</body>
</html>"""
                    st.download_button(
                        label="🎓 Download Certificate of Completion",
                        data=cert_html,
                        file_name="studybuddy_certificate.html",
                        mime="text/html"
                    )
                else:
                    st.error("❌ You did not pass. You need at least 7/10 to unlock your Certificate of Completion.")
                    if st.button("🔄 Retake Exam"):
                        st.session_state.exam_score = None
                        st.session_state.exam_graded = None
                        st.rerun()
                        
                # Detailed exam breakdown
                st.write("### 📝 Exam Review Breakdown:")
                for idx, r in enumerate(graded):
                    c_status = "✅ Correct" if r["is_correct"] else "❌ Incorrect"
                    with st.expander(f"Question {idx+1}: {r['question']} - {c_status}"):
                        st.write(f"**Your Answer:** {r['user_answer']}")
                        st.write(f"**Correct Answer:** {r['correct_answer']}")
                        st.caption(f"*Rationale: {r['explanation']}*")
                        
        st.write("---")
        st.write("### 📈 Course Progress log:")
        st.write(state["history"])
        
        if st.button("Study another topic"):
            reset_session()
            st.session_state.exam_questions = None
            st.session_state.exam_graded = None
            st.session_state.exam_score = None
            st.session_state.slides_html = None
            st.rerun()
            
        st.stop()
        
    current_concept = st.session_state.review_concept if st.session_state.get("concept_stage") == "review" and st.session_state.review_concept else subconcepts[current_idx]
    
    st.write(f"### Current Concept: **{current_concept}**")
    
    # Tutor Agent generates lesson once per concept
    if not st.session_state.explanation:
        with st.spinner("Tutor agent preparing explanation..."):
            explanation = orchestrator.get_explanation(state)
            st.session_state.explanation = explanation
    else:
        explanation = st.session_state.explanation

    clean_exp, _ = parse_flashcards(explanation)
    current_stage = st.session_state.get("concept_stage", "lesson")

    if current_stage == "lesson":
        st.markdown("<div class='lesson-card'>", unsafe_allow_html=True)
        st.markdown("#### 📖 Lesson Explanation")
        st.markdown(clean_exp)
        resources = build_resource_recommendations(state["topic"], current_concept)
        st.markdown("#### 🔎 Recommended Reading & Videos")
        res_col_1, res_col_2 = st.columns(2)
        with res_col_1:
            st.markdown("**Read more**")
            for item in resources["reading"]:
                st.markdown(f"- [{item['label']}]({item['url']})")
        with res_col_2:
            st.markdown("**Watch next**")
            for item in resources["videos"]:
                st.markdown(f"- [{item['label']}]({item['url']})")
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("➡️ Start Quiz for This Concept", type="primary"):
            st.session_state.concept_stage = "quiz"
            st.rerun()

    elif current_stage == "quiz":
        st.markdown("<div class='quiz-card'>", unsafe_allow_html=True)
        st.markdown("#### 📝 Concept Check (3 Questions)")

        if not st.session_state.quiz_round:
            with st.spinner("Quiz agent preparing 3 questions for this concept..."):
                quiz_round = orchestrator.get_quiz_questions_batch(state, explanation, n=3)
                st.session_state.quiz_round = quiz_round
                st.session_state.quiz_round_idx = 0
                st.session_state.quiz_round_results = []

        quiz_round = st.session_state.quiz_round
        q_idx = st.session_state.quiz_round_idx
        total_qs = len(quiz_round)

        if q_idx < total_qs and not st.session_state.graded:
            question_data = quiz_round[q_idx]
            st.markdown(f"**Question {q_idx + 1} of {total_qs}:**")
            options = question_data.get("options", [])
            selected_option = st.radio(
                label=question_data.get("question", ""),
                options=options,
                index=None,
                key=f"mcq_round_radio_{q_idx}"
            )
            st.write("---")
            if st.button(f"Submit Answer ({q_idx + 1}/{total_qs})", type="primary"):
                if selected_option is None:
                    st.warning("Please select an option before submitting.")
                else:
                    grade = orchestrator.quiz.grade_answer(question_data, selected_option)
                    st.session_state.quiz_round_results.append({
                        "correct": grade["correct"],
                        "feedback": grade["explanation"],
                        "question": question_data.get("question", ""),
                        "selected": selected_option
                    })
                    next_q_idx = q_idx + 1
                    st.session_state.quiz_round_idx = next_q_idx

                    if next_q_idx >= total_qs:
                        round_results = st.session_state.quiz_round_results
                        correct_count = sum(1 for r in round_results if r["correct"])
                        passed = correct_count >= 2

                        combined_feedback = f"**Round Complete:** {correct_count}/{total_qs} correct.\n\n"
                        for i, r in enumerate(round_results):
                            status = "✅" if r["correct"] else "❌"
                            combined_feedback += f"{status} **Q{i+1}:** {r['feedback']}\n\n"

                        evaluation = orchestrator.evaluator.evaluate(
                            state["level"], passed, combined_feedback
                        )

                        current_subconcept = state["subconcepts"][state["current_index"]]
                        st.session_state.review_concept = current_subconcept
                        if current_subconcept not in state["scores"]:
                            state["scores"][current_subconcept] = []
                        state["scores"][current_subconcept].append(passed)
                        state["history"].append({
                            "subconcept": current_subconcept,
                            "level": state["level"],
                            "correct": passed,
                            "action": evaluation["action"],
                            "next_level": evaluation["next_level"],
                            "reasoning": evaluation.get("reasoning", ""),
                            "score": f"{correct_count}/{total_qs}"
                        })

                        if correct_count < total_qs:
                            smart_cards = orchestrator.flashcard_agent.generate_mistake_flashcards(
                                [current_subconcept],
                                state["level"]
                            )
                            if smart_cards:
                                st.session_state.smart_flashcards = smart_cards
                                st.session_state.flashcards_html = orchestrator.flashcard_agent.build_html_flashcard_deck(
                                    smart_cards,
                                    title="Smart Revision Flashcards"
                                )
                            else:
                                st.session_state.smart_flashcards = []
                                st.session_state.flashcards_html = None
                        else:
                            st.session_state.smart_flashcards = []
                            st.session_state.flashcards_html = None

                        if evaluation["action"] == "advance":
                            if current_subconcept not in state["completed"]:
                                state["completed"].append(current_subconcept)
                            state["current_index"] += 1
                        state["level"] = evaluation["next_level"]

                        orchestrator.save_session(state)
                        st.session_state.graded = {
                            "correct": passed,
                            "feedback": combined_feedback,
                            "evaluation": evaluation,
                            "next_state": state
                        }
                        st.session_state.state = state
                        st.session_state.concept_stage = "review"
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    elif current_stage == "review" and st.session_state.graded:
        result = st.session_state.graded
        correct = result["correct"]
        feedback = result["feedback"]
        evaluation = result["evaluation"]
        round_results = st.session_state.get("quiz_round_results", [])
        correct_count = sum(1 for r in round_results if r["correct"])
        total_qs_done = len(round_results)

        st.markdown("<div class='quiz-card'>", unsafe_allow_html=True)
        st.markdown("#### ✅ Quiz Review")

        if correct:
            st.success(f"🎉 **Passed!** {correct_count}/{total_qs_done} correct — great work!")
        else:
            st.error(f"❌ **Not yet.** {correct_count}/{total_qs_done} correct — need ≥2 to advance.")

        with st.expander("📋 See detailed feedback", expanded=True):
            st.markdown(feedback)

        st.markdown("<div class='evaluator-card'>", unsafe_allow_html=True)
        st.markdown(f"🔄 **Evaluator Decision:** Action: `{evaluation['action'].upper()}` | Next Level: `{evaluation['next_level'].upper()}`")
        st.caption(f"*Rationale: {evaluation['reasoning']}*")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.smart_flashcards:
            card_count = len(st.session_state.smart_flashcards)
            st.write("---")
            st.markdown("### 🧠 Mistake Flashcards")
            st.caption(f"{card_count} targeted revision flashcards were generated from the questions you missed.")
            st.download_button(
                label="📥 Download Mistake Flashcards (HTML)",
                data=st.session_state.flashcards_html,
                file_name="nova_mistake_flashcards.html",
                mime="text/html"
            )
        elif correct_count == total_qs_done:
            st.info("No mistake flashcards needed for this concept — you answered all 3 correctly.")

        if correct:
            if st.button("➡️ Continue to Next Concept", type="primary"):
                reset_concept_flow(clear_explanation=True)
                st.rerun()
        else:
            btn_label = "🔄 Re-try Concept (Simpler Analogy)" if evaluation["action"] == "repeat_simpler" else "🔄 Re-try Concept (Practice)"
            if st.button(btn_label, type="primary"):
                reset_concept_flow(clear_explanation=True)
                st.rerun()
