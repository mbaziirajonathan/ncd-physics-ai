import os, json
from flask import Flask, render_template_string, request, jsonify
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

with open("ncdc_physics.json", "r", encoding="utf-8") as f:
    db = json.load(f)

SYSTEM_PROMPT = f"""You are a NCDC Uganda S1-S4 Physics Tutor..."""
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "ncdc_strict_key_2025")
HTML = """<!DOCTYPE html>..."""
@app.route("/")
def home(): return render_template_string(HTML)
@app.route("/ask", methods=["POST"])
def ask():
    q = request.json["q"]
    resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": q}], temperature=0.1, max_tokens=500)
    return jsonify({"a": resp.choices[0].message.content})
if __name__ == "__main__": app.run(host="0.0.0.0", port=5000)
