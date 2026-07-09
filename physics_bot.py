import os
import requests
import threading
import time
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ========== KEEP ALIVE FOR RENDER ==========
def keep_alive():
    while True:
        try:
            requests.get("https://ncd-physics-ai.onrender.com/health", timeout=10)
        except:
            pass
        time.sleep(600)

def startup_ping():
    time.sleep(15)
    try:
        requests.get("https://ncd-physics-ai.onrender.com/health", timeout=10)
    except:
        pass

threading.Thread(target=keep_alive, daemon=True).start()
threading.Thread(target=startup_ping, daemon=True).start()

# ========== HEALTH ROUTE ==========
@app.route("/health")
def health():
    return "OK", 200

# ========== SVG DIAGRAM FUNCTIONS ==========
def svg_lever():
    return """<svg width="100%" viewBox="0 0 400 200" style="background:white;border-radius:8px">
<line x1="50" y1="100" x2="350" y2="100" stroke="black" stroke-width="3"/>
<polygon points="200,100 190,120 210,120" fill="gray"/>
<line x1="100" y1="100" x2="100" y2="60" stroke="red" stroke-width="3"/>
<line x1="300" y1="100" x2="300" y2="50" stroke="blue" stroke-width="3"/>
<text x="200" y="25" text-anchor="middle" font-size="18" font-weight="bold">Lever - Fulcrum in Center</text></svg>"""

def svg_incline():
    return """<svg width="100%" viewBox="0 0 400 230" style="background:white;border-radius:8px">
<polygon points="50,200 350,200 350,100" fill="#d2b48c" stroke="black" stroke-width="2"/>
<rect x="180" y="140" width="40" height="30" fill="#8b4513" stroke="black"/>
<line x1="200" y1="155" x2="200" y2="120" stroke="black" stroke-width="2"/>
<line x1="200" y1="155" x2="170" y2="155" stroke="black" stroke-width="2"/>
<line x1="200" y1="155" x2="200" y2="185" stroke="black" stroke-width="2"/>
<text x="200" y="30" text-anchor="middle" font-size="18" font-weight="bold">Inclined Plane</text></svg>"""

def svg_ohm():
    return """<svg width="100%" viewBox="0 0 400 200" style="background:white;border-radius:8px">
<text x="50" y="90" font-weight="bold">+</text>
<rect x="60" y="80" width="50" height="20" fill="#ffe066" stroke="black" stroke-width="2"/><text x="85" y="94" text-anchor="middle">Battery</text>
<line x1="110" y1="90" x2="140" y2="90" stroke="black" stroke-width="2"/>
<rect x="140" y="80" width="50" height="20" fill="white" stroke="black" stroke-width="2"/><text x="165" y="94" text-anchor="middle">A</text>
<line x1="190" y1="90" x2="220" y2="90" stroke="black" stroke-width="2"/>
<rect x="220" y="80" width="50" height="20" fill="white" stroke="black" stroke-width="2"/><text x="245" y="94" text-anchor="middle">R</text>
<line x1="270" y1="90" x2="300" y2="90" stroke="black" stroke-width="2"/>
<rect x="300" y="80" width="50" height="20" fill="white" stroke="black" stroke-width="2"/><text x="325" y="94" text-anchor="middle">V</text>
<polyline points="350,90 350,130 50,130 50,100" fill="none" stroke="black" stroke-width="2"/>
<text x="50" y="150" font-weight="bold">-</text>
<text x="200" y="25" text-anchor="middle" font-size="18" font-weight="bold">Series Circuit: Ohm's Law</text></svg>"""

def svg_prism():
    return """<svg width="100%" viewBox="0 0 400 200" style="background:white;border-radius:8px">
<polygon points="100,150 300,150 250,50 150,50" fill="#add8e6" stroke="black" stroke-width="2"/>
<line x1="50" y1="100" x2="150" y2="80" stroke="red" stroke-width="2"/>
<line x1="250" y1="120" x2="350" y2="140" stroke="violet" stroke-width="2"/>
<text x="200" y="25" text-anchor="middle" font-size="18" font-weight="bold">Triangular Prism - Dispersion</text></svg>"""

def svg_convex():
    return """<svg width="100%" viewBox="0 0 400 200" style="background:white;border-radius:8px">
<line x1="50" y1="100" x2="350" y2="100" stroke="black" stroke-width="1"/>
<ellipse cx="200" cy="100" rx="10" ry="80" fill="none" stroke="black" stroke-width="2"/>
<line x1="100" y1="130" x2="100" y2="70" stroke="red" stroke-width="3"/><text x="100" y="150" text-anchor="middle">Object</text>
<line x1="300" y1="80" x2="300" y2="120" stroke="blue" stroke-width="3"/><text x="300" y="150" text-anchor="middle">Image</text>
<text x="150" y="90" text-anchor="middle">F</text><text x="250" y="90" text-anchor="middle">F</text>
<text x="200" y="25" text-anchor="middle" font-size="18" font-weight="bold">Convex Lens</text></svg>"""

