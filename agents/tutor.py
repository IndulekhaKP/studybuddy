from core.llm_client import generate_content_with_retry, get_model

class TutorAgent:
    """Specialist Agent that explains academic concepts.
    
    Responsibilities:
    - Teach the student concept-by-concept.
    - Ground explanations using reference curriculum notes (from the MCP server) to prevent hallucination.
    - Use an intuitive analogy and a worked-out example.
    - Adapt explanation depth and language depending on the student's level (beginner / intermediate).
    """

    def __init__(self):
        self.model = get_model()
        self.instruction = (
            "You are an adaptive, encouraging, and clear academic tutor. "
            "Your goal is to explain a specific sub-concept to a student based on their learning level "
            "(beginner or intermediate) and reference curriculum notes provided for grounding. "
            "You must strictly follow these structural requirements:\n"
            "1. Keep the explanation short, clean, and easy to read.\n"
            "2. Start with a vivid, relatable analogy (e.g. comparing computer memory to a post office).\n"
            "3. Provide exactly one concrete worked-out example to reinforce the concept.\n"
            "4. Tailor your tone: use simple words and intuitive explanations for 'beginner'; "
            "use slightly more detailed, professional terminology and algebraic/formal examples for 'intermediate'.\n"
            "5. At the very end of your response, add exactly 3 flashcards for study/review. Use this exact formatting for each card:\n"
            "[FLASHCARD]\n"
            "Front: [Key question or term]\n"
            "Back: [Brief definition or answer]\n"
            "[FLASHCARD]"
        )

    def explain(self, subconcept: str, level: str, curriculum_notes: str) -> str:
        """Generates an explanation for the subconcept tailored to the student level.
        
        Args:
            subconcept: The title of the sub-concept.
            level: The student's current level ('beginner' or 'intermediate').
            curriculum_notes: Reference grounding facts loaded from the curriculum tool.
        """
        try:
            prompt = (
                f"Concept to teach: '{subconcept}'\n"
                f"Student learning level: {level}\n"
                f"Grounding curriculum notes: {curriculum_notes}\n\n"
                f"Provide a clear explanation with an analogy and a worked example."
            )
            response = generate_content_with_retry(
                model=self.model,
                system_instruction=self.instruction,
                user_prompt=prompt,
                temperature=0.2,
            )
            return response.text.strip()
        except Exception as e:
            print(f"[TUTOR ERROR] Explanation generation failed: {e}")
            return (
                f"Let's learn about **{subconcept}**!\n\n"
                f"Reference Notes: {curriculum_notes}\n\n"
                f"*(Note: An error occurred generating the custom explanation: {str(e)}. Let's practice with a quiz next!)*"
            )

    def generate_slides_summary(self, context_text: str) -> str:
        """Generates a JSON list of 5-7 slides summarizing key ideas from the provided context."""
        prompt = (
            f"Analyze the following educational context and summarize its key ideas into a presentation slide deck "
            f"containing exactly 5 to 7 slides.\n\n"
            f"Educational Context:\n{context_text[:10000]}\n\n"
            f"Requirements:\n"
            f"- Return a valid JSON array of objects representing slides.\n"
            f"- Each object in the array must contain exactly 2 keys:\n"
            f"  1. 'title': slide title string.\n"
            f"  2. 'points': a list of 2 to 4 key takeaways/bullet points (strings) for this slide.\n"
            f"- The first slide should be a Title Slide outlining the course name.\n"
            f"- Output ONLY the raw JSON array. Do not wrap it in markdown code blocks."
        )
        
        try:
            response = generate_content_with_retry(
                model=self.model,
                user_prompt=prompt,
                temperature=0.2,
            )
            return response.text.strip()
        except Exception as e:
            print(f"[TUTOR ERROR] Slide deck generation failed: {e}. Using fallback.")
            import json
            fallback_slides = [
                {"title": "Welcome to the Lesson Presentation", "points": ["An interactive course summary", "Generated dynamically from your uploaded PDF text"]},
                {"title": "Core Principles", "points": ["Overview of primary concepts", "Key terms and definitions", "Foundation analysis"]}
            ]
            return json.dumps(fallback_slides)
