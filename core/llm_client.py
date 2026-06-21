import os
import random
import time
import urllib.error
import urllib.request
import json
from dataclasses import dataclass


DEFAULT_MODEL = "openai/gpt-oss-20b"
DEFAULT_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
TASK_MODEL_DEFAULTS = {
    "planner": "llama-3.1-8b-instant",
    "tutor": "openai/gpt-oss-120b",
    "quiz": "openai/gpt-oss-120b",
    "evaluator": "llama-3.1-8b-instant",
    "flashcards": "llama-3.1-8b-instant",
    "guardrails": "llama-3.1-8b-instant",
    "grounding": "llama-3.1-8b-instant",
    "developer_notes": "llama-3.1-8b-instant",
}


@dataclass
class LLMResponse:
    text: str


def get_api_key() -> str:
    return os.getenv("GROQ_API_KEY", "").strip()


def get_model(task: str | None = None, default: str = DEFAULT_MODEL) -> str:
    if task:
        task_env = os.getenv(f"LLM_MODEL_{task.upper()}", "").strip()
        if task_env:
            return task_env
        if task in TASK_MODEL_DEFAULTS:
            return TASK_MODEL_DEFAULTS[task]

    model = os.getenv("LLM_MODEL", "").strip()
    return model or default


def has_valid_api_key() -> bool:
    return get_api_key().startswith("gsk_")


def generate_content_with_retry(
    model: str,
    user_prompt: str,
    system_instruction: str | None = None,
    temperature: float = 0.2,
    max_retries: int = 5,
    initial_backoff: float = 2.0,
) -> LLMResponse:
    """Calls Groq's OpenAI-compatible chat completions API with retry handling."""
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing.")

    payload = {
        "model": model,
        "messages": [],
        "temperature": max(temperature, 1e-8),
    }

    if system_instruction:
        payload["messages"].append({"role": "system", "content": system_instruction})
    payload["messages"].append({"role": "user", "content": user_prompt})

    request = urllib.request.Request(
        DEFAULT_BASE_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 StudyBuddy/1.0",
        },
        method="POST",
    )

    backoff = initial_backoff
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
                text = data["choices"][0]["message"]["content"]
                return LLMResponse(text=text.strip())
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            err_msg = f"HTTP {exc.code}: {body}"
            is_retryable = exc.code in {429, 500, 502, 503, 504}
            if is_retryable and attempt < max_retries - 1:
                sleep_time = backoff + random.uniform(0, 1)
                print(
                    f"[LLM RETRY] Temporary API error. Retrying in {sleep_time:.2f}s "
                    f"(Attempt {attempt + 1}/{max_retries})"
                )
                time.sleep(sleep_time)
                backoff *= 2
                continue
            raise RuntimeError(err_msg) from exc
        except Exception:
            if attempt < max_retries - 1:
                sleep_time = backoff + random.uniform(0, 1)
                time.sleep(sleep_time)
                backoff *= 2
                continue
            raise
