import os
from flask import Flask, request, jsonify
from src.translator import translate_content

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def translate():
    if request.method == "GET":
        # browser-friendly: /?content=Bonjour%20tout%20le%20monde!
        text = request.args.get("content", "", type=str)
    else:
        # JSON POST: {"text": "..."}
        data = request.get_json(silent=True) or {}
        text = data.get("text", "")

    if not isinstance(text, str):
        return jsonify({"error": "Invalid payload: text/content must be a string"}), 400

    is_english, translated_text = translate_content(text)
    return jsonify({
        "is_english": bool(is_english),
        "translated_text": translated_text,
        "classification_confidence": None
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(debug=False, host="0.0.0.0", port=port)