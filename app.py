import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Custom CSS for rich premium aesthetics (glassmorphism, vibrant accents, clean cards)
st.set_page_config(page_title="StudyBuddy: Adaptive Tutor", page_icon="🎓", layout="wide")

st.markdown("""
<style>
    /* Styling elements for a premium feel */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
        font-family: 'Outfit', 'Inter', sans-serif;
    }
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #4f46e5 0%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .badge {
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-beginner {
        background-color: #d1fae5;
        color: #065f46;
    }
    .badge-intermediate {
        background-color: #eff6ff;
        color: #1e40af;
    }
    .lesson-card {
        background-color: white;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
        border-left: 5px solid #4f46e5;
        margin-bottom: 20px;
    }
    .quiz-card {
        background-color: white;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
        border-left: 5px solid #06b6d4;
        margin-bottom: 20px;
    }
    .evaluator-card {
        background-color: #f5f3ff;
        border-radius: 8px;
        padding: 16px;
        border: 1px dashed #c084fc;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Safety check for Gemini API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.warning("⚠️ GEMINI_API_KEY environment variable not found in .env.")
    api_key_input = st.text_input("Please enter your Gemini API Key to run the app:", type="password")
    if api_key_input:
        try:
            with open(".env", "w") as f:
                f.write(f"GEMINI_API_KEY={api_key_input}\n")
            os.environ["GEMINI_API_KEY"] = api_key_input
            st.success("API Key saved to .env and loaded successfully!")
        except Exception:
            os.environ["GEMINI_API_KEY"] = api_key_input
            st.success("API Key loaded successfully for this session!")
        st.rerun()
    st.info("Tip: You can copy `.env.example` to `.env` and fill in your key to avoid this prompt.")
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

def reset_session():
    st.session_state.state = None
    st.session_state.explanation = None
    st.session_state.question = None
    st.session_state.graded = None

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
st.sidebar.markdown("<h2 style='color:#4f46e5; margin-bottom: 0px;'>🎓 StudyBuddy</h2>", unsafe_allow_html=True)
st.sidebar.caption("Multi-Agent Adaptive Tutor")
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
    st.sidebar.caption(f"Session: `{state['session_id']}`")
    if st.sidebar.button("🔄 Study New Topic"):
        reset_session()
        st.rerun()

# Main Panel Design
st.markdown("<h1 class='main-title'>StudyBuddy: Adaptive Learning</h1>", unsafe_allow_html=True)

if not st.session_state.state:
    # Setup Page
    st.write("Welcome! StudyBuddy is an intelligent, multi-agent tutoring system. Simply enter a topic or upload a PDF textbook/chapter you want to learn, and we will build a tailored curriculum that adapts difficulty in real time based on your responses.")
    
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
    
    # Check if curriculum is fully completed
    if current_idx >= len(subconcepts):
        st.balloons()
        st.markdown("""
        <div style='text-align: center; padding: 40px; background-color: white; border-radius: 12px;'>
            <h2 style='color: #4f46e5;'>🎉 Course Completed!</h2>
            <p>Amazing job! You have successfully mastered all concepts for this topic.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("### 📈 Session History & Progress log:")
        st.write(state["history"])
        
        if st.button("Study another topic"):
            reset_session()
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
            st.caption("Click a card to reveal the answer!")
            for idx, card in enumerate(flashcards):
                with st.expander(f"🎴 Card {idx+1}: {card['front']}"):
                    st.markdown(f"**Answer:** {card['back']}")
        
    with col_quiz:
        st.markdown("<div class='quiz-card'>", unsafe_allow_html=True)
        st.markdown("#### 📝 Concept Check")
        
        # Quiz Agent generates quiz question (ignore string questions from older sessions)
        if not st.session_state.question or isinstance(st.session_state.question, str):
            with st.spinner("Quiz agent writing question..."):
                question_data = orchestrator.get_quiz_question(state, explanation)
                st.session_state.question = question_data
        else:
            question_data = st.session_state.question
            
        st.markdown(f"**Question:**\n{question_data.get('question', '')}")
        st.write("---")
        
        # Student response controls
        if not st.session_state.graded:
            options = question_data.get("options", [])
            selected_option = st.radio("Choose the correct option:", options, index=None, key="mcq_option_radio")
            if st.button("Submit Answer", type="primary"):
                if selected_option is None:
                    st.warning("Please select an option before submitting.")
                else:
                    with st.spinner("Quiz Agent grading and Evaluator Agent planning next step..."):
                        # Submit and evaluate (Adaptive Loop execution)
                        result = orchestrator.submit_answer(state, question_data, selected_option)
                        st.session_state.graded = result
                        st.session_state.state = result["next_state"]
                        st.rerun()
        else:
            result = st.session_state.graded
            correct = result["correct"]
            feedback = result["feedback"]
            evaluation = result["evaluation"]
            
            if correct:
                st.success("🎉 Correct!")
            else:
                st.error("❌ Incorrect")
                
            st.markdown(f"**Grader Feedback:**\n{feedback}")
            
            # Evaluator Output (demonstrates adaptive loop routing)
            st.markdown("<div class='evaluator-card'>", unsafe_allow_html=True)
            st.markdown(f"🔄 **Evaluator Decision:** Action: `{evaluation['action'].upper()}` | Next Level: `{evaluation['next_level'].upper()}`")
            st.caption(f"*Rationale: {evaluation['reasoning']}*")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Action button based on loop
            if correct:
                if st.button("➡️ Advance to Next Concept"):
                    st.session_state.explanation = None
                    st.session_state.question = None
                    st.session_state.graded = None
                    st.rerun()
            else:
                btn_label = "🔄 Re-try Concept (Simpler Analogy)" if evaluation["action"] == "repeat_simpler" else "🔄 Re-try Concept (Practice)"
                if st.button(btn_label):
                    st.session_state.explanation = None
                    st.session_state.question = None
                    st.session_state.graded = None
                    st.rerun()
                    
        st.markdown("</div>", unsafe_allow_html=True)
