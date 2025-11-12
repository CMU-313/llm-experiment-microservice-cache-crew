import os
from flask import Flask
from flask import request, jsonify
from src.translator import translate_content

app = Flask(__name__)

@app.post("/")
def translate():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")

    # Add in an error check
    if not isinstance(text, str):
        return jsonify({"error": "Invalid payload: 'text' must be a string"}), 400

    is_english, translated_text = translate_content(text)
    return jsonify({
        "is_english": bool(is_english),
        "translated_text": translated_text,
        "classification_confidence": None
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(debug=False, host="0.0.0.0", port=port)