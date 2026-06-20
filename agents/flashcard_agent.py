import json
from google.adk.agents import Agent
from google.genai import Client
from google.genai import types


class FlashcardAgent:
    """Smart Flashcard Agent that generates targeted revision flashcards for weak topics.
    
    Responsibilities:
    - Detect topics where the student made errors (from session history).
    - Generate focused, high-quality flip flashcards for those weak spots.
    - Return flashcards as a structured list of {front, back} dicts.
    """

    def __init__(self):
        self.adk_agent = Agent(
            name="FlashcardAgent",
            model="gemini-2.0-flash",
            instruction=(
                "You are an expert educational flashcard creator. "
                "Given a list of weak topics a student struggled with, you generate concise, "
                "high-quality flashcards to help them revise. "
                "Each flashcard has a clear question on the front and a precise answer on the back. "
                "Keep flashcard fronts under 15 words and backs under 30 words."
            )
        )
        self.client = Client()

    def detect_weak_topics(self, history: list) -> list:
        """Scans session history and returns subconcepts where the student failed.
        
        Args:
            history: The session state history list (list of evaluation log dicts).
        Returns:
            List of subconcept strings where student answered incorrectly.
        """
        weak = []
        for log in history:
            if not log.get("correct", True):
                subconcept = log.get("subconcept", "")
                if subconcept and subconcept not in weak:
                    weak.append(subconcept)
        return weak

    def generate_mistake_flashcards(self, weak_topics: list, level: str = "intermediate") -> list:
        """Generates targeted revision flashcards for weak/failed topics.
        
        Args:
            weak_topics: List of subconcept strings where student made errors.
            level: Current student difficulty level.
        Returns:
            List of dicts: [{"front": str, "back": str}, ...]
        """
        if not weak_topics:
            return []
        
        topics_str = ", ".join(weak_topics)
        prompt = (
            f"Generate revision flashcards for a {level}-level student who struggled with: "
            f"{topics_str}.\n\n"
            f"Requirements:\n"
            f"- Generate 2 flashcards per topic (total {len(weak_topics) * 2} cards).\n"
            f"- Return a JSON array of objects with exactly 2 keys each: 'front' and 'back'.\n"
            f"- 'front': a short question (under 15 words) about the concept.\n"
            f"- 'back': a concise, accurate answer (under 30 words).\n"
            f"- Make flashcards pedagogically useful - focus on key definitions, principles, or formulas.\n"
            f"- Return only the raw JSON array, no markdown code fences."
        )
        
        try:
            from core.gemini_client import generate_content_with_retry
            response = generate_content_with_retry(
                client=self.client,
                model=self.adk_agent.model,
                contents=f"{self.adk_agent.instruction}\n\n{prompt}",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3
                )
            )
            cards = json.loads(response.text.strip())
            if isinstance(cards, list):
                return [c for c in cards if "front" in c and "back" in c]
            return []
        except Exception as e:
            print(f"[FLASHCARD AGENT ERROR] Failed to generate flashcards: {e}")
            fallback = []
            for topic in weak_topics:
                fallback.append({
                    "front": f"What is the core idea behind {topic}?",
                    "back": f"{topic} is a fundamental concept - review your lesson notes to master it."
                })
            return fallback

    def build_html_flashcard_deck(self, flashcards: list, title: str = "Revision Flashcards") -> str:
        """Builds a downloadable HTML flip-card deck from a list of flashcards.
        
        Args:
            flashcards: List of {front, back} dicts.
            title: Title for the HTML deck.
        Returns:
            HTML string of the complete flip-card deck.
        """
        cards_html = ""
        for i, card in enumerate(flashcards):
            front = str(card.get("front", "")).replace("<", "&lt;").replace(">", "&gt;")
            back = str(card.get("back", "")).replace("<", "&lt;").replace(">", "&gt;")
            cards_html += f"""
            <div class="flip-card" onclick="this.classList.toggle('flipped')">
                <div class="flip-card-inner">
                    <div class="flip-card-front">
                        <div class="card-num">Card {i + 1}</div>
                        <div class="card-text">{front}</div>
                        <div class="card-hint">Click to flip</div>
                    </div>
                    <div class="flip-card-back">
                        <div class="card-num">Answer</div>
                        <div class="card-text">{back}</div>
                    </div>
                </div>
            </div>
            """
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - StudyBuddy</title>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #1A0F07 0%, #2C1810 100%);
            min-height: 100vh;
            padding: 40px 20px;
            color: #F5E6D0;
        }}
        h1 {{
            font-family: 'Playfair Display', serif;
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(90deg, #FF6F20 0%, #F2C94C 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .subtitle {{
            text-align: center;
            color: #D9B68C;
            margin-bottom: 40px;
            font-size: 1rem;
        }}
        .card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 24px;
            max-width: 1100px;
            margin: 0 auto;
        }}
        .flip-card {{
            background: transparent;
            height: 200px;
            perspective: 1000px;
            cursor: pointer;
        }}
        .flip-card-inner {{
            position: relative;
            width: 100%;
            height: 100%;
            transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            transform-style: preserve-3d;
            border-radius: 16px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        }}
        .flip-card.flipped .flip-card-inner {{
            transform: rotateY(180deg);
        }}
        .flip-card-front, .flip-card-back {{
            position: absolute;
            width: 100%;
            height: 100%;
            -webkit-backface-visibility: hidden;
            backface-visibility: hidden;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
            border-radius: 16px;
        }}
        .flip-card-front {{
            background: linear-gradient(135deg, #2C1810 0%, #3D2010 100%);
            border: 1px solid #FF6F20;
        }}
        .flip-card-back {{
            background: linear-gradient(135deg, #FF6F20 0%, #A65E2E 100%);
            transform: rotateY(180deg);
        }}
        .card-num {{
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-weight: 600;
            margin-bottom: 12px;
            opacity: 0.7;
        }}
        .card-text {{
            font-size: 1rem;
            font-weight: 500;
            line-height: 1.5;
            text-align: center;
        }}
        .card-hint {{
            font-size: 0.7rem;
            opacity: 0.5;
            margin-top: 12px;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: #A65E2E;
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>
    <h1>\U0001f342 {title}</h1>
    <p class="subtitle">StudyBuddy - Smart Mistake Flashcards &nbsp;|&nbsp; Click any card to flip</p>
    <div class="card-grid">
        {cards_html}
    </div>
    <div class="footer">Generated by StudyBuddy Adaptive Tutor &nbsp;\U0001f393</div>
</body>
</html>"""


class_symbols = [FlashcardAgent]
