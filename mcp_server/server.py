import os
import json
import sys
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
    s_key = subconcept.lower().strip()
    
    if t_key in kb:
        # Look for subconcept matching in keys
        for key, value in kb[t_key].items():
            if s_key in key.lower() or key.lower() in s_key:
                return json.dumps(value, indent=2)
        
        # Topic found but not this specific subconcept. Return available subconcepts as options
        return json.dumps({
            "message": f"Subconcept '{subconcept}' not found for topic '{topic}'.",
            "available_subconcepts": list(kb[t_key].keys())
        })
        
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
