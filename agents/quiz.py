import json
from core.llm_client import generate_content_with_retry, get_model

class QuizAgent:
    """Specialist Agent that conducts assessments.
    
    Responsibilities:
    - Generate a level-appropriate question based on the concept and tutor explanation.
    - Evaluate a student's answer.
    - Output evaluation as a JSON object with 'correct' (boolean) and 'explanation' (string).
    """

    def __init__(self):
        self.model = get_model()
        self.instruction = (
            "You are an assessment designer and grader. "
            "Your role is two-fold:\n"
            "1. Generate a single clear question (multiple-choice or short-answer) "
            "to check understanding of a concept, matching the student's level.\n"
            "2. Grade a student's answer, deciding if it is correct or incorrect, "
            "and explain why in a supportive, constructive tone."
        )

    def generate_question(self, subconcept: str, level: str, explanation: str) -> str:
        """Generates a single multiple-choice question with 4 options and returns it as a JSON string.
        
        Args:
            subconcept: The title of the concept.
            level: The student's level ('beginner' or 'intermediate').
            explanation: The exact explanation the tutor agent just generated.
        """
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
            response = generate_content_with_retry(
                model=self.model,
                system_instruction=self.instruction,
                user_prompt=prompt,
                temperature=0.1,
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

    def generate_questions_batch(self, subconcept: str, level: str, explanation: str, n: int = 3) -> list:
        """Generates a batch of 2-3 MCQ questions for a subconcept.
        
        Args:
            subconcept: The title of the concept.
            level: The student's level ('beginner' or 'intermediate').
            explanation: The exact explanation the tutor agent just generated.
            n: Number of questions to generate (2 or 3).
        Returns:
            List of question dicts, each with: question, options, correct_index, explanation
        """
        prompt = (
            f"Generate exactly {n} multiple-choice questions (MCQs) to test the student's "
            f"understanding of the concept '{subconcept}' at a {level} level.\n"
            f"Grounding context (explanation given to student):\n{explanation}\n\n"
            f"Requirements:\n"
            f"- The response must be a JSON array containing exactly {n} objects.\n"
            f"- Each object must contain exactly 4 keys:\n"
            f"  1. 'question': the question text string.\n"
            f"  2. 'options': a list of exactly 4 choices (strings).\n"
            f"  3. 'correct_index': integer index (0, 1, 2, or 3) of the correct option.\n"
            f"  4. 'explanation': a clear, friendly explanation of the correct answer.\n"
            f"- Make questions distinct - test different aspects of the concept.\n"
            f"- Do not write any markdown code blocks. Return only the raw JSON array."
        )
        
        try:
            response = generate_content_with_retry(
                model=self.model,
                system_instruction=self.instruction,
                user_prompt=prompt,
                temperature=0.2,
            )
            questions = json.loads(response.text.strip())
            if isinstance(questions, list) and len(questions) >= 2:
                return questions[:n]
            raise ValueError("Invalid response format")
        except Exception as e:
            print(f"[QUIZ ERROR] Batch MCQ generation failed: {e}. Falling back to single questions.")
            fallback = []
            for i in range(n):
                single_json = self.generate_question(subconcept, level, explanation)
                try:
                    fallback.append(json.loads(single_json))
                except Exception:
                    fallback.append({
                        "question": f"Question {i+1}: Which of the following best describes '{subconcept}'?",
                        "options": [f"Core principle of {subconcept}", "Unrelated concept", "Random guess", "None of the above"],
                        "correct_index": 0,
                        "explanation": f"The first option provides the most accurate definition of {subconcept}."
                    })
            return fallback

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

    def generate_final_exam(self, subconcepts: list) -> str:
        """Generates a final exam containing exactly 10 MCQ questions covering the subconcepts.
        
        Returns:
            A JSON string containing a list of 10 question dictionaries.
        """
        prompt = (
            f"Generate a final course exam containing exactly 10 multiple-choice questions (MCQs) "
            f"covering the following subconcepts that the student has just learned:\n"
            f"{', '.join(subconcepts)}\n\n"
            f"Requirements:\n"
            f"- Return a valid JSON array of exactly 10 objects.\n"
            f"- Each object in the array must contain exactly 4 keys:\n"
            f"  1. 'question': the question text string.\n"
            f"  2. 'options': a list of exactly 4 choices (strings).\n"
            f"  3. 'correct_index': integer index (0, 1, 2, or 3) of the correct option.\n"
            f"  4. 'explanation': a clear educational explanation of the correct choice.\n"
            f"- Output ONLY the raw JSON array. Do not wrap it in markdown code blocks."
        )
        
        try:
            response = generate_content_with_retry(
                model=self.model,
                system_instruction=self.instruction,
                user_prompt=prompt,
                temperature=0.2,
            )
            return response.text.strip()
        except Exception as e:
            print(f"[QUIZ ERROR] Final exam generation failed: {e}. Using fallback.")
            import json
            fallback_questions = []
            for i, concept in enumerate(subconcepts * 4):
                if len(fallback_questions) >= 10:
                    break
                fallback_questions.append({
                    "question": f"Which of the following best describes the key concept of '{concept}'?",
                    "options": [
                        f"A core principle of {concept}",
                        f"An unrelated detail",
                        f"A generic false choice",
                        f"None of the above"
                    ],
                    "correct_index": 0,
                    "explanation": f"The first option provides the most accurate and foundational definition of {concept}."
                })
            return json.dumps(fallback_questions)

class_symbols = [QuizAgent]