def svg_concave():
    return """<svg width="100%" viewBox="0 0 400 200" style="background:white;border-radius:8px">
<line x1="50" y1="100" x2="350" y2="100" stroke="black" stroke-width="1"/>
<path d="M 190 20 Q 200 100 190 180" fill="none" stroke="black" stroke-width="2"/>
<path d="M 210 20 Q 200 100 210 180" fill="none" stroke="black" stroke-width="2"/>
<line x1="100" y1="130" x2="100" y2="70" stroke="red" stroke-width="3"/><text x="100" y="150" text-anchor="middle">Object</text>
<line x1="50" y1="80" x2="50" y2="120" stroke="blue" stroke-width="3" stroke-dasharray="5,5"/><text x="50" y="150" text-anchor="middle">Virtual Image</text>
<text x="150" y="90" text-anchor="middle">F</text><text x="250" y="90" text-anchor="middle">F</text>
<text x="200" y="25" text-anchor="middle" font-size="18" font-weight="bold">Concave Lens</text></svg>"""

def svg_transformer():
    return """<svg width="100%" viewBox="0 0 400 200" style="background:white;border-radius:8px">
<rect x="120" y="50" width="40" height="100" fill="gray" stroke="black"/>
<rect x="240" y="50" width="40" height="100" fill="gray" stroke="black"/>
<path d="M 100 70 Q 110 70 110 90 Q 100 90 100 110" stroke="red" fill="none" stroke-width="2"/>
<path d="M 100 80 Q 110 80 110 100 Q 100 100 100 120" stroke="red" fill="none" stroke-width="2"/>
<path d="M 300 70 Q 290 70 290 90 Q 300 90 300 110" stroke="blue" fill="none" stroke-width="2"/>
<path d="M 300 80 Q 290 80 290 100 Q 300 100 300 120" stroke="blue" fill="none" stroke-width="2"/>
<text x="130" y="40" text-anchor="middle">N1</text><text x="260" y="40" text-anchor="middle">N2</text>
<text x="100" y="140" text-anchor="middle">Vin</text><text x="300" y="140" text-anchor="middle">Vout</text>
<text x="200" y="25" text-anchor="middle" font-size="18" font-weight="bold">Step-up Transformer</text></svg>"""

# ========== DIAGRAM DETECTION ==========
def get_diagram_svg(user_msg):
    msg = user_msg.lower()
    if any(k in msg for k in ["lever"]): return svg_lever(), "Lever"
    if any(k in msg for k in ["incline", "inclined plane"]): return svg_incline(), "Inclined Plane"
    if any(k in msg for k in ["ohm", "circuit", "series circuit"]): return svg_ohm(), "Series Circuit"
    if any(k in msg for k in ["prism"]): return svg_prism(), "Triangular Prism"
    if any(k in msg for k in ["convex lens", "convex"]): return svg_convex(), "Convex Lens"
    if any(k in msg for k in ["concave lens", "concave"]): return svg_concave(), "Concave Lens"
    if any(k in msg for k in ["transformer"]): return svg_transformer(), "Transformer"
    return None, None

# ========== HTML FRONTEND ==========
HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>NCD Physics AI</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {font-family:Arial; background:#e8f0fe; margin:0; padding:20px}
    #chat {background:white; padding:20px; border-radius:12px; max-width:700px; margin:auto; box-shadow:0 4px 10px rgba(0,0,0,0.1)}
    h2 {color:#1a73e8; text-align:center}
    #messages {min-height:300px; max-height:500px; overflow-y:auto; border:1px solid #ddd; padding:10px; border-radius:8px; margin-bottom:10px}
   .user {background:#1a73e8; color:white; padding:8px 12px; border-radius:10px; margin:5px 0; text-align:right}
   .bot {background:#f1f3f4; padding:8px 12px; border-radius:10px; margin:5px 0}
    input {width:75%; padding:12px; border:1px solid #ddd; border-radius:8px}
    button {width:20%; padding:12px; background:#1a73e8; color:white; border:none; border-radius:8px; cursor:pointer}
    button:hover {background:#155ab6}
    svg {max-width:100%; margin-top:10px}
  </style>
</head>
<body>
  <div id="chat">
    <h2>NCD Physics AI - S1 to S4</h2>
    <div id="messages"></div>
    <input id="msg" placeholder="e.g: draw convex lens, explain ohm's law" onkeypress="if(event.key==='Enter')send()">
    <button onclick="send()">Send</button>
  </div>

<script>
async function send(){
  let input = document.getElementById('msg');
  let text = input.value;
  if(!text) return;
  document.getElementById('messages').innerHTML += '<div class="user">'+text+'</div>';
  input.value = '';
  
  let res = await fetch("/", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({message: text})
  });
  let data = await res.json();
  document.getElementById('messages').innerHTML += '<div class="bot">'+data.reply + (data.svg? data.svg : '') + '</div>';
  document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
}
</script>
</body>
</html>
"""

# ========== ROUTES ==========
@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML)

@app.route("/", methods=["POST"])
def chat():
    data = request.json
    user_msg = data.get("message", "")
    
    svg, diagram_name = get_diagram_svg(user_msg)
    
    system_prompt = """You are NCD Physics AI for Uganda NCDC S1-S4.
    Rules:
    1. If topic is in NCDC S1-S4, answer and teach it.
    2. If topic is NOT in syllabus, say: 'This topic is not in NCDC S1-S4 Physics' then briefly explain anyway.
    3. For diagrams requested, describe them in text too for UNEB.
    4. Be concise, use Ugandan examples where possible."""
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg}
        ]
    )
    
    ai_text = response.choices[0].message.content
    
    return jsonify({"reply": ai_text, "svg": svg, "diagram": diagram_name})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
