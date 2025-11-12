import os
import time
import pytest
from unittest.mock import patch

from src.translator import translate_content, get_translation, get_language

def test_chinese():
    # Deterministic canned case in translate_content
    is_english, translated_content = translate_content("这是一条中文消息")
    assert is_english is False
    assert translated_content == "This is a Chinese message"

@patch("src.translator.get_language")
@patch("src.translator.get_translation")
def test_unexpected_language(mock_translate, mock_language):
    mock_language.return_value = "I don't understand your request"  # invalid classifier output
    mock_translate.return_value = "This is your first example."
    result = translate_content("Hier ist dein erstes Beispiel.")
    assert result == (False, "Unintelligible")

@patch("src.translator.get_language")
@patch("src.translator.get_translation")
def test_empty_translation(mock_translate, mock_language):
    mock_language.return_value = "German"
    mock_translate.return_value = ""  # empty => invalid
    result = translate_content("Hier ist dein erstes Beispiel.")
    assert result == (False, "Unintelligible")

@patch("src.translator.get_language")
@patch("src.translator.get_translation")
def test_non_english_characters_in_translation(mock_translate, mock_language):
    mock_language.return_value = "German"
    mock_translate.return_value = "你好。"  # non-ASCII => invalid by our validator
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

_TRANSLATION_EVAL = [
    {"post": "Bonjour tout le monde!", "expected": "Hello everyone!"},
    {"post": "¿Cómo estás hoy?", "expected": "How are you today?"},
    {"post": "Je voudrais un café, s'il vous plaît.", "expected": "I would like a coffee, please."},
    {"post": "Ich habe gestern einen sehr guten Film gesehen.", "expected": "I watched a really good movie yesterday."},
    {"post": "これはテストです。", "expected": "This is a test."},
    {"post": "Ciao, mi chiamo Luca e vivo a Roma.", "expected": "Hi, my name is Luca and I live in Rome."},
    {"post": "Привет, как дела?", "expected": "Hi, how are you?"},
    {"post": "오늘 날씨가 정말 좋네요.", "expected": "The weather is really nice today."},
    {"post": "Gracias por tu ayuda con el proyecto.", "expected": "Thank you for your help with the project."},
    {"post": "Xin chao, ban co khoe khong?", "expected": "Hello, how are you?"},
]

_LANGUAGE_EVAL = [
    {"post": "Bonjour tout le monde!", "expected": "French"},
    {"post": "¿Cómo estás hoy?", "expected": "Spanish"},
    {"post": "Je voudrais un café, s'il vous plaît.", "expected": "French"},
    {"post": "Ich habe gestern einen sehr guten Film gesehen.", "expected": "German"},
    {"post": "これはテストです。", "expected": "Japanese"},
    {"post": "Ciao, mi chiamo Luca e vivo a Roma.", "expected": "Italian"},
    {"post": "Привет, как дела?", "expected": "Russian"},
    {"post": "오늘 날씨가 정말 좋네요.", "expected": "Korean"},
    {"post": "Gracias por tu ayuda con el proyecto.", "expected": "Spanish"},
    {"post": "Hello there! How are you doing?", "expected": "English"},
]

_COMBINED_EVAL = [
    # non-English => expect (False, translated)
    (False, "Here is your first example.", "Hier ist dein erstes Beispiel."),
    (False, "Hello everyone!", "Bonjour tout le monde!"),
    (False, "How are you today?", "¿Cómo estás hoy?"),
    (False, "This is a test.", "これはテストです。"),
    (False, "It is a beautiful day.", "C’est une belle journée."),
    (True, "This is your first example.", "This is your first example."),
    (True, "How are you today?", "How are you today?"),
    (True, "The weather is beautiful.", "The weather is beautiful."),
    (True, "Please help me with my homework.", "Please help me with my homework."),
    (True, "Good morning everyone!", "Good morning everyone!"),
]