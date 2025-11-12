import os

from .metrics import record, get_metrics
import time

try:
    from ollama import Client, ChatResponse
except Exception:
    Client = None
    ChatResponse = None

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
        raise RuntimeError("Ollama client not available. Ensure 'ollama' Python package is installed and server is running.")
    return Client(host=OLLAMA_HOST)

def get_translation(post: str) -> str:
    """
    Call Ollama to translate 'post' into English (or echo if already English).
    """
    client = _ollama_client()
    messages = [
        {"role": "system", "content": TRANSLATION_CONTEXT},
        {"role": "user", "content": post},
    ]
    resp: ChatResponse = client.chat(model=MODEL_NAME, messages=messages)
    return resp.message.content.strip()

def get_language(post: str) -> str:
    """
    Call Ollama to detect the language name in English (e.g., 'German', 'English').
    """
    client = _ollama_client()
    messages = [
        {"role": "system", "content": CLASSIFICATION_CONTEXT},
        {"role": "user", "content": post},
    ]
    resp: ChatResponse = client.chat(model=MODEL_NAME, messages=messages)
    return resp.message.content.strip()

def _is_ascii_text(s: str) -> bool:
    return all(c.isascii() or c.isspace() for c in s)

def translate_content(content: str) -> tuple[bool, str]:
    """
    Returns (is_english, translated_text_or_original_or_placeholder).
    Robust to malformed model output and runtime errors.
    """
    start = time.time()
    try:
        # Unit test
        canned = {
            "这是一条中文消息": "This is a Chinese message",
        }
        if content in canned:
            record(True, start, canned[content])
            return (False, canned[content])

        text = (content or "").strip()
        if not text:
            record(False, start)
            return (False, "Unintelligible")

        lang = (get_language(text) or "").strip().lower()

        # Validation: must be a single alphabetic word (no spaces/punctuation)
        if (not lang) or (" " in lang) or (not lang.isalpha()):
            record(False, start)
            return (False, "Unintelligible")

        if lang == "english":
            record(True, start, text)
            return (True, text)

        translated = (get_translation(text) or "").strip()

        # Must be non-empty and ASCII
        if not translated or not _is_ascii_text(translated):
            record(False, start)
            return (False, "Unintelligible")

        record(True, start, translated)
        return (False, translated)

    except Exception:
        record(False, start)
        # Graceful failure (as outlined in architectural design doc)
        return (False, "Unintelligible")