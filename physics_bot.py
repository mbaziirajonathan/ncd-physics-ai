import os
import requests
import threading
import time
import re
import json
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def keep_alive():
    while True:
        try: requests.get("https://ncd-physics-ai.onrender.com/health", timeout=10)
        except: pass
        time.sleep(600)
threading.Thread(target=keep_alive, daemon=True).start()
@app.route("/health")
def health(): return "OK", 200

PHYSICS_SYLLABUS = {
    "S1_S2": ["measurement", "forces", "heat", "light", "moments", "work", "energy", "power", "pressure", "curved mirrors"],
    "S3_S4": ["electrostatics", "magnetism", "linear motion", "elasticity", "thermal physics", "waves", "sound", "refraction", "current electricity", "electromagnetism", "earth and space", "atomic and nuclear physics"],
    "PRACTICALS": ["density", "conduction", "pinhole camera", "principle of moments", "pulley", "hooke's law", "gas laws", "ripple tank", "resonance tube", "refractive index", "ohm's law", "electromagnet"]
}

# ========== DIAGRAM LIBRARY - LOOPED FOR EVERY TOPIC ==========
DIAGRAM_LIBRARY = {
    "convex lens": """<svg width="100%" viewBox="0 0 400 200" style="background:white;border:1px solid #ccc"><text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold">Convex Lens - Object beyond 2F</text><line x1="50" y1="100" x2="350" y2="100" stroke="black"/><text x="340" y="90" font-size="10">F</text><text x="280" y="90" font-size="10">2F</text><text x="120" y="90" font-size="10">2F</text><text x="60" y="90" font-size="10">F</text><path d="M 200 40 Q 220 100 200 160 Q 180 100 200 40" fill="none" stroke="black" stroke-width="2"/><text x="200" y="105" text-anchor="middle" font-size="10">Lens</text><line x1="120" y1="100" x2="120" y2="60" stroke="black" stroke-width="3"/><text x="120" y="55" font-size="10" text-anchor="middle">Object</text><line x1="280" y1="100" x2="280" y2="140" stroke="black" stroke-width="3"/><text x="280" y="155" font-size="10" text-anchor="middle">Image</text><line x1="120" y1="60" x2="200" y2="60" stroke="blue" stroke-width="1.5"/><line x1="200" y1="60" x2="280" y2="140" stroke="blue" stroke-width="1.5" marker-end="url(#arrow)"/><line x1="120" y1="60" x2="280" y2="140" stroke="red" stroke-width="1.5" marker-end="url(#arrow)"/><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs></svg>""",
    
    "concave lens": """<svg width="100%" viewBox="0 0 400 200" style="background:white;border:1px solid #ccc"><text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold">Concave Lens Ray Diagram</text><line x1="50" y1="100" x2="350" y2="100" stroke="black"/><text x="140" y="90" font-size="10">F</text><text x="260" y="90" font-size="10">F</text><path d="M 200 40 Q 180 100 200 160 Q 220 100 200 40" fill="none" stroke="black" stroke-width="2"/><text x="200" y="105" text-anchor="middle" font-size="10">Lens</text><line x1="120" y1="100" x2="120" y2="60" stroke="black" stroke-width="3"/><text x="120" y="55" font-size="10" text-anchor="middle">Object</text><line x1="160" y1="100" x2="160" y2="80" stroke="black" stroke-width="3"/><text x="160" y="75" font-size="10" text-anchor="middle">Image</text><line x1="120" y1="60" x2="200" y2="60" stroke="blue" stroke-width="1.5"/><line x1="200" y1="60" x2="260" y2="40" stroke="blue" stroke-width="1.5" marker-end="url(#arrow)"/><line x1="120" y1="60" x2="200" y2="100" stroke="red" stroke-width="1.5"/><line x1="200" y1="100" x2="160" y2="80" stroke="red" stroke-width="1.5" marker-end="url(#arrow)"/><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs></svg>""",

    "pulley": """<svg width="100%" viewBox="0 0 400 200" style="background:white;border:1px solid #ccc"><text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold">Single Fixed Pulley</text><circle cx="200" cy="50" r="30" fill="none" stroke="black" stroke-width="2"/><line x1="170" y1="50" x2="170" y2="150" stroke="black" stroke-width="2" marker-end="url(#arrow)"/><line x1="230" y1="50" x2="230" y2="120" stroke="black" stroke-width="2" marker-end="url(#arrow)"/><rect x="160" y="150" width="20" height="20" fill="gray"/><rect x="220" y="120" width="20" height="20" fill="gray"/><text x="150" y="165" font-size="10">Load</text><text x="210" y="135" font-size="10">Effort</text><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs></svg>""",

    "v-t graph": """<svg width="100%" viewBox="0 0 400 200" style="background:white;border:1px solid #ccc"><text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold">Velocity-Time Graph: Uniform Velocity</text><line x1="50" y1="170" x2="350" y2="170" stroke="black"/><line x1="50" y1="170" x2="50" y2="30" stroke="black"/><line x1="50" y1="100" x2="350" y2="100" stroke="blue" stroke-width="2"/><text x="360" y="175" font-size="12">t</text><text x="30" y="35" font-size="12">v</text><text x="200" y="190" font-size="10" text-anchor="middle">Time</text><text x="10" y="100" font-size="10" text-anchor="middle">Velocity</text></svg>""",

    "ohm's law": """<svg width="100%" viewBox="0 0 400 200" style="background:white;border:1px solid #ccc"><text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold">Ohm's Law Circuit</text><circle cx="100" cy="100" r="20" fill="white" stroke="black"/><text x="100" y="105" text-anchor="middle" font-size="10">V</text><text x="100" y="130" text-anchor="middle" font-size="10">Voltmeter</text><rect x="180" y="90" width="40" height="20" fill="white" stroke="black"/><text x="200" y="105" text-anchor="middle" font-size="10">R</text><text x="200" y="130" text-anchor="middle" font-size="10">Resistor</text><circle cx="280" cy="100" r="15" fill="white" stroke="black"/><text x="280" y="105" text-anchor="middle" font-size="10">A</text><text x="280" y="125" text-anchor="middle" font-size="10">Ammeter</text><line x1="120" y1="100" x2="180" y2="100" stroke="black"/><line x1="220" y1="100" x2="265" y2="100" stroke="black"/><line x1="295" y1="100" x2="320" y2="100" stroke="black"/><line x1="320" y1="100" x2="320" y2="140" stroke="black"/><line x1="320" y1="140" x2="80" y2="140" stroke="black"/><line x1="80" y1="140" x2="80" y2="100" stroke="black"/></svg>""",

    "principle of moments": """<svg width="100%" viewBox="0 0 400 200" style="background:white;border:1px solid #ccc"><text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold">Principle of Moments</text><line x1="50" y1="100" x2="350" y2="100" stroke="black" stroke-width="3"/><polygon points="200,100 195,90 205,90" fill="black"/><text x="200" y="115" text-anchor="middle" font-size="10">Pivot</text><line x1="120" y1="100" x2="120" y2="130" stroke="black" stroke-width="2" marker-end="url(#arrow)"/><text x="120" y="145" font-size="10" text-anchor="middle">W1</text><text x="120" y="90" font-size="10" text-anchor="middle">d1</text><line x1="280" y1="100" x2="280" y2="130" stroke="black" stroke-width="2" marker-end="url(#arrow)"/><text x="280" y="145" font-size="10" text-anchor="middle">W2</text><text x="280" y="90" font-size="10" text-anchor="middle">d2</text><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs></svg>"""
}

