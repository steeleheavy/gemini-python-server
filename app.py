import os
import base64
import google.generativeai as genai
from flask import Flask, request, jsonify
# Add this import:
from flask_cors import CORS

gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
genai.configure(api_key=gemini_api_key)

app = Flask(__name__)
# Enable CORS for all routes:
CORS(app)

@app.route("/uploadPlate", methods=["POST"])
def upload_plate():
    try:
        data = request.get_json()
        base64_img = data.get("base64")
        prompt = data.get("prompt")
        if not base64_img or not prompt:
            return jsonify({"error": "Missing base64 or prompt"}), 400

        # decode image, save temp.png
        with open("temp.png", "wb") as f:
            f.write(base64.b64decode(base64_img))

        # upload file to gemini
        myfile = genai.upload_file("temp.png", mime_type="image/png")

        # call generate_content
        model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")
        result = model.generate_content([myfile, prompt])

        # remove temp file
        os.remove("temp.png")

        return jsonify({"recognizedPlate": result.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return "Gemini Python server is up!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
