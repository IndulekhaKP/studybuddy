import re
import os
from google import genai
from google.genai import types

def sanitize_input(text: str) -> str:
    """Sanitizes user input to prevent prompt injection and HTML injection.
    
    Design Decision:
    We strip HTML tags and restrict the input to a maximum of 500 characters.
    This prevents abnormally large payloads and potential script injection.
    """
    if not text:
        return ""
    # Strip HTML tags
    clean = re.sub(r'<[^>]*>', '', text)
    # Truncate input to 500 characters
    return clean.strip()[:500]

def is_educational_and_safe(text: str) -> tuple[bool, str]:
    """Uses Gemini 2.0 Flash to verify if the topic is educational and safe.
    
    Returns:
        (is_safe, explanation_or_redirect_suggestion)
        If safe is False, the string explains why or redirects.
    """
    cleaned_text = sanitize_input(text)
    if not cleaned_text:
        return False, "Input is empty or invalid."
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Fallback if no API key is loaded yet
        return check_offline_guardrails(cleaned_text)
        
    try:
        client = genai.Client(api_key=api_key)
        
        # Guide prompt forcing structured JSON output
        system_instruction = (
            "You are a safety filter for StudyBuddy, an adaptive tutor. "
            "Your job is to determine if a student's topic request is appropriate "
            "for an academic environment. It must be related to educational concepts (e.g. math, science, "
            "history, literature, computer science, etc.). "
            "It must NOT contain unsafe, violent, sexually explicit, harmful, or offensive content. "
            "You must respond with a JSON object containing two fields:\n"
            "1. 'safe': boolean (true if appropriate and educational, false otherwise)\n"
            "2. 'reason': string (a friendly, polite refusal and redirect if unsafe/off-topic, e.g. 'I can only help you with academic topics like math or science! Let's try one of those.', or empty if safe).\n"
            "Do not output any markdown formatting, backticks, or other text outside the raw JSON."
        )
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"User request: '{cleaned_text}'",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                temperature=0.0
            )
        )
        
        import json
        result = json.loads(response.text.strip())
        return result.get("safe", False), result.get("reason", "")
    except Exception as e:
        print(f"Guardrails API call failed: {e}. Falling back to local offline filter.")
        return check_offline_guardrails(cleaned_text)

def check_offline_guardrails(text: str) -> tuple[bool, str]:
    """Offline backup safety check in case the API is unavailable."""
    words = text.lower().split()
    inappropriate_keywords = {
        "hack", "exploit", "cheat", "kill", "bomb", "hate", "abuse", "nsfw", "porn", "drugs", "weapons"
    }
    for word in words:
        # Check direct matches or substrings
        if any(bad_word in word for bad_word in inappropriate_keywords):
            return False, "This request violates safety policies. Please enter an educational topic like fractions or biology."
            
    # Simple length check - topics should typically be brief
    if len(text.split()) > 10:
        return False, "Topics should be concise names (e.g., 'Fractions', 'Photosynthesis'). Please try a shorter phrase."
        
    return True, ""
