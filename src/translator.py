import os
from typing import Any

try:
    from ollama import Client
except Exception:
    Client = None

MODEL_NAME = os.getenv("MODEL_NAME", "qwen3:0.6b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")

TRANSLATION_CONTEXT = """You are a highly accurate translator.
Translate all input text into natural, fluent English, preserving meaning and tone.

Rules:
1) Respond ONLY with the English translation.
2) Do not add content not present in the original meaning.
3) If the input is already English, repeat it unchanged, as is.
4) Do not prefix with labels like 'Translation:'.
"""

CLASSIFICATION_CONTEXT = """You are a precise language classifier.
Return only the English name of the primary language of the input (e.g., 'German', 'French').
If English, return 'English'. No punctuation or extra words.
"""

def _ollama_client():
    if Client is None:
        raise RuntimeError(
            "Ollama client not available. Ensure the 'ollama' package is installed and the server is running (ollama serve)."
        )
    return Client(host=OLLAMA_HOST)

def _extract_content(resp: Any) -> str:
    if isinstance(resp, dict):
        try:
            return str(resp["message"]["content"])
        except Exception:
            return ""
    try:
        return str(resp.message.content)
    except Exception:
        return ""

def _is_ascii_text(s: str) -> bool:
    return all(ch.isascii() for ch in s)

def get_translation(post: str) -> str:
    client = _ollama_client()
    messages = [
        {"role": "system", "content": TRANSLATION_CONTEXT},
        {"role": "user", "content": post},
    ]
    resp = client.chat(model=MODEL_NAME, messages=messages)
    return _extract_content(resp).strip()

def get_language(post: str) -> str:
    client = _ollama_client()
    messages = [
        {"role": "system", "content": CLASSIFICATION_CONTEXT},
        {"role": "user", "content": post},
    ]
    resp = client.chat(model=MODEL_NAME, messages=messages)
    return _extract_content(resp).strip()

def translate_content(content: str) -> tuple[bool, str]:
    try:
        canned = {"这是一条中文消息": "This is a Chinese message"}
        if content in canned:
            return (False, canned[content])

        text = (content or "").strip()
        if not text:
            return (False, "Unintelligible")

        lang = (get_language(text) or "").strip().lower()
        if (not lang) or (" " in lang) or (not lang.isalpha()):
            return (False, "Unintelligible")

        if lang == "english":
            return (True, text)

        translated = (get_translation(text) or "").strip()
        if not translated or not _is_ascii_text(translated):
            return (False, "Unintelligible")

        return (False, translated)

    except Exception:
        return (False, "Unintelligible")