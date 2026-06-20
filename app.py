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
if "exam_questions" not in st.session_state:
    st.session_state.exam_questions = None
if "exam_graded" not in st.session_state:
    st.session_state.exam_graded = None
if "exam_score" not in st.session_state:
    st.session_state.exam_score = None
if "slides_html" not in st.session_state:
    st.session_state.slides_html = None

def reset_session():
    st.session_state.state = None
    st.session_state.explanation = None
    st.session_state.question = None
    st.session_state.graded = None
    st.session_state.exam_questions = None
    st.session_state.exam_graded = None
    st.session_state.exam_score = None
    st.session_state.slides_html = None

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
import os
col_side_logo, col_side_text = st.sidebar.columns([0.25, 0.75])
with col_side_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=45)
with col_side_text:
    st.sidebar.markdown("<h2 style='color:#4f46e5; margin-top: 5px; margin-bottom: 0px;'>StudyBuddy</h2>", unsafe_allow_html=True)
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
    
    # Add Slides presentation generator download
    if state.get("pdf_text"):
        st.sidebar.markdown("### 🖥️ Slide Presentation")
        if not st.session_state.slides_html:
            if st.sidebar.button("⚙️ Generate Slides Summary"):
                with st.spinner("Generating slide deck summary..."):
                    slides_data = orchestrator.get_presentation_slides(state["pdf_text"])
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
col_title_logo, col_title_text = st.columns([0.1, 0.9])
with col_title_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=75)
with col_title_text:
    st.markdown("<h1 class='main-title' style='margin-top: 5px;'>StudyBuddy: Adaptive Learning</h1>", unsafe_allow_html=True)

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
        <div style='text-align: center; padding: 25px; background-color: white; border-radius: 12px; border-left: 5px solid #4f46e5; margin-bottom: 20px;'>
            <h2 style='color: #4f46e5; margin: 0;'>🎉 Curriculum Lessons Completed!</h2>
            <p style='color: #4b5563; margin-top: 5px; margin-bottom: 0;'>Amazing job! You have successfully mastered all lessons. Now, complete the Final Course Exam to receive your Certificate.</p>
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
                        st.markdown(f"**Question {q_idx+1}:** {q['question']}")
                        sel = st.radio(
                            f"Choose option for Question {q_idx+1}:", 
                            q['options'], 
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
