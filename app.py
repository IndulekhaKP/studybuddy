import os
import streamlit as st
from dotenv import load_dotenv
from core.llm_client import DEFAULT_MODEL, TASK_MODEL_DEFAULTS

# Load environment variables from .env
load_dotenv()

# Initialize theme state
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# Inject theme CSS dynamically based on light/dark mode selection
if st.session_state.theme == "light":
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600&family=Inter:wght@300;400;500;600;700&display=swap');
        
        .stApp {
            background: linear-gradient(135deg, #FDF6EE 0%, #F5E6D0 100%);
            font-family: 'Inter', sans-serif;
            color: #2C1A0E;
        }
        
        /* Overrides for Light Mode */
        .stApp p, .stApp span, .stApp label, .stApp li {
            color: #4A2E18 !important;
        }
        
        .main-title {
            font-size: 3.2rem;
            font-weight: 800;
            background: linear-gradient(90deg, #FF6F20 0%, #F2C94C 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            font-family: 'Playfair Display', serif;
        }
        
        section[data-testid="stSidebar"] {
            background-color: #FDF0E0 !important;
            border-right: 1px solid #D9B68C !important;
        }
        section[data-testid="stSidebar"] .stMarkdown p {
            color: #A65E2E !important;
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
            background-color: #FFF3E0 !important;
            color: #A65E2E !important;
            border: 1px solid #FF6F20 !important;
        }
        .badge-intermediate {
            background-color: #FFF8E1 !important;
            color: #8B5000 !important;
            border: 1px solid #F2C94C !important;
        }
        
        .lesson-card {
            background: #FFFFFF;
            border: 1px solid #D9B68C;
            border-left: 5px solid #FF6F20;
            border-radius: 16px;
            padding: 26px;
            margin-bottom: 24px;
            box-shadow: 0 4px 20px -2px rgba(198, 93, 59, 0.1);
        }
        .lesson-card h4, .lesson-card h1, .lesson-card h2, .lesson-card h3 {
            font-family: 'Playfair Display', serif;
            color: #2C1A0E !important;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .lesson-card p, .lesson-card li, .lesson-card div {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 1.05rem;
            line-height: 1.65;
            color: #2C1A0E !important;
        }
        
        .quiz-card {
            background: #FFFFFF;
            border: 1px solid #D9B68C;
            border-left: 5px solid #C65D3B;
            border-radius: 16px;
            padding: 26px;
            margin-bottom: 24px;
            box-shadow: 0 4px 20px -2px rgba(198, 93, 59, 0.1);
        }
        
        .evaluator-card {
            background: #FFF8F0;
            border: 1px dashed #F2C94C;
            border-radius: 12px;
            padding: 18px;
            margin-top: 15px;
        }
        
        .stTextInput>div>div>input {
            background-color: #FFFBF7 !important;
            color: #2C1A0E !important;
            border: 1px solid #D9B68C !important;
            border-radius: 10px !important;
        }
        .stSelectbox>div>div>div {
            background-color: #FFFBF7 !important;
            color: #2C1A0E !important;
            border: 1px solid #D9B68C !important;
            border-radius: 10px !important;
        }
        .stForm {
            background: #FFFFFF !important;
            border: 1px solid #D9B68C !important;
            border-radius: 16px !important;
            padding: 24px !important;
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05);
        }
        
        .stButton>button {
            background: linear-gradient(90deg, #FF6F20 0%, #C65D3B 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 9999px !important;
            padding: 10px 24px !important;
            font-weight: 700 !important;
            font-family: 'Inter', sans-serif !important;
            text-transform: uppercase !important;
            letter-spacing: 0.06em !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 14px rgba(255, 111, 32, 0.3) !important;
        }
        .stButton>button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(255, 111, 32, 0.45) !important;
        }
        
        .stDownloadButton>button {
            background: linear-gradient(90deg, #F2C94C 0%, #A65E2E 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 9999px !important;
            padding: 10px 24px !important;
            font-weight: 600 !important;
            font-family: 'Inter', sans-serif !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 14px rgba(242, 201, 76, 0.3) !important;
        }
        .stDownloadButton>button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(242, 201, 76, 0.45) !important;
        }
        
        div[data-testid="stMarkdownContainer"] p {
            color: #4A2E18 !important;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600&family=Inter:wght@300;400;500;600;700&display=swap');
        
        .stApp {
            background: linear-gradient(135deg, #1A0F07 0%, #2C1810 100%);
            font-family: 'Inter', sans-serif;
            color: #F5E6D0;
        }
        
        /* Overrides for Night Eye Mode */
        .stApp p, .stApp span, .stApp label, .stApp li {
            color: #D9B68C !important;
        }
        
        .main-title {
            font-size: 3.2rem;
            font-weight: 800;
            background: linear-gradient(90deg, #FF6F20 0%, #F2C94C 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            font-family: 'Playfair Display', serif;
        }
        
        section[data-testid="stSidebar"] {
            background-color: #150A04 !important;
            border-right: 1px solid #3D2010 !important;
        }
        section[data-testid="stSidebar"] .stMarkdown p {
            color: #D9B68C !important;
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
            background-color: rgba(255,111,32,0.12) !important;
            color: #FF8C42 !important;
            border: 1px solid rgba(255,111,32,0.3) !important;
        }
        .badge-intermediate {
            background-color: rgba(242,201,76,0.12) !important;
            color: #F2C94C !important;
            border: 1px solid rgba(242,201,76,0.3) !important;
        }
        
        .lesson-card {
            background: #2C1810;
            border: 1px solid #3D2010;
            border-left: 5px solid #FF6F20;
            border-radius: 16px;
            padding: 26px;
            margin-bottom: 24px;
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.3);
        }
        .lesson-card h4, .lesson-card h1, .lesson-card h2, .lesson-card h3 {
            font-family: 'Playfair Display', serif;
            color: #F5E6D0 !important;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .lesson-card p, .lesson-card li, .lesson-card div {
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 1.05rem;
            line-height: 1.65;
            color: #D9B68C !important;
        }
        
        .quiz-card {
            background: #2C1810;
            border: 1px solid #3D2010;
            border-left: 5px solid #C65D3B;
            border-radius: 16px;
            padding: 26px;
            margin-bottom: 24px;
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.3);
        }
        
        .evaluator-card {
            background: rgba(255,111,32,0.08);
            border: 1px dashed rgba(242,201,76,0.4);
            border-radius: 12px;
            padding: 18px;
            margin-top: 15px;
        }
        
        .stTextInput>div>div>input {
            background-color: #150A04 !important;
            color: #F5E6D0 !important;
            border: 1px solid #3D2010 !important;
            border-radius: 10px !important;
        }
        .stSelectbox>div>div>div {
            background-color: #150A04 !important;
            color: #F5E6D0 !important;
            border: 1px solid #3D2010 !important;
            border-radius: 10px !important;
        }
        .stForm {
            background: #2C1810 !important;
            border: 1px solid #3D2010 !important;
            border-radius: 16px !important;
            padding: 24px !important;
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.3);
        }
        
        .stButton>button {
            background: linear-gradient(90deg, #FF6F20 0%, #C65D3B 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 9999px !important;
            padding: 10px 24px !important;
            font-weight: 700 !important;
            font-family: 'Inter', sans-serif !important;
            text-transform: uppercase !important;
            letter-spacing: 0.06em !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 14px rgba(255,111,32,0.35) !important;
        }
        .stButton>button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(255,111,32,0.5) !important;
        }
        
        .stDownloadButton>button {
            background: linear-gradient(90deg, #F2C94C 0%, #A65E2E 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 9999px !important;
            padding: 10px 24px !important;
            font-weight: 600 !important;
            font-family: 'Inter', sans-serif !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 14px rgba(242,201,76,0.35) !important;
        }
        .stDownloadButton>button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(242,201,76,0.5) !important;
        }
        
        div[data-testid="stMarkdownContainer"] p {
            color: #D9B68C !important;
        }
    </style>
    """, unsafe_allow_html=True)

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

def parse_flashcards(text: str):
    """Extracts flashcards from tutor's output based on [FLASHCARD] tags."""
    import re
    if not text:
        return "", []
        
    parts = re.split(r'\[FLASHCARD\]', text)
    clean_explanation = parts[0].strip()
    
    flashcards = []
    for part in parts[1:]:
        part_str = part.strip()
        if not part_str:
            continue
        lines = part_str.split("\n")
        front = ""
        back = ""
        for line in lines:
            if line.strip().lower().startswith("front:"):
                front = line.strip()[6:].strip()
            elif line.strip().lower().startswith("back:"):
                back = line.strip()[5:].strip()
        if front and back:
            flashcards.append({"front": front, "back": back})
            
    # Clean up any leftover tags or formatting
    clean_explanation = clean_explanation.replace("[FLASHCARD]", "").strip()
    return clean_explanation, flashcards

# Sidebar Design
st.sidebar.markdown("<h2 style='margin-top: 5px; margin-bottom: 0px;'>🎓 StudyBuddy</h2>", unsafe_allow_html=True)
st.sidebar.caption("Multi-Agent Adaptive Tutor")
st.sidebar.write("---")

# Theme selector button (Night Eye / Light Mode)
theme_btn_label = "👁️ Night Eye Mode" if st.session_state.theme == "light" else "☀️ Light Mode"
if st.sidebar.button(theme_btn_label, key="theme_toggle_btn"):
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
    st.rerun()
st.sidebar.write("---")

if st.session_state.state:
    state = st.session_state.state
    
    # Visualizing current difficulty level
    level = state["level"]
    level_class = "badge-beginner" if level == "beginner" else "badge-intermediate"
    st.sidebar.markdown(f"**Current Level:** <span class='badge {level_class}'>{level.upper()}</span>", unsafe_allow_html=True)
    st.sidebar.write(f"**Topic:** {state['topic']}")
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
    
    # Add Slides presentation generator download
    st.sidebar.markdown("### 🖥️ Slide Presentation")
    if not st.session_state.slides_html:
        if st.sidebar.button("⚙️ Generate Slides Summary"):
            with st.spinner("Generating slide deck summary..."):
                slide_context = state.get("pdf_text") or f"Topic: {state['topic']}\nCurriculum Path: {', '.join(state['subconcepts'])}"
                slides_data = orchestrator.get_presentation_slides(slide_context)
                from core.presentation import generate_html_slides
                st.session_state.slides_html = generate_html_slides(slides_data)
                st.rerun()
    else:
        st.sidebar.download_button(
            label="📥 Download HTML Slideshow",
            data=st.session_state.slides_html,
            file_name="lesson_presentation.html",
            mime="text/html"
        )
        st.sidebar.write("---")
            
    # Smart Mistake Flashcards
    st.sidebar.markdown("### \U0001f9e0 Smart Flashcards")
    if not st.session_state.get("flashcards_html"):
        if st.sidebar.button("\u26a1 Generate Mistake Flashcards"):
            with st.spinner("FlashcardAgent analyzing weak topics..."):
                smart_cards = orchestrator.generate_mistake_flashcards(state)
                if smart_cards:
                    fc_html = orchestrator.flashcard_agent.build_html_flashcard_deck(
                        smart_cards, title="Smart Revision Flashcards"
                    )
                    st.session_state.flashcards_html = fc_html
                    st.session_state.smart_flashcards = smart_cards
                    st.rerun()
                else:
                    st.sidebar.info("No weak topics detected yet - keep studying!")
    else:
        card_count = len(st.session_state.get("smart_flashcards", []))
        st.sidebar.caption(f"\u2705 {card_count} targeted flashcards ready")
        st.sidebar.download_button(
            label="\U0001f4e5 Download Flashcard Deck (HTML)",
            data=st.session_state.flashcards_html,
            file_name="studybuddy_smart_flashcards.html",
            mime="text/html"
        )
        if st.sidebar.button("\U0001f504 Regenerate Flashcards"):
            st.session_state.flashcards_html = None
            st.session_state.smart_flashcards = []
            st.rerun()
    st.sidebar.write("---")

    # Add Download Study Notes button
    notes_markdown = f"# StudyBuddy Study Notes: {state['topic']}\n\n"
    if state.get("history"):
        for log in state["history"]:
            notes_markdown += f"## Concept: {log['subconcept']}\n"
            notes_markdown += f"- **Difficulty Level**: {log['level'].upper()}\n"
            notes_markdown += f"- **Result Check**: {'PASSED' if log['correct'] else 'FAILED'}\n"
            notes_markdown += f"- **Grader Feedback**: {log['reasoning']}\n\n"
            
    st.sidebar.download_button(
        label="📝 Download Study Notes (MD)",
        data=notes_markdown,
        file_name=f"{state['topic'].replace(' ', '_')}_study_notes.md",
        mime="text/markdown"
    )
    st.sidebar.write("---")

    st.sidebar.caption(f"Session: `{state['session_id']}`")
    if st.sidebar.button("🔄 Study New Topic"):
        reset_session()
        st.rerun()

# Main Panel Design
st.markdown("<h1 class='main-title' style='margin-top: 5px;'>🎓 StudyBuddy: Adaptive Learning</h1>", unsafe_allow_html=True)

if not st.session_state.state:
    # Setup Page
    st.write("Welcome to StudyBuddy — your intelligent Autumn-powered tutor. Enter a topic or upload a PDF textbook chapter below, and our AI agents will craft a personalized learning path that adapts to your pace in real time.")
    
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
            
        st.markdown("### 💡 Try these seeded topics for instant curriculum lookup:")
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
    
    # Course Progress dashboard
    col_prog_bar, col_prog_txt = st.columns([0.85, 0.15])
    with col_prog_bar:
        st.progress(progress_percentage)
    with col_prog_txt:
        st.markdown(f"**{int(progress_percentage * 100)}%** ({completed_count}/{total_count})")
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
        <div class="title">StudyBuddy</div>
        <div class="subtitle">Certificate of Completion</div>
        <div class="presented-to">This is proudly presented to the scholar who mastered</div>
        <div class="student-name">StudyBuddy Graduate</div>
        <div class="course-name">Course Topic: <strong>{state['topic']}</strong></div>
        <div class="badge">Final Score: {score}/10 (Passed)</div>
        <div class="date-signature">
            <div class="item">Date Issued</div>
            <div class="item">StudyBuddy Adaptive Agent</div>
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
        
    current_concept = subconcepts[current_idx]
    
    st.write(f"### Current Concept: **{current_concept}**")
    
    # Create side-by-side layout for lesson (Tutor) and quiz (Quiz)
    col_lesson, col_quiz = st.columns([1.1, 0.9], gap="large")
    
    with col_lesson:
        st.markdown("<div class='lesson-card'>", unsafe_allow_html=True)
        st.markdown("#### 📖 Lesson Explanation")
        
        # Tutor Agent generates lesson
        if not st.session_state.explanation:
            with st.spinner("Tutor agent preparing explanation..."):
                explanation = orchestrator.get_explanation(state)
                st.session_state.explanation = explanation
        else:
            explanation = st.session_state.explanation
            
        clean_exp, flashcards = parse_flashcards(explanation)
        st.markdown(clean_exp)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Display Flashcards if available
        if flashcards:
            st.write("---")
            st.markdown("### 🎴 Study Flashcards")
            st.caption("Click a card to flip it and reveal the answer!")
            
            # Dynamic card colors based on selected theme
            if st.session_state.theme == "light":
                front_bg = "linear-gradient(135deg, #FFFBF7 0%, #FDF0E0 100%)"
                front_color = "#2C1A0E"
                front_border = "1px solid #D9B68C"
                back_bg = "linear-gradient(135deg, #FF6F20 0%, #C65D3B 100%)"
                back_color = "#FFFFFF"
                back_border = "1px solid rgba(255, 111, 32, 0.2)"
                title_color_front = "#A65E2E"
                title_color_back = "#FFE0CC"
                shadow = "rgba(198, 93, 59, 0.15)"
            else:
                front_bg = "linear-gradient(135deg, #2C1810 0%, #1A0F07 100%)"
                front_color = "#F5E6D0"
                front_border = "1px solid rgba(217, 182, 140, 0.15)"
                back_bg = "linear-gradient(135deg, #FF6F20 0%, #A65E2E 100%)"
                back_color = "#FFFFFF"
                back_border = "1px solid rgba(255, 111, 32, 0.25)"
                title_color_front = "#D9B68C"
                title_color_back = "#FFE0CC"
                shadow = "rgba(0, 0, 0, 0.45)"

            cards_html = f"""
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
                .card-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                    gap: 12px;
                    padding: 5px;
                    font-family: 'Inter', sans-serif;
                }}
                .flip-card {{
                    background-color: transparent;
                    width: 100%;
                    height: 140px;
                    perspective: 1000px;
                    cursor: pointer;
                }}
                .flip-card-inner {{
                    position: relative;
                    width: 100%;
                    height: 100%;
                    text-align: center;
                    transition: transform 0.6s;
                    transform-style: preserve-3d;
                    box-shadow: 0 4px 12px {shadow};
                    border-radius: 12px;
                }}
                .flip-card.flipped .flip-card-inner {{
                    transform: rotateY(180deg);
                }}
                .flip-card-front, .flip-card-back {{
                    position: absolute;
                    width: 100%;
                    height: 100%;
                    -webkit-backface-visibility: hidden;
                    backface-visibility: hidden;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    padding: 12px;
                    border-radius: 12px;
                    box-sizing: border-box;
                }}
                .flip-card-front {{
                    background: {front_bg};
                    color: {front_color};
                    border: {front_border};
                }}
                .flip-card-back {{
                    background: {back_bg};
                    color: {back_color};
                    border: {back_border};
                }}
                .title-label {{
                    font-size: 0.7rem;
                    text-transform: uppercase;
                    letter-spacing: 0.08em;
                    color: {title_color_front};
                    margin-bottom: 6px;
                    font-weight: 600;
                }}
                .card-text {{
                    font-size: 0.85rem;
                    font-weight: 500;
                    line-height: 1.3;
                }}
                .flip-card-back .title-label {{
                    color: {title_color_back};
                }}
            </style>
            <div class="card-grid">
            """
            for idx, card in enumerate(flashcards):
                front_esc = card['front'].replace("'", "&#39;").replace('"', "&quot;")
                back_esc = card['back'].replace("'", "&#39;").replace('"', "&quot;")
                cards_html += f"""
                <div class="flip-card" onclick="this.classList.toggle('flipped')">
                    <div class="flip-card-inner">
                        <div class="flip-card-front">
                            <div class="title-label">Card {idx+1} (Front)</div>
                            <div class="card-text">{front_esc}</div>
                        </div>
                        <div class="flip-card-back">
                            <div class="title-label">Answer (Back)</div>
                            <div class="card-text">{back_esc}</div>
                        </div>
                    </div>
                </div>
                """
            cards_html += "</div>"
            import streamlit.components.v1 as components
            components.html(cards_html, height=170)
        
    with col_quiz:
        st.markdown("<div class='quiz-card'>", unsafe_allow_html=True)
        st.markdown("#### 📝 Concept Check (2–3 Questions)")
        
        # Load or generate the quiz round (batch of 3 questions)
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
                label=question_data.get('question', ''),
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
                        passed = correct_count >= 2  # >=2/3 to pass
                        
                        combined_feedback = f"**Round Complete:** {correct_count}/{total_qs} correct.\n\n"
                        for i, r in enumerate(round_results):
                            status = "✅" if r["correct"] else "❌"
                            combined_feedback += f"{status} **Q{i+1}:** {r['feedback']}\n\n"
                        
                        evaluation = orchestrator.evaluator.evaluate(
                            state["level"], passed, combined_feedback
                        )
                        
                        current_subconcept = state["subconcepts"][state["current_index"]]
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
                    st.rerun()
        
        elif st.session_state.graded:
            result = st.session_state.graded
            correct = result["correct"]
            feedback = result["feedback"]
            evaluation = result["evaluation"]
            round_results = st.session_state.get("quiz_round_results", [])
            correct_count = sum(1 for r in round_results if r["correct"])
            total_qs_done = len(round_results)
            
            if correct:
                st.success(f"🎉 **Passed!** {correct_count}/{total_qs_done} correct — great work!")
            else:
                st.error(f"❌ **Not yet.** {correct_count}/{total_qs_done} correct — need ≥2 to advance.")
            
            with st.expander("📋 See detailed feedback"):
                st.markdown(feedback)
            
            st.markdown("<div class='evaluator-card'>", unsafe_allow_html=True)
            st.markdown(f"🔄 **Evaluator Decision:** Action: `{evaluation['action'].upper()}` | Next Level: `{evaluation['next_level'].upper()}`")
            st.caption(f"*Rationale: {evaluation['reasoning']}*")
            st.markdown("</div>", unsafe_allow_html=True)
            
            if correct:
                if st.button("➡️ Advance to Next Concept"):
                    st.session_state.explanation = None
                    st.session_state.question = None
                    st.session_state.graded = None
                    st.session_state.quiz_round = None
                    st.session_state.quiz_round_idx = 0
                    st.session_state.quiz_round_results = []
                    st.rerun()
            else:
                btn_label = "🔄 Re-try Concept (Simpler Analogy)" if evaluation["action"] == "repeat_simpler" else "🔄 Re-try Concept (Practice)"
                if st.button(btn_label):
                    st.session_state.explanation = None
                    st.session_state.question = None
                    st.session_state.graded = None
                    st.session_state.quiz_round = None
                    st.session_state.quiz_round_idx = 0
                    st.session_state.quiz_round_results = []
                    st.rerun()
                    
        st.markdown("</div>", unsafe_allow_html=True)
