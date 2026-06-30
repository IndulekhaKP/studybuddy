# NOVA — Project Reference Map (PROJECT.md)

> _This file is the single source of truth for the codebase layout, agent responsibilities, and change guide.
> Think of it like a CLAUDE.md — always read this before editing anything._

---

## 📁 Directory Structure

```
kaggleproject/
├── app.py                    # ★ MAIN FILE — Streamlit UI, CSS themes, all page logic (~1150 lines)
├── agents/
│   ├── orchestrator.py       # Coordinates all sub-agents; session flow controller
│   ├── quiz.py               # QuizAgent — generates MCQ questions & grades answers
│   ├── tutor.py              # TutorAgent — generates lesson explanations with [FLASHCARD] tags
│   ├── planner.py            # PlannerAgent — generates subconcept learning path
│   └── evaluator.py          # EvaluatorAgent — decides advance/repeat/simplify after each quiz
├── core/
│   ├── llm_client.py         # Shared Groq/OpenAI-compatible client with retry logic
│   ├── guardrails.py         # Input sanitization & topic safety check
│   ├── storage.py            # DB helpers (SQLite via studybuddy.db)
│   ├── pdf_processor.py      # extract_text_from_pdf() — PyMuPDF based
│   ├── presentation.py       # generate_html_slides() — builds downloadable HTML slideshow
│   └── developer_knowledge.py # Lightweight developer grounding notes helper
├── mcp_server/
│   └── client.py             # MCPClientHelper.call_tool() — wraps MCP tools
├── studybuddy.db             # SQLite database for session persistence
├── .env                      # GROQ_API_KEY and optional LLM_MODEL live here
├── requirements.txt          # pip dependencies
└── PROJECT.md                # ← YOU ARE HERE (like CLAUDE.md)
```

---

## 🎨 UI / CSS — app.py: Lines 1–311

### Theme System
- Two themes: `light` (default) and `dark` ("Night Eye Mode")
- Toggled via `st.session_state.theme`; CSS injected at top of app.py
- Light CSS block: lines 14–161 | Dark CSS block: lines 163–310

### CSS Classes to Edit for NOVA
| Class | Location | Purpose |
|---|---|---|
| `.main-title` | ~L29, L178 | Page header gradient text |
| `.lesson-card` | ~L67, L216 | Left lesson panel card |
| `.quiz-card` | ~L87, L236 | Right quiz panel card |
| `.evaluator-card` | ~L97, L246 | Evaluator feedback box |
| `.stButton>button` | ~L125, L274 | All primary buttons |
| `.stDownloadButton>button` | ~L141, L290 | Download buttons |
| `section[data-testid="stSidebar"]` | ~L39, L188 | Sidebar background |
| `.badge-beginner` / `.badge-intermediate` | ~L56, L205 | Level badges |

### NOVA Palette
```
Primary:    #1F2937  (charcoal)
Secondary:  #475569  (slate)
Accent:     #94A3B8  (cool gray)
Surface:    #F8FAFC  (soft white)
Border:     #E2E8F0  (light slate)
Fonts:      Playfair Display (headings) + Inter (body)
```

### Flashcard Colors (app.py lines 828–847)
- Light theme: front=white/slate, back=slate gradient
- Dark theme: front=midnight/slate, back=slate gradient
- Flashcards no longer render in the lesson stage; they appear only after quiz review if the learner missed anything.

---

## 🧠 Agent Responsibilities

### agents/orchestrator.py — StudyBuddyOrchestrator
- `start_new_session(topic, level, pdf_text)` → generates plan, saves state
- `load_session(session_id)` → loads from DB via MCP
- `get_explanation(state)` → calls TutorAgent with grounded notes
- `get_quiz_question(state, explanation)` → calls QuizAgent.generate_question()
  ★ CHANGED: now calls generate_questions_batch() returning list of 2-3 MCQs
- `submit_answer(state, question_data, answer)` → grades + evaluates + saves
  ★ CHANGED: tracks quiz_round_results; advance only if ≥2/3 correct
- `get_final_exam(state)` → QuizAgent.generate_final_exam()
- `get_presentation_slides(context)` → TutorAgent slide summary
- NEW: `generate_mistake_flashcards(state)` → FlashcardAgent call

### agents/quiz.py — QuizAgent
- `generate_question(subconcept, level, explanation)` → 1 MCQ JSON string
- NEW: `generate_questions_batch(subconcept, level, explanation, n=3)` → list of 2-3 MCQs
- `grade_answer(question_data, student_answer)` → {correct, explanation}
- `generate_final_exam(subconcepts)` → JSON list of 10 MCQs

### agents/tutor.py — TutorAgent
- `explain(subconcept, level, curriculum_notes)` → explanation with [FLASHCARD] tags
- `generate_slides_summary(context_text)` → JSON slide objects

### agents/evaluator.py — EvaluatorAgent
- `evaluate(level, correct, feedback)` → {action, next_level, reasoning}
- Actions: "advance" | "repeat_simpler" | "repeat_same"

