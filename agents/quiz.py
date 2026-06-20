import json
from google.adk.agents import Agent
from google.genai import Client
from google.genai import types

class QuizAgent:
    """Specialist Agent that conducts assessments.
    
    Responsibilities:
    - Generate a level-appropriate question based on the concept and tutor explanation.
    - Evaluate a student's answer.
    - Output evaluation as a JSON object with 'correct' (boolean) and 'explanation' (string).
    """

    def __init__(self):
        # Configure ADK Agent
        self.adk_agent = Agent(
            name="QuizAgent",
            model="gemini-2.5-flash",
            instruction=(
                "You are an assessment designer and grader. "
                "Your role is two-fold:\n"
                "1. Generate a single clear question (multiple-choice or short-answer) "
                "to check understanding of a concept, matching the student's level.\n"
                "2. Grade a student's answer, deciding if it is correct or incorrect, "
                "and explain why in a supportive, constructive tone."
            )
        )
        self.client = Client()

    def generate_question(self, subconcept: str, level: str, explanation: str) -> str:
        """Generates a single multiple-choice question with 4 options and returns it as a JSON string.
        
        Args:
            subconcept: The title of the concept.
            level: The student's level ('beginner' or 'intermediate').
            explanation: The exact explanation the tutor agent just generated.
        """
        from google.genai import types
        
        prompt = (
            f"Generate one multiple-choice question (MCQ) to test the student's "
            f"understanding of the concept '{subconcept}' at a {level} level.\n"
            f"Grounding context (explanation given to student):\n{explanation}\n\n"
            f"Requirements:\n"
            f"- The response must be a JSON object containing exactly 4 keys:\n"
            f"  1. 'question': the question text string.\n"
            f"  2. 'options': a list of exactly 4 choices (strings).\n"
            f"  3. 'correct_index': integer index (0, 1, 2, or 3) of the correct option.\n"
            f"  4. 'explanation': a clear, friendly explanation explaining why the correct option is correct and why other choices are incorrect.\n"
            f"- Do not write any markdown code blocks, and do not use backtick wrapping outside the JSON. Return only the raw JSON."
        )
        
        try:
            response = self.client.models.generate_content(
                model=self.adk_agent.model,
                contents=f"{self.adk_agent.instruction}\n\n{prompt}",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            return response.text.strip()
        except Exception as e:
            print(f"[QUIZ ERROR] MCQ generation failed: {e}. Using fallback.")
            # Fallback MCQ question JSON
            fallback = {
                "question": f"Which of the following best describes the core concept of {subconcept}?",
                "options": [
                    f"A foundational principle of {subconcept}",
                    f"An unrelated concept",
                    f"A random guess",
                    f"None of the above"
                ],
                "correct_index": 0,
                "explanation": f"The first option provides the most accurate and foundational definition of {subconcept}."
            }
            return json.dumps(fallback)

    def grade_answer(self, question_data: dict, student_answer: str) -> dict:
        """Grades the student's MCQ response deterministically.
        
        Args:
            question_data: The dictionary containing the question details (question, options, correct_index, explanation).
            student_answer: The student's selected option text.
        Returns:
            Dict: {'correct': bool, 'explanation': str}
        """
        try:
            options = question_data.get("options", [])
            correct_idx = question_data.get("correct_index", 0)
            correct_answer = options[correct_idx] if 0 <= correct_idx < len(options) else ""
            
            correct = (student_answer.strip() == correct_answer.strip())
            
            explanation_body = question_data.get("explanation", "No further explanation available.")
            if correct:
                feedback = f"🎉 **Correct!** Great job. You selected the right answer: **{student_answer}**.\n\n{explanation_body}"
            else:
                feedback = f"❌ **Incorrect.** You selected **{student_answer}**. The correct answer is **{correct_answer}**.\n\n{explanation_body}"
                
            return {
                "correct": correct,
                "explanation": feedback
            }
        except Exception as e:
            print(f"[QUIZ GRADING ERROR] {e}")
            return {
                "correct": False,
                "explanation": f"Error grading choice: {e}"
            }
class_symbols = [QuizAgent]
