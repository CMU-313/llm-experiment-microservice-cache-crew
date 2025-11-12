import os
from flask import Flask
from flask import request, jsonify
from src.translator import translate_content

app = Flask(__name__)

@app.route("/translate")
def translate():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    is_english, translated_content = translate_content(text)
    return jsonify({
        "is_english": bool(is_english),
        "translated_content": translated,
        "classification_confidence": None, 
    }), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
