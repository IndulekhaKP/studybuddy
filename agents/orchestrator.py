import json
import uuid
from agents.planner import PlannerAgent
from agents.tutor import TutorAgent
from agents.quiz import QuizAgent
from agents.evaluator import EvaluatorAgent
from mcp_server.client import MCPClientHelper

class StudyBuddyOrchestrator:
    """Orchestrator Agent that manages the learning workflow.
    
    Responsibilities:
    - Coordinates between sub-agents: Planner, Tutor, Quiz, and Evaluator.
    - Saves and loads progress via the MCP server tools.
    - Resolves curriculum grounding content via MCP tools.
    - Drives the loop: Path Planning -> Explanation -> Quiz -> Evaluation -> Adaptive Step.
    """

    def __init__(self):
        # Instantiate sub-agents
        self.planner = PlannerAgent()
        self.tutor = TutorAgent()
        self.quiz = QuizAgent()
        self.evaluator = EvaluatorAgent()

    def start_new_session(self, topic: str, initial_level: str = "intermediate", pdf_text: str = None) -> dict:
        """Initializes a new session, generates the subconcept list, and saves state to DB.
        
        Args:
            topic: The educational topic chosen by the student.
            initial_level: Student's starting difficulty level ('beginner' or 'intermediate').
            pdf_text: Optional text extracted from an uploaded PDF.
        """
        # Generate random anonymous session ID to store progress without PII
        session_id = f"sb_{uuid.uuid4().hex[:10]}"
        
        # 1. Planner generates the learning path (pass PDF context if available)
        subconcepts = self.planner.plan(topic, pdf_context=pdf_text)
        
        # 2. Construct initial progress state
        state = {
            "session_id": session_id,
            "topic": topic,
            "subconcepts": subconcepts,
            "current_index": 0,
            "level": initial_level,
            "scores": {},       # Format: {subconcept: [bool]}
            "history": [],      # List of evaluation logs
            "completed": [],    # Subconcepts completed successfully
            "pdf_text": pdf_text # Store extracted PDF text for grounding
        }
        
        # 3. Save progress using the MCP server tool
        MCPClientHelper.call_tool("save_progress", {
            "session_id": session_id,
            "state_json": json.dumps(state)
        })
        
        return state

    def load_session(self, session_id: str) -> dict:
        """Retrieves an existing progress state using the MCP load_progress tool."""
        res_json = MCPClientHelper.call_tool("load_progress", {"session_id": session_id})
        try:
            return json.loads(res_json)
        except Exception as e:
            print(f"Error loading session: {e}")
            return {}

    def save_session(self, state: dict) -> None:
        """Saves current state using the MCP save_progress tool."""
        MCPClientHelper.call_tool("save_progress", {
            "session_id": state["session_id"],
            "state_json": json.dumps(state)
        })

    def get_explanation(self, state: dict) -> str:
        """Fetches grounded notes (from PDF or MCP server) and gets a Tutor explanation.
        
        Args:
            state: The current session state dictionary.
        """
        topic = state["topic"]
        subconcepts = state["subconcepts"]
        idx = state["current_index"]
        
        if idx >= len(subconcepts):
            return "Curriculum completed! You have finished all lessons."
            
        current_subconcept = subconcepts[idx]
        level = state["level"]
        pdf_text = state.get("pdf_text")
        
        if pdf_text:
            # Dynamic Grounding: Extract only the document sections relevant to the current subconcept
            try:
                from google.genai import Client
                client = Client()
                prompt = (
                    f"Read the following document text and extract the exact sentences, paragraphs, "
                    f"or facts that explain the sub-concept: '{current_subconcept}'. "
                    f"Provide only the relevant factual text as-is. Do not write summaries or explanations yourself.\n\n"
                    f"Document Text:\n{pdf_text}"
                )
                from core.gemini_client import generate_content_with_retry
                response = generate_content_with_retry(
                    client=client,
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                curriculum_notes = response.text.strip()
            except Exception as e:
                print(f"[ORCHESTRATOR ERROR] PDF text extraction failed: {e}")
                curriculum_notes = f"Grounding notes from PDF (Error extracting details: {e})"
        else:
            # Check if this is a developer/tech topic
            dev_keywords = ["google cloud", "gcp", "firebase", "android", "flutter", "bigquery", "cloud run", 
                            "kubernetes", "golang", "python", "programming", "javascript", "react", "html", 
                            "css", "sql", "sqlite", "github", "git", "api", "database", "node.js"]
            is_dev_topic = any(kw in topic.lower() for kw in dev_keywords) or any(kw in current_subconcept.lower() for kw in dev_keywords)
            
            curriculum_notes = None
            if is_dev_topic:
                try:
                    from core.developer_knowledge import query_developer_docs
                    curriculum_notes = query_developer_docs(f"{topic} {current_subconcept}")
                    if curriculum_notes:
                        print(f"[ORCHESTRATOR] Developer Knowledge API successfully grounded topic '{topic}'")
                except Exception as ex:
                    print(f"[ORCHESTRATOR WARNING] Developer Knowledge import or call failed: {ex}")
            
            if not curriculum_notes:
                # Default: Call MCP Tool to retrieve grounding facts from curriculum database
                curriculum_notes = MCPClientHelper.call_tool("get_curriculum_content", {
                    "topic": topic,
                    "subconcept": current_subconcept
                })
                # Fallback: If the topic is not found in the local knowledge base, use Google Search
                if "error" in curriculum_notes:
                    curriculum_notes = "USE_GOOGLE_SEARCH"
        
        # Tutor Agent generates explanation based on level and grounding
        explanation = self.tutor.explain(current_subconcept, level, curriculum_notes)
        return explanation

    def get_quiz_question(self, state: dict, explanation: str) -> dict:
        """Asks the Quiz Agent to generate a question for the current subconcept.
        
        Args:
            state: The current session state dictionary.
            explanation: The text explanation just provided by the Tutor.
        Returns:
            Dict containing MCQ question details.
        """
        subconcepts = state["subconcepts"]
        idx = state["current_index"]
        current_subconcept = subconcepts[idx]
        level = state["level"]
        
        # Quiz Agent generates question
        question_json = self.quiz.generate_question(current_subconcept, level, explanation)
        try:
            return json.loads(question_json)
        except Exception as e:
            print(f"[ORCHESTRATOR ERROR] Failed to parse question JSON: {e}")
            return {
                "question": f"Which of the following is correct about {current_subconcept}?",
                "options": [
                    "Option A (Correct)",
                    "Option B",
                    "Option C",
                    "Option D"
                ],
                "correct_index": 0,
                "explanation": "Option A is the correct answer."
            }

    def submit_answer(self, state: dict, question_data: dict, student_answer: str) -> dict:
        """Grades student answer, evaluates level adaptation, updates state, and persists to DB.
        
        Args:
            state: The current session state dictionary.
            question_data: The MCQ question data dictionary.
            student_answer: The student's selected option text.
        Returns:
            Dict: {
                'correct': bool,
                'feedback': str,
                'evaluation': dict,
                'next_state': dict
            }
        """
        subconcepts = state["subconcepts"]
        idx = state["current_index"]
        current_subconcept = subconcepts[idx]
        level = state["level"]
        
        # 1. Quiz Agent grades the student's response
        grading = self.quiz.grade_answer(question_data, student_answer)
        correct = grading["correct"]
        feedback = grading["explanation"]
        
        # 2. Evaluator Agent determines the next step and level adjustment (Adaptive Loop)
        evaluation = self.evaluator.evaluate(level, correct, feedback)
        action = evaluation["action"]
        next_level = evaluation["next_level"]
        
        # Record response history in the session scores dict
        if current_subconcept not in state["scores"]:
            state["scores"][current_subconcept] = []
        state["scores"][current_subconcept].append(correct)
        
        # Log evaluation log
        state["history"].append({
            "subconcept": current_subconcept,
            "level": level,
            "correct": correct,
            "action": action,
            "next_level": next_level,
            "reasoning": evaluation.get("reasoning", "")
        })
        
        # Apply transition action
        if action == "advance":
            if current_subconcept not in state["completed"]:
                state["completed"].append(current_subconcept)
            state["current_index"] += 1
        elif action == "repeat_simpler":
            # Keep index the same, level drops to beginner
            pass
        elif action == "repeat_same":
            # Keep index and level the same
            pass
            
        state["level"] = next_level
        
        # 3. Save progress via the MCP save_progress tool
        self.save_session(state)
        
        return {
            "correct": correct,
            "feedback": feedback,
            "evaluation": evaluation,
            "next_state": state
        }

    def get_final_exam(self, state: dict) -> list[dict]:
        """Generates a final course exam covering all subconcepts in the session."""
        subconcepts = state["subconcepts"]
        exam_json = self.quiz.generate_final_exam(subconcepts)
        try:
            return json.loads(exam_json)
        except Exception as e:
            print(f"[ORCHESTRATOR ERROR] Failed to parse final exam JSON: {e}")
            return [{
                "question": "What is the primary key to mastering the topic you just studied?",
                "options": [
                    "Reviewing and practicing consistently",
                    "Skipping the quiz check-ins",
                    "Relying on guessing",
                    "Avoiding explanations"
                ],
                "correct_index": 0,
                "explanation": "Consistent practice and active study are scientifically proven to be the most effective methods to master any academic topic."
            }]

    def get_presentation_slides(self, pdf_text: str) -> list[dict]:
        """Generates slide summaries from the uploaded PDF context."""
        slides_json = self.tutor.generate_slides_summary(pdf_text)
        try:
            return json.loads(slides_json)
        except Exception as e:
            print(f"[ORCHESTRATOR ERROR] Failed to parse slides JSON: {e}")
            return [
                {"title": "Lesson Presentation Overview", "points": ["Overview of primary concepts", "Key terms and definitions"]}
            ]
