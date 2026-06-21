import asyncio
import os
import sys
import json
import re
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

class MCPClientHelper:
    """Helper class to connect to the MCP server and call tools.
    
    Design Decision:
    We support two execution paths:
    1. SSE (Server-Sent Events) HTTP transport: if MCP_SERVER_URL is set in .env.
    2. Stdio Subprocess transport (default): launches server.py as a Python subprocess.
    3. Direct Fallback: if MCP execution fails (e.g. library version mismatch or subprocess 
       fails), it directly executes the SQLite and local file lookups. This ensures the 
       app never crashes and remains fully functional in any environment.
    """

    @staticmethod
    async def call_tool_async(tool_name: str, arguments: dict) -> str:
        sse_url = os.getenv("MCP_SERVER_URL")
        
        if sse_url:
            # Connect via HTTP/SSE
            async with sse_client(sse_url) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    response = await session.call_tool(tool_name, arguments)
                    if response.content and len(response.content) > 0:
                        return response.content[0].text
                    return ""
        else:
            # Default: Connect via local stdio subprocess
            server_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "mcp_server",
                "server.py"
            )
            # Run the server with current python executable
            server_params = StdioServerParameters(
                command=sys.executable,
                args=[server_path]
            )
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    response = await session.call_tool(tool_name, arguments)
                    if response.content and len(response.content) > 0:
                        return response.content[0].text
                    return ""

    @classmethod
    def call_tool(cls, tool_name: str, arguments: dict) -> str:
        """Synchronous wrapper to execute async tool calls.
        
        Streamlit pages are run in synchronous threads, so we wrap the async event loop here.
        If any error occurs, it falls back to direct execution of backend functions.
        """
        try:
            # We create an event loop or use the running one
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
            if loop.is_running():
                # If the loop is already running (e.g., inside an async context),
                # we run the task using an executor or run it in a separate thread.
                # Since Streamlit is synchronous, loop.is_running() is usually false,
                # but to be absolutely safe, we provide a thread-safe runner:
                import nest_asyncio
                nest_asyncio.apply()
                return loop.run_until_complete(cls.call_tool_async(tool_name, arguments))
            else:
                return loop.run_until_complete(cls.call_tool_async(tool_name, arguments))
                
        except Exception as e:
            # Print warning and execute direct local fallback
            print(f"[MCP CLIENT WARNING] Connection failed, activating direct local fallback: {e}")
            return cls.execute_local_fallback(tool_name, arguments)

    @classmethod
    def execute_local_fallback(cls, tool_name: str, arguments: dict) -> str:
        """Executes database and KB lookups locally to ensure app reliability."""
        from core.storage import save_progress, load_progress

        def normalize_text(text: str) -> str:
            return re.sub(r"[^a-z0-9\s]+", " ", text.lower()).strip()

        def find_best_subconcept_match(topic_entries: dict, subconcept_text: str):
            s_key = normalize_text(subconcept_text)
            s_tokens = {token for token in s_key.split() if len(token) > 2}
            best_key = None
            best_value = None
            best_score = -1

            for key, value in topic_entries.items():
                k_key = normalize_text(key)
                k_tokens = {token for token in k_key.split() if len(token) > 2}

                score = 0
                if s_key and (s_key in k_key or k_key in s_key):
                    score += 5
                score += len(s_tokens & k_tokens) * 2
                if key.lower() in {"definition", "overview", "introduction"}:
                    score += 1

                if score > best_score:
                    best_key = key
                    best_value = value
                    best_score = score

            return best_key, best_value, best_score
        
        if tool_name == "save_progress":
            session_id = arguments.get("session_id")
            state_json = arguments.get("state_json")
            try:
                state = json.loads(state_json)
                save_progress(session_id, state)
                return "Progress saved successfully (local fallback)."
            except Exception as err:
                return f"Error in local fallback save: {err}"
                
        elif tool_name == "load_progress":
            session_id = arguments.get("session_id")
            state = load_progress(session_id)
            return json.dumps(state)
            
        elif tool_name == "get_curriculum_content":
            topic = arguments.get("topic", "").lower().strip()
            subconcept = arguments.get("subconcept", "").lower().strip()
            
            kb_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "mcp_server",
                "knowledge_base.json"
            )
            if os.path.exists(kb_path):
                try:
                    with open(kb_path, "r", encoding="utf-8") as f:
                        kb = json.load(f)
                    if topic in kb:
                        topic_entries = kb[topic]
                        best_key, best_value, best_score = find_best_subconcept_match(topic_entries, subconcept)
                        if best_value and best_score > 0:
                            result = dict(best_value)
                            result["matched_subconcept"] = best_key
                            return json.dumps(result)

                        fallback_key = next(iter(topic_entries.keys()))
                        fallback_value = dict(topic_entries[fallback_key])
                        fallback_value["matched_subconcept"] = fallback_key
                        fallback_value["fallback_reason"] = (
                            f"No close subconcept match found for '{subconcept}'. Using topic overview from '{fallback_key}'."
                        )
                        return json.dumps(fallback_value)
                except Exception as err:
                    return json.dumps({"error": f"Error loading local KB: {err}"})
                    
            return json.dumps({"error": f"Fallback: Topic '{topic}' not found in curriculum."})
            
        return f"Error: Tool '{tool_name}' not supported by fallback."