### agents/planner.py — PlannerAgent
- `plan(topic, pdf_context)` → list of subconcept strings

### agents/flashcard_agent.py — FlashcardAgent (NEW)
- `generate_mistake_flashcards(wrong_topics, level)` → list of {front, back} dicts
- Takes topics where student answered incorrectly and generates targeted flashcards

---

## 📋 Session State Keys (app.py)
| Key | Type | Purpose |
|---|---|---|
| `theme` | str | "light" or "dark" |
| `state` | dict | Full session state (topic, subconcepts, scores, history, level, etc.) |
| `explanation` | str | Current tutor explanation text |
| `question` | dict | Current quiz question dict (legacy single) |
| `graded` | dict | Grading result after answer submit |
| `exam_questions` | list | Final exam questions list |
| `exam_graded` | list | Final exam graded results |
| `exam_score` | int | Final exam score |
| `slides_html` | str | Generated HTML slideshow |
| `flashcards_html` | str | Smart mistake flashcards HTML download (NEW) |
| `quiz_round` | list | Current batch of 2-3 MCQs (NEW) |
| `quiz_round_idx` | int | Which Q in the round we're on (0,1,2) (NEW) |
| `quiz_round_results` | list | List of bool results for current round (NEW) |
| `smart_flashcards` | list | FlashcardAgent-generated {front,back} dicts (NEW) |
| `concept_stage` | str | Current flow stage: lesson, quiz, review |
| `review_concept` | str | Concept being reviewed after quiz submission |
| `focus_mode` | str | Kairu timer state |
| `focus_started_at` | float | Unix timestamp when focus session starts |
| `focus_ends_at` | float | Unix timestamp when focus session ends |
| `focus_duration_minutes` | int | Current Kairu duration |
| `focus_label` | str | Label for the active Kairu session |
| `orchestrator` | obj | Singleton orchestrator instance |

---

## 🔄 Page Flow (app.py)

```
app.py top-to-bottom:
1. CSS injection (theme) — lines 13–310
2. API key safety check — lines 312–331
3. Import orchestrator + guardrails — lines 334–341
4. Session state initialization — lines 343–410
5. Helper functions: reset_session(), reset_concept_flow(), parse_flashcards(), focus helpers — lines 411–520
6. SIDEBAR rendering — lines 522–650
7. MAIN PANEL — lines 652+
   ├── if not state → Setup Page (topic form / PDF upload)
   └── else → Active Learning Page
       ├── Progress bar
       ├── if completed → Final Exam section with answer key review
       └── else → staged lesson/quiz/review flow
           ├── lesson stage: explanation only
           ├── quiz stage: 3-question round
           └── review stage: evaluator feedback + mistake flashcards + next concept
```

### Sidebar Modules
- `Aura Tracker`: shows completed topics out of total subconcepts plus a simple aura status
- `Kairu Focus`: 30-minute and 5-minute focus sessions with a countdown display, pause/resume controls, and a left-side sticky rail
- `Cozy Rain`: built-in study ambience player with play/pause controls in the sidebar
- Slide presentation download was removed from the sidebar
- Mistake flashcard download now appears in the review step, not the sidebar
- Lesson explanations now end with reading and YouTube search links for the current concept

---

## ✅ Planned / Completed Changes

### 1. UI Agent — NOVA Theme
- Files: `app.py`
- Replace warm accent-heavy styling with a minimal slate palette
- Rename visible branding to NOVA
- Add sidebar Aura Tracker and Kairu focus timer
- Keep the layout calm, professional, and functional
- Simplify the setup page into a more student-friendly onboarding screen
- Keep the primary buttons in a consistent light-blue / black text style in both light and dark mode
- Normalize lesson text so inline math renders as Markdown math instead of raw LaTeX
- Add topic-aware resource recommendations at the end of lesson explanations
- Add a built-in rain ambience player to the sidebar for focused study sessions

### 2. Quiz Agent — 2-3 Questions Per Topic
- Files: `agents/quiz.py`, `agents/orchestrator.py`, `app.py` (lines 943–1010)
- Add `generate_questions_batch()` to QuizAgent (returns 2-3 MCQs)
- Session state: quiz_round, quiz_round_idx, quiz_round_results
- Pass logic: ≥2/3 correct → advance; else repeat
- Final exam includes an explicit answer-key review after completion

### 3. Flashcard Agent — Smart Mistake Flashcards + Download
- Files: `agents/flashcard_agent.py` (NEW), `agents/orchestrator.py`, `app.py`
- FlashcardAgent detects wrong-answer topics and generates targeted flashcards
- HTML flip-card deck downloadable in the review step
- Trigger: after each quiz round if the learner misses any questions

---

## ⚙️ Environment
- Runtime: Python 3.x + Streamlit
- AI: Groq OpenAI-compatible API via `core/llm_client.py`
- Key env var: GROQ_API_KEY in .env
- Optional model override: LLM_MODEL in .env (default: openai/gpt-oss-20b)
- Run command: `streamlit run app.py` from /home/jaswanth/kaggleproject/
- Dependencies: see requirements.txt
