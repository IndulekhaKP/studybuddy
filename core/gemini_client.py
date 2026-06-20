import time
import random

def generate_content_with_retry(client, model: str, contents, config=None, max_retries=5, initial_backoff=2.0):
    """Wraps Gemini client generate_content calls with exponential backoff on 429 rate limit errors."""
    backoff = initial_backoff
    for attempt in range(max_retries):
        try:
            if config:
                return client.models.generate_content(model=model, contents=contents, config=config)
            else:
                return client.models.generate_content(model=model, contents=contents)
        except Exception as e:
            err_msg = str(e)
            is_rate_limit = any(x in err_msg.lower() for x in ["429", "resource_exhausted", "quota", "rate limit", "limit exceeded"])
            if is_rate_limit and attempt < max_retries - 1:
                sleep_time = backoff + random.uniform(0, 1)
                print(f"[GEMINI RETRY] Rate limit hit (429). Retrying in {sleep_time:.2f} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(sleep_time)
                backoff *= 2
            else:
                raise e
