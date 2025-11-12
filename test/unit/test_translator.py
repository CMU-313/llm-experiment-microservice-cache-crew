import os
import time
import pytest
from unittest.mock import patch
from flask import Flask, request, jsonify

from src.translator import translate_content, get_translation, get_language

def test_chinese():
    is_english, translated_content = translate_content("这是一条中文消息")
    assert is_english is False
    assert translated_content == "This is a Chinese message"

@patch("src.translator.get_language")
@patch("src.translator.get_translation")
def test_unexpected_language(mock_translate, mock_language):
    mock_language.return_value = "I don't understand your request"
    mock_translate.return_value = "This is your first example."
    result = translate_content("Hier ist dein erstes Beispiel.")
    assert result == (False, "Unintelligible")

@patch("src.translator.get_language")
@patch("src.translator.get_translation")
def test_empty_translation(mock_translate, mock_language):
    mock_language.return_value = "German"
    mock_translate.return_value = ""
    result = translate_content("Hier ist dein erstes Beispiel.")
    assert result == (False, "Unintelligible")

@patch("src.translator.get_language")
@patch("src.translator.get_translation")
def test_non_english_characters_in_translation(mock_translate, mock_language):
    mock_language.return_value = "German"
    mock_translate.return_value = "你好。"
    result = translate_content("Hier ist dein erstes Beispiel.")
    assert result == (False, "Unintelligible")

@patch("src.translator.get_language")
@patch("src.translator.get_translation")
def test_language_detection_exception(mock_translate, mock_language):
    mock_language.side_effect = Exception("API timeout")
    mock_translate.return_value = "Translation failed."
    result = translate_content("Hier ist dein erstes Beispiel.")
    assert result == (False, "Unintelligible")

RUN_EVAL = os.getenv("RUN_EVAL") == "1"

#Ensure that Ollama is ready
def _ollama_ready():
    try:
        from src.translator import _ollama_client
        _ollama_client()
        return True
    except Exception:
        return False

LIVE_OK = RUN_EVAL and _ollama_ready()
requires_live = pytest.mark.skipif(not LIVE_OK, reason="Requires RUN_EVAL=1 and a local Ollama server")

_TRANSLATION_EVAL = [
    {"post": "¿Cómo estás hoy?", "expected": "How are you today?"},
    {"post": "これはテストです。", "expected": "This is a test."},
]

_LANGUAGE_EVAL = [
    {"post": "¿Cómo estás hoy?", "expected": "Spanish"},
    {"post": "Je voudrais un café, s'il vous plaît.", "expected": "French"},
    {"post": "Ich habe gestern einen sehr guten Film gesehen.", "expected": "German"},
    {"post": "Ciao, mi chiamo Luca e vivo a Roma.", "expected": "Italian"},
    {"post": "Привет, как дела?", "expected": "Russian"},
    {"post": "오늘 날씨가 정말 좋네요.", "expected": "Korean"},
    {"post": "Gracias por tu ayuda con el proyecto.", "expected": "Spanish"},
    {"post": "Hello there! How are you doing?", "expected": "English"},
]

_COMBINED_EVAL = [
    (False, "Here is your first example.", "Hier ist dein erstes Beispiel."),
    (False, "Hello everyone!", "Bonjour tout le monde!"),
    (False, "How are you today?", "¿Cómo estás hoy?"),
    (True, "This is your first example.", "This is your first example."),
    (True, "The weather is beautiful.", "The weather is beautiful."),
    (True, "Please help me with my homework.", "Please help me with my homework."),
    (True, "Good morning everyone!", "Good morning everyone!"),
]

@pytest.mark.skipif(not RUN_EVAL, reason="Set RUN_EVAL=1 to run evaluator tests")
@pytest.mark.parametrize("post,expected", [(c["post"], c["expected"]) for c in _TRANSLATION_EVAL])
def test_translation_eval_live(post, expected):
    assert get_translation(post) == expected

@pytest.mark.skipif(not RUN_EVAL, reason="Set RUN_EVAL=1 to run evaluator tests")
@pytest.mark.parametrize("post,expected", [(c["post"], c["expected"]) for c in _LANGUAGE_EVAL])
def test_language_eval_live(post, expected):
    assert get_language(post) == expected

@pytest.mark.skipif(not RUN_EVAL, reason="Set RUN_EVAL=1 to run evaluator tests")
@pytest.mark.parametrize("is_english_expected, expected_english, post", _COMBINED_EVAL)
def test_combined_eval_live(is_english_expected, expected_english, post):
    is_english, translated = translate_content(post)
    assert is_english is is_english_expected
    assert translated == expected_english

@patch("src.translator.get_language")
@patch("src.translator.get_translation")
def test_llm_normal_response(mock_translate, mock_language):
    # LLM behaves as expected
    mock_language.return_value = "French"
    mock_translate.return_value = "Hello everyone!"
    is_english, out = translate_content("Bonjour tout le monde!")
    assert is_english is False
    assert out == "Hello everyone!"

@patch("src.translator.get_language")
@patch("src.translator.get_translation")
def test_llm_gibberish_response(mock_translate, mock_language):
    mock_language.return_value = "Germ@n!!"
    mock_translate.return_value = "Anything here should be ignored"
    assert translate_content("Hier ist dein erstes Beispiel.") == (False, "Unintelligible")