import os
import json
import sys
import re
from mcp.server.fastmcp import FastMCP

# Ensure parent directory is in sys.path so we can import from core.storage
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from core.storage import save_progress as db_save_progress, load_progress as db_load_progress

# Initialize the FastMCP server
mcp = FastMCP("StudyBuddyMCP")

# Path to local knowledge base JSON
KB_PATH = os.path.join(os.path.dirname(__file__), "knowledge_base.json")

def load_kb():
    if os.path.exists(KB_PATH):
        try:
            with open(KB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading knowledge base JSON: {e}")
    return {}


def _normalize_text(text: str) -> str:
    return re.sub(r"[^a-z0-9\s]+", " ", text.lower()).strip()


def _find_best_subconcept_match(topic_entries: dict, subconcept: str):
    """Returns the closest matching KB entry for a generated subconcept label."""
    s_key = _normalize_text(subconcept)
    s_tokens = {token for token in s_key.split() if len(token) > 2}
    best_key = None
    best_value = None
    best_score = -1

    for key, value in topic_entries.items():
        k_key = _normalize_text(key)
        k_tokens = {token for token in k_key.split() if len(token) > 2}

        score = 0
        if s_key and (s_key in k_key or k_key in s_key):
            score += 5
        score += len(s_tokens & k_tokens) * 2

        # If the generated subconcept repeats the main topic, prefer a definition-like entry.
        if key.lower() in {"definition", "overview", "introduction"}:
            score += 1

        if score > best_score:
            best_key = key
            best_value = value
            best_score = score

    return best_key, best_value, best_score

@mcp.tool()
def get_curriculum_content(topic: str, subconcept: str) -> str:
    """Retrieves educational notes and examples for a given subconcept of a topic.
    
    This grounds the Tutor agent in factual knowledge, preventing hallucination.
    
    Args:
        topic: The overall subject (e.g. 'fractions', 'photosynthesis', 'basic algebra').
        subconcept: The specific lesson detail (e.g. 'adding fractions', 'chloroplasts').
    """
    kb = load_kb()
    t_key = topic.lower().strip()
    
    if t_key in kb:
        topic_entries = kb[t_key]
        best_key, best_value, best_score = _find_best_subconcept_match(topic_entries, subconcept)

        if best_value and best_score > 0:
            result = dict(best_value)
            result["matched_subconcept"] = best_key
            return json.dumps(result, indent=2)

        # Fall back to the first available topic entry so we stay grounded locally.
        fallback_key = next(iter(topic_entries.keys()))
        fallback_value = dict(topic_entries[fallback_key])
        fallback_value["matched_subconcept"] = fallback_key
        fallback_value["fallback_reason"] = (
            f"No close subconcept match found for '{subconcept}'. Using topic overview from '{fallback_key}'."
        )
        return json.dumps(fallback_value, indent=2)
        
    return json.dumps({
        "error": f"Topic '{topic}' is not in the curriculum knowledge base.",
        "available_topics": list(kb.keys())
    })

@mcp.tool()
def save_progress(session_id: str, state_json: str) -> str:
    """Persists the serialized student progress state in the SQLite database.
    
    Args:
        session_id: An anonymous session identifier string.
        state_json: The serialized JSON state containing progress parameters.
    """
    try:
        state = json.loads(state_json)
        success = db_save_progress(session_id, state)
        if success:
            return "Progress saved successfully to database."
        return "Failed to save progress."
    except Exception as e:
        return f"Error saving progress: {e}"

@mcp.tool()
def load_progress(session_id: str) -> str:
    """Loads the student progress state from the SQLite database as a JSON string.
    
    Args:
        session_id: An anonymous session identifier string.
    """
    try:
        state = db_load_progress(session_id)
        return json.dumps(state)
    except Exception as e:
        return json.dumps({"error": f"Error loading progress: {e}"})

if __name__ == "__main__":
    # Support running the server standalone on stdio (the standard MCP client mode)
    # Streamlit client launches this script as a subprocess using Stdio parameters.
    # Alternatively, you can run this file directly in terminal to interact with it.
    mcp.run()