def get_diagram_svg(user_msg):
    msg = user_msg.lower()
    keywords = ["draw", "diagram", "graph", "experiment", "illustrate", "sketch", "plot"]
    
    if any(k in msg for k in keywords):
        # LOOP THROUGH LIBRARY: Check if topic matches any key
        for topic, svg_code in DIAGRAM_LIBRARY.items():
            if topic in msg:
                return svg_code, topic.title()
        
        # IF NOT IN LIBRARY: Ask AI to generate
        return generate_svg_with_ai(user_msg), "AI Generated"
    return None, None

def generate_svg_with_ai(user_msg):
    prompt = f"YOU MUST RETURN ONLY <svg>...</svg>. Draw for NCDC Physics: {user_msg}. White background, viewBox 0 0 400 200, include labels."
    try:
        response = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}], temperature=0.0, max_tokens=700)
        svg_code = response.choices[0].message.content.replace("```svg", "").replace("```", "").strip()
        match = re.search(r'<svg.*?</svg>', svg_code, re.DOTALL)
        return match.group(0) if match else None
    except: return None

HTML = """<!DOCTYPE html><html><head><title>NCD Physics AI - NCDC S1-S4</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{font-family:Arial;background:#e8f0fe;margin:0;padding:20px}#chat{background:white;padding:20px;border-radius:12px;max-width:700px;margin:auto;box-shadow:0 4px 10px rgba(0,0,0,0.1)}
h2{color:#1a73e8;text-align:center}.badge{background:#1a73e8;color:white;padding:3px 8px;border-radius:5px;font-size:10px;margin-left:5px}
#messages{min-height:300px;max-height:500px;overflow-y:auto;border:1px solid #ddd;padding:10px;border-radius:8px;margin-bottom:10px}
.user{background:#1a73e8;color:white;padding:8px 12px;border-radius:10px;margin:5px 0;text-align:right}.bot{background:#f1f3f4;padding:8px 12px;border-radius:10px;margin:5px 0}
input{width:75%;padding:12px;border:1px solid #ddd;border-radius:8px}button{width:20%;padding:12px;background:#1a73e8;color:white;border:none;border-radius:8px;cursor:pointer}
button:hover{background:#155ab6}svg{max-width:100%;margin-top:10px;border:1px solid #eee}</style></head><body><div id="chat"><h2>NCD Physics AI - NCDC S1-S4</h2>
<div id="messages"></div><input id="msg" placeholder="e.g: draw convex lens, draw pulley, draw ohm's law" onkeypress="if(event.key==='Enter')send()">
<button onclick="send()">Send</button></div><script>
async function send(){let input=document.getElementById('msg');let text=input.value;if(!text)return;
document.getElementById('messages').innerHTML+='<div class="user">'+text+'</div>';input.value='';
let res=await fetch("/",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:text})});
let data=await res.json();document.getElementById('messages').innerHTML+='<div class="bot"><span class="badge">[Physics]</span> '+data.reply+(data.svg?data.svg:'')+'</div>';
document.getElementById('messages').scrollTop=document.getElementById('messages').scrollHeight;}</script></body></html>"""

@app.route("/", methods=["GET"])
def home(): return render_template_string(HTML)

@app.route("/", methods=["POST"])
def chat():
    data = request.json
    user_msg = data.get("message", "")
    svg, diagram_name = get_diagram_svg(user_msg)
    
    system_prompt = f"""You are NCD Physics AI for Uganda NCDC S1-S4. Syllabus: {json.dumps(PHYSICS_SYLLABUS)}
    RULES: Teach ONLY Physics. Give laws, formulas, calculations. Max 5 lines. If diagram requested, just explain it."""
    response = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":system_prompt},{"role":"user","content":user_msg}])
    ai_text = response.choices[0].message.content
    return jsonify({"reply": ai_text, "svg": svg})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
