from google.adk.agents import Agent
from google.genai import Client

class TutorAgent:
    """Specialist Agent that explains academic concepts.
    
    Responsibilities:
    - Teach the student concept-by-concept.
    - Ground explanations using reference curriculum notes (from the MCP server) to prevent hallucination.
    - Use an intuitive analogy and a worked-out example.
    - Adapt explanation depth and language depending on the student's level (beginner / intermediate).
    """

    def __init__(self):
        # Configure ADK Agent settings
        self.adk_agent = Agent(
            name="TutorAgent",
            model="gemini-2.5-flash",
            instruction=(
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
        )
        self.client = Client()

    def explain(self, subconcept: str, level: str, curriculum_notes: str) -> str:
        """Generates an explanation for the subconcept tailored to the student level.
        
        Args:
            subconcept: The title of the sub-concept.
            level: The student's current level ('beginner' or 'intermediate').
            curriculum_notes: Reference grounding facts loaded from the curriculum tool.
        """
        from google.genai import types
        
        try:
            if curriculum_notes == "USE_GOOGLE_SEARCH":
                prompt = (
                    f"Concept to teach: '{subconcept}'\n"
                    f"Student learning level: {level}\n\n"
                    f"You must use the Google Search tool to search for verified academic details "
                    f"on this concept. Then, provide a clear explanation containing a relatable analogy "
                    f"and a worked example based on those search results."
                )
                response = self.client.models.generate_content(
                    model=self.adk_agent.model,
                    contents=f"{self.adk_agent.instruction}\n\n{prompt}",
                    config=types.GenerateContentConfig(
                        tools=[types.Tool(google_search=types.GoogleSearch())]
                    )
                )
            else:
                prompt = (
                    f"Concept to teach: '{subconcept}'\n"
                    f"Student learning level: {level}\n"
                    f"Grounding curriculum notes: {curriculum_notes}\n\n"
                    f"Provide a clear explanation with an analogy and a worked example."
                )
                response = self.client.models.generate_content(
                    model=self.adk_agent.model,
                    contents=f"{self.adk_agent.instruction}\n\n{prompt}"
                )
            return response.text.strip()
        except Exception as e:
            print(f"[TUTOR ERROR] Explanation generation failed: {e}")
            return (
                f"Let's learn about **{subconcept}**!\n\n"
                f"Reference Notes: {curriculum_notes}\n\n"
                f"*(Note: An error occurred generating the custom explanation: {str(e)}. Let's practice with a quiz next!)*"
            )

    def generate_slides_summary(self, pdf_text: str) -> str:
        """Generates a JSON list of 5-7 slides summarizing key ideas from the PDF text."""
        from google.genai import types
        
        prompt = (
            f"Analyze the following document text and summarize its key ideas into a presentation slide deck "
            f"containing exactly 5 to 7 slides.\n\n"
            f"Document Text:\n{pdf_text[:10000]}\n\n"
            f"Requirements:\n"
            f"- Return a valid JSON array of objects representing slides.\n"
            f"- Each object in the array must contain exactly 2 keys:\n"
            f"  1. 'title': slide title string.\n"
            f"  2. 'points': a list of 2 to 4 key takeaways/bullet points (strings) for this slide.\n"
            f"- The first slide should be a Title Slide outlining the course name.\n"
            f"- Output ONLY the raw JSON array. Do not wrap it in markdown code blocks."
        )
        
        try:
            response = self.client.models.generate_content(
                model=self.adk_agent.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2
                )
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
