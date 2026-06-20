import json
import os
from google.adk.agents import Agent
from google.genai import Client
from google.genai import types

class PlannerAgent:
    """Specialist Agent that structures the learning path.
    
    Responsibilities:
    - Receive a topic string.
    - Output a clean, ordered list of 3 to 6 sub-concepts.
    - Format output as a JSON array of strings.
    """
    
    def __init__(self):
        # We define a google-adk Agent to encapsulate the persona and parameters
        self.adk_agent = Agent(
            name="PlannerAgent",
            model="gemini-2.5-flash",
            instruction=(
                "You are an academic curriculum planner. Given a topic, break it down into an ordered "
                "JSON list of 3 to 6 atomic, sequential sub-concepts (from easiest/foundation to hardest/advanced) "
                "that a student must learn to master the topic. "
                "Your response must be a valid JSON array of strings. Do not return markdown, do not use backticks, "
                "and do not write anything else outside the JSON array."
            )
        )
        # We initialize the Gemini Client (uses GEMINI_API_KEY from environment)
        self.client = Client()

    def plan(self, topic: str, pdf_context: str = None) -> list[str]:
        """Generates a learning path of sub-concepts for the given topic or PDF context.
        
        Args:
            topic: The string subject (e.g. 'Photosynthesis').
            pdf_context: Optional extracted text from an uploaded PDF.
        Returns:
            A list of subconcept title strings.
        """
        if pdf_context:
            instruction = (
                "You are an academic curriculum planner. Read the provided document text and "
                "break down ONLY the concepts covered in this text into a logical sequence of "
                "3 to 6 atomic, sequential sub-concepts (from easiest/foundation to hardest/advanced). "
                "Your response must be a valid JSON array of strings. Do not return markdown, do not use backticks, "
                "and do not write anything else outside the JSON array."
            )
            prompt = f"Document Text:\n{pdf_context}\n\nBreak down this document into 3 to 6 key sequential concepts."
        else:
            instruction = self.adk_agent.instruction
            prompt = f"Break down the topic: '{topic}'"
        
        try:
            # We call the model with response_mime_type set to json to guarantee structured output
            from core.gemini_client import generate_content_with_retry
            response = generate_content_with_retry(
                client=self.client,
                model=self.adk_agent.model,
                contents=f"{instruction}\n\n{prompt}",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            
            subconcepts = json.loads(response.text.strip())
            if isinstance(subconcepts, list):
                # Return sanitized strings
                return [str(s).strip() for s in subconcepts if s]
            elif isinstance(subconcepts, dict) and "subconcepts" in subconcepts:
                return [str(s).strip() for s in subconcepts["subconcepts"] if s]
                
            return [f"Introduction to {topic}", f"Core of {topic}", f"Applications of {topic}"]
            
        except Exception as e:
            print(f"[PLANNER ERROR] Failed to generate path via Gemini: {e}. Using generic fallback.")
            # Fallback path if API key or JSON fails
            return [
                f"Introduction to {topic}",
                f"Core Principles of {topic}",
                f"Advanced Applications of {topic}"
            ]
