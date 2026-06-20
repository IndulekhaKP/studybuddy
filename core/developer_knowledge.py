import os
import json
import urllib.request
import urllib.parse

def query_developer_docs(query: str) -> str | None:
    """Queries the Google Developer Knowledge API for documentation chunks.
    
    Args:
        query: The search term or subconcept to search for.
    Returns:
        A formatted string of relevant snippets, or None if the query fails or API is not enabled.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[DEV KNOWLEDGE] No API key found in environment.")
        return None
        
    try:
        # Base url and encoded parameters
        base_url = "https://developerknowledge.googleapis.com/v1alpha/documents:searchDocumentChunks"
        params = {
            "query": query,
            "key": api_key,
            "pageSize": 3
        }
        url_parts = list(urllib.parse.urlparse(base_url))
        url_parts[4] = urllib.parse.urlencode(params)
        url = urllib.parse.urlunparse(url_parts)
        
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "StudyBuddyTutor/1.0", "Content-Type": "application/json"},
            method="GET"
        )
        
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                chunks = data.get("documentChunks", [])
                if not chunks:
                    return None
                    
                context_parts = []
                for chunk in chunks:
                    content = chunk.get("content", {}).get("markdown", "")
                    uri = chunk.get("document", {}).get("uri", "")
                    if content:
                        source = f" (Source: {uri})" if uri else ""
                        context_parts.append(f"{content.strip()}{source}")
                        
                if context_parts:
                    return "\n\n---\n\n".join(context_parts)
            return None
    except Exception as e:
        # Gracefully handle 403 Forbidden, 400 Bad Request, timeouts, etc.
        print(f"[DEV KNOWLEDGE WARNING] Developer Knowledge API query failed: {e}. Falling back to Google Search.")
        return None
