import os, json
from flask import Flask, render_template_string, request, jsonify
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

with open("ncdc_physics.json", "r", encoding="utf-8") as f:
    db = json.load(f)

SYSTEM_PROMPT = """You are a NCDC Uganda S1-S4 Physics AI Tutor. Answer clearly using UNEB syllabus."""

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "ncdc_secret")

HTML = """<!DOCTYPE html>
<html>
<head><title>NCDC Physics AI</title>
<style>body{font-family:Arial;padding:20px;max-width:700px;margin:auto;background:#f5f5f5} #chat{border:1px solid #ccc;padding:10px;height:400px;overflow-y:scroll;margin-bottom:10px;background:white} input{width:75%;padding:10px} button{padding:10px 20px;background:#2563eb;color:white;border:none}</style>
</head>
<body>
<h1>NCDC Physics S1-S4 AI Tutor</h1>
<div id="chat"></div>
<input id="q" placeholder="Ask a physics question...">
<button onclick="send()">Ask</button>
<script>
async function send(){
  let q = document.getElementById('q').value;
  if(!q) return;
  let chat = document.getElementById('chat');
  chat.innerHTML += '<b>You:</b> ' + q + '<br>';
  let res = await fetch('/ask', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({q:q})});
  let data = await res.json();
  chat.innerHTML += '<b>AI:</b> ' + data.a + '<br><br>';
  document.getElementById('q').value='';
  chat.scrollTop = chat.scrollHeight;
}
</script>
</body></html>"""

@app.route("/")
def home(): 
    return render_template_string(HTML)

@app.route("/ask", methods=["POST"])
def ask():
    q = request.json["q"]
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":q}]
    )
    return jsonify({"a": resp.choices[0].message.content})

if __name__ == "__main__": 
    app.run(host="0.0.0.0", port=10000)
