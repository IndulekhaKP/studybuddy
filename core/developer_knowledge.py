from core.llm_client import generate_content_with_retry, get_model, has_valid_api_key

def query_developer_docs(query: str) -> str | None:
    """Generates concise developer-oriented grounding notes for technical topics.
    
    Args:
        query: The search term or subconcept to search for.
    Returns:
        A formatted string of relevant notes, or None if the call fails.
    """
    if not has_valid_api_key():
        print("[DEV KNOWLEDGE] No valid Groq API key found in environment.")
        return None

    try:
        prompt = (
            "Provide short, factual developer notes for the following topic.\n"
            "Return plain text only, no markdown headings, and focus on definitions, core concepts, and practical context.\n\n"
            f"Topic: {query}"
        )
        response = generate_content_with_retry(
            model=get_model(task="developer_notes"),
            user_prompt=prompt,
            temperature=0.1,
        )
        return response.text.strip() or None
    except Exception as e:
        print(f"[DEV KNOWLEDGE WARNING] Developer note generation failed: {e}.")
        return None
