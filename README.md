# StudyBuddy: Adaptive Tutoring Agent (Agents for Good)

StudyBuddy is a multi-agent adaptive tutoring system designed for the "Agents for Good" track. The application helps students learn complex topics by breaking them down into a personalized path, explaining concepts with level-tailored analogies and worked examples, testing comprehension, and dynamically adjusting lesson difficulty in real time based on user feedback.

---

## Architecture Overview

StudyBuddy leverages a hierarchical multi-agent coordination structure built using Google's Agent Development Kit (ADK) and Gemini. The orchestration loop consists of:
- **Planner Agent**: Splits the requested topic into an ordered list of 3-6 sub-concepts.
- **Tutor Agent**: Explains concepts using analogies and worked examples, tailored to the student's difficulty level (Beginner or Intermediate) and grounded in reference curriculum content.
- **Quiz Agent**: Generates level-appropriate test questions and grades student responses.
- **Evaluator Agent**: Runs the adaptive loop decision logic, deciding whether to advance, repeat the same lesson, or drop the difficulty.
- **MCP Server**: FastMCP server that exposes tools for looking up curriculum grounded content and loading/saving anonymous student progress.

```
       +-----------------------+
       |   Streamlit Web UI    |
       +-----------+-----------+
                   |
                   v
       +-----------------------+
       |  Orchestrator Agent   |
       +-----------+-----------+
                   |
     +-------------+-------------+
     |             |             |
     v             v             v
+----------+  +---------+  +-----------+
| Planner  |  |  Tutor  |  |   Quiz    |
+----------+  +----+----+  +-----+-----+
                   |             |
                   v             v
+----------+  +----+----+  +-----+-----+
|Evaluator |<--| Ground  |<--| Grader  |
+----------+  +----+----+  +-----------+
                   |
                   v
     +-----------------------+
     |   FastMCP Server      |
     | (Curriculum & SQLite) |
     +-----------------------+
```

---

## Folder Structure

```
studybuddy/
├── README.md
├── .env.example
├── .gitignore
├── requirements.txt
├── app.py                  # Streamlit UI + orchestration entry point
├── agents/
│   ├── orchestrator.py     # Main coordinator agent
│   ├── planner.py          # Lesson path generation agent
│   ├── tutor.py            # Analogy and explanation agent
│   ├── quiz.py             # Question generator & answer grading agent
│   └── evaluator.py        # Adaptive loop progression decision agent
├── mcp_server/
│   ├── server.py           # FastMCP server exposing curriculum + storage tools
│   ├── client.py           # Resilient MCP client helper (stdio & SSE)
│   └── knowledge_base.json # Grounded curriculum content (fractions, photosynthesis, basic algebra)
├── core/
│   ├── guardrails.py       # Input sanitization and educational safety check
│   └── storage.py          # SQLite persistence layer
└── docs/
    └── architecture.md     # In-depth architectural design description
```

---

## Setup & Running Guide

Follow these steps to run StudyBuddy from a clean clone:

### 1. Create a Virtual Environment and Install Dependencies
Open your terminal and navigate to the project directory:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy the `.env.example` file to `.env`:
```bash
copy .env.example .env
```
Open `.env` and fill in your Gemini API key:
```env
GEMINI_API_KEY=AIzaSy...
```

### 3. Run the Application
Our client helper features a **zero-config mode** that launches the MCP server automatically as a background subprocess using `stdio`. To run the application in this mode, simply start the Streamlit UI:
```bash
streamlit run app.py
```

*Alternative (Dedicated Server Mode)*:
If you want to run the MCP server as a separate network service over HTTP/SSE:
1. In one terminal, run:
   ```bash
   python mcp_server/server.py
   ```
   *(By default, FastMCP launches an HTTP server listening on standard ports or prompts you. To run over SSE, set `transport="sse"` in `server.py` and run).*
2. Add `MCP_SERVER_URL` to your `.env` pointing to your running server (e.g. `http://localhost:8000/sse`).
3. In a second terminal, run:
   ```bash
   streamlit run app.py
   ```

---

## Course Concepts & Implementation Map

- **Safety & Input Sanitization**: Implemented in [core/guardrails.py](file:///C:/Users/user/.gemini/antigravity/scratch/studybuddy/core/guardrails.py#L7-L38) using a double filter (HTML strip and Gemini safety check).
- **SQLite DB Persistence**: Code located in [core/storage.py](file:///C:/Users/user/.gemini/antigravity/scratch/studybuddy/core/storage.py#L9-L72).
- **FastMCP Server**: Custom tools exposed in [mcp_server/server.py](file:///C:/Users/user/.gemini/antigravity/scratch/studybuddy/mcp_server/server.py#L19-L74).
- **Multi-Agent Orchestration**: Managed by [agents/orchestrator.py](file:///C:/Users/user/.gemini/antigravity/scratch/studybuddy/agents/orchestrator.py#L9-L157).
- **Adaptive Difficulty Loop**: Evaluator logic written in [agents/evaluator.py](file:///C:/Users/user/.gemini/antigravity/scratch/studybuddy/agents/evaluator.py#L8-L100).
- **Frontend Dashboard**: Streamlit code in [app.py](file:///C:/Users/user/.gemini/antigravity/scratch/studybuddy/app.py#L11-L245).
