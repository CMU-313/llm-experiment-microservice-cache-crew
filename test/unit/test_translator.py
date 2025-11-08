from src.translator import translate_content
from unittest.mock import patch

def test_chinese():
    is_english, translated_content = translate_content("这是一条中文消息")
    assert is_english == False
    assert translated_content == "This is a Chinese message"

def test_llm_normal_response():
    pass

def test_llm_gibberish_response():
    pass

# Tests from Collab Notebook

@patch("__main__.get_language")
@patch("__main__.get_translation")
def test_unexpected_language(mock_translate, mock_language):
    mock_language.return_value = "I don't understand your request"
    mock_translate.return_value = "This is your first example."

    result = translate_content("Hier ist dein erstes Beispiel.")
    assert result == (False, "Unintelligible")

@patch("__main__.get_language")
@patch("__main__.get_translation")
def test_empty_translation(mock_translate, mock_language):
    mock_language.return_value = "German"
    mock_translate.return_value = ""

    result = translate_content("Hier ist dein erstes Beispiel.")
    assert result == (False, "Unintelligible")

@patch("__main__.get_language")
@patch("__main__.get_translation")
def test_non_english_characters_in_translation(mock_translate, mock_language):
    mock_language.return_value = "German"
    mock_translate.return_value = "你好。"

    result = translate_content("Hier ist dein erstes Beispiel.")
    assert result == (False, "Unintelligible")

@patch("__main__.get_language")
@patch("__main__.get_translation")
def test_language_detection_exception(mock_translate, mock_language):
    mock_language.side_effect = Exception("API timeout")
    mock_translate.return_value = "Translation failed."

    result = translate_content("Hier ist dein erstes Beispiel.")
    assert result == (False, "Unintelligible")
