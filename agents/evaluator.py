import json
from core.llm_client import generate_content_with_retry, get_model

class EvaluatorAgent:
    """Specialist Agent that handles the adaptive learning loop.
    
    Responsibilities:
    - Receive recent quiz results (current level + correctness).
    - Determine progression action: 'advance', 'repeat_simpler', or 'repeat_same'.
    - Adjust student level (beginner or intermediate).
    - Explain the educational rationale for the adjustment.
    
    Adaptive Loop Rubric:
    - If answer is correct:
      - Level is 'beginner' -> Action: 'advance', Level becomes 'intermediate' (Level Up!)
      - Level is 'intermediate' -> Action: 'advance', Level remains 'intermediate'
    - If answer is incorrect:
      - Level is 'intermediate' -> Action: 'repeat_simpler', Level drops to 'beginner' (Difficulty drops, simpler explanation next)
      - Level is 'beginner' -> Action: 'repeat_same', Level remains 'beginner' (Foundation practice)
    """

    def __init__(self):
        self.model = get_model()
        self.instruction = (
            "You are an educational evaluator in charge of an adaptive learning engine. "
            "You assess a student's performance and determine their next curriculum step and level. "
            "You must strictly follow this rubric:\n"
            "1. If correct is true:\n"
            "   - level is 'intermediate' -> action: 'advance', next_level: 'intermediate'\n"
            "   - level is 'beginner' -> action: 'advance', next_level: 'intermediate'\n"
            "2. If correct is false:\n"
            "   - level is 'intermediate' -> action: 'repeat_simpler', next_level: 'beginner'\n"
            "   - level is 'beginner' -> action: 'repeat_same', next_level: 'beginner'\n\n"
            "You must return a JSON object with three keys:\n"
            "- 'action': 'advance', 'repeat_simpler', or 'repeat_same'\n"
            "- 'next_level': 'beginner' or 'intermediate'\n"
            "- 'reasoning': string (brief summary explaining the transition to the student in a friendly way, "
            "e.g. 'Great job! You mastered this, let's step up the challenge!' or 'No worries! Let's review this concept with a simpler explanation.').\n"
            "Do not include any extra text or code block wrapping in the response."
        )

    def evaluate(self, current_level: str, correct: bool, quiz_feedback: str) -> dict:
        """Evaluates student progress and outputs the next action and level.
        
        Args:
            current_level: Student's difficulty level ('beginner' or 'intermediate').
            correct: Whether the student answered the last quiz question correctly (bool).
            quiz_feedback: Explanation text from the quiz grader.
        Returns:
            Dict: {'action': str, 'next_level': str, 'reasoning': str}
        """
        prompt = (
            f"Student's current level: '{current_level}'\n"
            f"Was the student's answer correct?: {correct}\n"
            f"Grader feedback: '{quiz_feedback}'\n"
        )
        
        try:
            response = generate_content_with_retry(
                model=self.model,
                system_instruction=self.instruction,
                user_prompt=prompt,
                temperature=0.1,
            )
            
            data = json.loads(response.text.strip())
            # Validate output keys
            return {
                "action": data.get("action", "repeat_same"),
                "next_level": data.get("next_level", "beginner"),
                "reasoning": data.get("reasoning", "Adapting learning path to support you.")
            }
            
        except Exception as e:
            print(f"[EVALUATOR ERROR] LLM evaluation failed: {e}. Falling back to deterministic rubric.")
            # Deterministic Python fallback to ensure robust execution
            if correct:
                return {
                    "action": "advance",
                    "next_level": "intermediate",
                    "reasoning": "Mastery shown! Moving on to the next topic and raising the difficulty."
                }
            else:
                action = "repeat_simpler" if current_level == "intermediate" else "repeat_same"
                return {
                    "action": action,
                    "next_level": "beginner",
                    "reasoning": "Let's review this concept again with a simpler approach to make it stick!"
                }
