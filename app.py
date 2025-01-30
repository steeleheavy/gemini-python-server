import os
import base64
import google.generativeai as genai
from flask import Flask, request, jsonify

# Configure your Gemini key from environment variable
gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
if not gemini_api_key:
    print("WARNING: No GEMINI_API_KEY set in environment! Using placeholder...")

genai.configure(api_key=gemini_api_key)

app = Flask(__name__)

@app.route("/uploadPlate", methods=["POST"])
def upload_plate():
    try:
        data = request.get_json()
        base64_img = data.get("base64")
        prompt = data.get("prompt")
        if not base64_img or not prompt:
            return jsonify({"error": "Missing base64 or prompt"}), 400

        # 1) Decode the base64 image -> write temp file
        filename = "temp.png"
        with open(filename, "wb") as f:
            f.write(base64.b64decode(base64_img))

        # 2) Upload the file to gemini
        myfile = genai.upload_file(filename, mime_type="image/png")

        # 3) Use the gemini model to generate content
        #    e.g. gemini-2.0-flash-exp
        model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")

        # Build an array: [myfile, prompt], per the docs
        # The library automatically references the file's content
        result = model.generate_content([myfile, prompt])

        # Optionally remove the temp file from local disk
        os.remove(filename)

        return jsonify({"recognizedPlate": result.text})
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

# A simple test route
@app.route("/")
def index():
    return "Gemini Python server is up!"

# For local dev (Render will override with $PORT)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
