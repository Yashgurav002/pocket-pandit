"""One OpenAI-compatible chat client. Default: Gemma on local Ollama.

Switch to the hosted free Gemma (or any open model server) with env vars:
LLM_BASE_URL, GEMMA_MODEL, GEMMA_API_KEY.
"""
import os

import requests

BASE = os.environ.get("LLM_BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("GEMMA_MODEL", "gemma3:4b")


def ask(prompt, temperature=0.3):
    """Return the model's reply, or None if the model is unavailable (callers fall back)."""
    if os.environ.get("PANDIT_NO_LLM"):
        return None
    try:
        r = requests.post(f"{BASE}/chat/completions", timeout=600,
                          headers={"Authorization": f"Bearer {os.environ.get('GEMMA_API_KEY', 'ollama')}"},
                          json={"model": MODEL, "temperature": temperature,
                                "messages": [{"role": "user", "content": prompt}]})
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except (requests.RequestException, KeyError, IndexError) as e:
        print(f"[llm] unavailable: {e}")
        return None
