import sqlite3
import json
import os

# SQLite database file path (located in the project root)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "studybuddy.db")

def init_db():
    """Initializes the SQLite database and creates the progress table if it doesn't exist.
    
    Design Decision: 
    Using a single table 'progress' where session_id is the primary key.
    We serialize the entire progress state (curriculum path, current index, scores, etc.) 
    into a JSON string to enable flexible schema evolution while keeping storage logic simple.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            session_id TEXT PRIMARY KEY,
            state TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_progress(session_id: str, state: dict) -> bool:
    """Persists the session progress dictionary to SQLite.
    
    Args:
        session_id: A unique anonymous random identifier for the student session.
        state: Dict containing current learning path, scores, difficulty level, and history.
    """
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        state_str = json.dumps(state)
        # Using INSERT OR REPLACE (ON CONFLICT) to update state for existing sessions
        cursor.execute("""
            INSERT INTO progress (session_id, state)
            VALUES (?, ?)
            ON CONFLICT(session_id) DO UPDATE SET state=excluded.state
        """, (session_id, state_str))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Database error saving progress: {e}")
        return False

def load_progress(session_id: str) -> dict:
    """Loads and deserializes the student progress dictionary from SQLite.
    
    Args:
        session_id: The unique session identifier to retrieve.
    Returns:
        A dictionary of the session state, or empty dict if not found.
    """
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT state FROM progress WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return json.loads(row[0])
        return {}
    except Exception as e:
        print(f"Database error loading progress: {e}")
        return {}
