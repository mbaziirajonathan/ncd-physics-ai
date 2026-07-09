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

# ========== 15 DIAGRAM LIBRARY - PERFECT UNEB QUALITY ==========
DIAGRAM_LIBRARY = {
    "convex lens": """<svg width="100%" viewBox="0 0 400 200" style="background:white;border:1px solid #ccc"><text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold">Convex Lens - Object beyond 2F</text><line x1="50" y1="100" x2="350" y2="100" stroke="black"/><text x="70" y="90" font-size="10">F</text><text x="130" y="90" font-size="10">2F</text><text x="270" y="90" font-size="10">2F</text><text x="330" y="90" font-size="10">F</text><path d="M 200 50 Q 215 100 200 150 Q 185 100 200 50" fill="none" stroke="black" stroke-width="2"/><text x="200" y="105" text-anchor="middle" font-size="10">Lens</text><line x1="130" y1="100" x2="130" y2="70" stroke="black" stroke-width="3"/><text x="130" y="65" font-size="10" text-anchor="middle">Object</text><line x1="270" y1="100" x2="270" y2="130" stroke="black" stroke-width="3"/><text x="270" y="145" font-size="10" text-anchor="middle">Image</text><line x1="130" y1="70" x2="200" y2="70" stroke="blue" stroke-width="1.5"/><line x1="200" y1="70" x2="270" y2="130" stroke="blue" stroke-width="1.5" marker-end="url(#arrow)"/><line x1="130" y1="70" x2="270" y2="130" stroke="red" stroke-width="1.5" marker-end="url(#arrow)"/><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs></svg>""",
    
    "concave lens": """<svg width="100%" viewBox="0 0 400 200" style="background:white;border:1px solid #ccc"><text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold">Concave Lens</text><line x1="50" y1="100" x2="350" y2="100" stroke="black"/><text x="140" y="90" font-size="10">F</text><text x="260" y="90" font-size="10">F</text><path d="M 200 50 Q 185 100 200 150 Q 215 100 200 50" fill="none" stroke="black" stroke-width="2"/><text x="200" y="105" text-anchor="middle" font-size="10">Lens</text><line x1="120" y1="100" x2="120" y2="70" stroke="black" stroke-width="3"/><text x="120" y="65" font-size="10" text-anchor="middle">Object</text><line x1="160" y1="100" x2="160" y2="80" stroke="black" stroke-width="3"/><text x="160" y="75" font-size="10" text-anchor="middle">Image</text><line x1="120" y1="70" x2="200" y2="70" stroke="blue" stroke-width="1.5"/><line x1="200" y1="70" x2="260" y2="50" stroke="blue" stroke-width="1.5" marker-end="url(#arrow)"/><line x1="120" y1="70" x2="200" y2="100" stroke="red" stroke-width="1.5"/><line x1="200" y1="100" x2="160" y2="80" stroke="red" stroke-width="1.5" marker-end="url(#arrow)"/><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs></svg>""",

    "concave mirror": """<svg width="100%" viewBox="0 0 400 200" style="background:white;border:1px solid #ccc"><text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold">Concave Mirror</text><line x1="50" y1="100" x2="350" y2="100" stroke="black"/><text x="150" y="90" font-size="10">F</text><text x="100" y="90" font-size="10">C</text><path d="M 200 50 Q 250 100 200 150" fill="none" stroke="black" stroke-width="2"/><text x="260" y="105" font-size="10">Mirror</text><line x1="100" y1="100" x2="100" y2="70" stroke="black" stroke-width="3"/><text x="100" y="65" font-size="10" text-anchor="middle">Object</text><line x1="150" y1="100" x2="150" y2="130" stroke="black" stroke-width="3"/><text x="150" y="145" font-size="10" text-anchor="middle">Image</text><line x1="100" y1="70" x2="200" y2="70" stroke="blue" stroke-width="1.5"/><line x1="200" y1="70" x2="150" y2="130" stroke="blue" stroke-width="1.5" marker-end="url(#arrow)"/><line x1="100" y1="70" x2="200" y2="100" stroke="red" stroke-width="1.5"/><line x1="200" y1="100" x2="150" y2="130" stroke="red" stroke-width="1.5" marker-end="url(#arrow)"/><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs></svg>""",

    "pulley": """<svg width="100%" viewBox="0 0 400 200" style="background:white;border:1px solid #ccc"><text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold">Single Fixed Pulley</text><circle cx="200" cy="50" r="30" fill="none" stroke="black" stroke-width="2"/><line x1="170" y1="50" x2="170" y2="150" stroke="black" stroke-width="2" marker-end="url(#arrow)"/><line x1="230" y1="50" x2="230" y2="120" stroke="black" stroke-width="2" marker-end="url(#arrow)"/><rect x="160" y="150" width="20" height="20" fill="gray"/><rect x="220" y="120" width="20" height="20" fill="gray"/><text x="150" y="165" font-size="10">Load</text><text x="210" y="135" font-size="10">Effort</text><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs></svg>""",

    "principle of moments": """<svg width="100%" viewBox="0 0 400 200" style="background:white;border:1px solid #ccc"><text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold">Principle of Moments</text><line x1="50" y1="100" x2="350" y2="100" stroke="black" stroke-width="3"/><polygon points="200,100 195,90 205,90" fill="black"/><text x="200" y="115" text-anchor="middle" font-size="10">Pivot</text><line x1="120" y1="100" x2="120" y2="130" stroke="black" stroke-width="2" marker-end="url(#arrow)"/><text x="120" y="145" font-size="10" text-anchor="middle">W1</text><text x="120" y="90" font-size="10" text-anchor="middle">d1</text><line x1="280" y1="100" x2="280" y2="130" stroke="black" stroke-width="2" marker-end="url(#arrow)"/><text x="280" y="145" font-size="10" text-anchor="middle">W2</text><text x="280" y="90" font-size="10" text-anchor="middle">d2</text><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs></svg>""",

    "v-t graph": """<svg width="100%" viewBox="0 0 400 200" style="background:white;border:1px solid #ccc"><text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold">V-T Graph: Uniform Acceleration</text><line x1="50" y1="170" x2="350" y2="170" stroke="black"/><line x1="50" y1="170" x2="50" y2="30" stroke="black"/><line x1="50" y1="170" x2="350" y2="50" stroke="blue" stroke-width="2"/><text x="360" y="175" font-size="12">t</text><text x="30" y="35" font-size="12">v</text><text x="200" y="190" font-size="10" text-anchor="middle">Time</text><text x="10" y="100" font-size="10" text-anchor="middle">Velocity</text></svg>""",

    "ohm's law": """<svg width="100%" viewBox="0 0 400 200" style="background:white;border:1px solid #ccc"><text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold">Ohm's Law Circuit</text><circle cx="100" cy="100" r="20" fill="white" stroke="black"/><text x="100" y="105" text-anchor="middle" font-size="10">V</text><text x="100" y="130" text-anchor="middle" font-size="10">Voltmeter</text><rect x="180" y="90" width="40" height="20" fill="white" stroke="black"/><text x="200" y="105" text-anchor="middle" font-size="10">R</text><text x="200" y="130" text-anchor="middle" font-size="10">Resistor</text><circle cx="280" cy="100" r="15" fill="white" stroke="black"/><text x="280" y="105" text-anchor="middle" font-size="10">A</text><text x="280" y="125" text-anchor="middle" font-size="10">Ammeter</text><line x1="120" y1="100" x2="180" y2="100" stroke="black"/><line x1="220" y1="100" x2="265" y2="100" stroke="black"/><line x1="295" y1="100" x2="320" y2="100" stroke="black"/><line x1="320" y1="100" x2="320" y2="140" stroke="black"/><line x1="320" y1="140" x2="80" y2="140" stroke="black"/><line x1="80" y1="140" x2="80" y2="100" stroke="black"/></svg>""",

    "electromagnet": """<svg width="100%" viewBox="0 0 400 200" style="background:white;border:1px solid #ccc"><text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold">Electromagnet</text><rect x="150" y="80" width="100" height="40" fill="gray"/><text x="200" y="105" text-anchor="middle" font-size="10">Iron Core</text><path d="M 120 100 Q 150 70 180 100 Q 210 130 240 100 Q 270 70 300 100" fill="none" stroke="red" stroke-width="2"/><text x="310" y="105" font-size="10">Coils</text><circle cx="110" cy="100" r="8" fill="black"/><circle cx="320" cy="100" r="8" fill="black"/><text x="100" y="120" font-size="10">Battery</text></svg>""",

    "refraction": """<svg width="100%" viewBox="0 0 400 200" style="background:white;border:1px solid #ccc"><text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold">Refraction of Light</text><line x1="50" y1="100" x2="350" y2="100" stroke="black"/><text x="200" y="95" text-anchor="middle" font-size="10">Normal</text><text x="200" y="50" text-anchor="middle" font-size="10">Air</text><text x="200" y="150" text-anchor="middle" font-size="10">Glass</text><line x1="120" y1="60" x2="200" y2="100" stroke="red" stroke-width="2" marker-end="url(#arrow)"/><line x1="200" y1="100" x2="240" y2="140" stroke="red" stroke-width="2" marker-end="url(#arrow)"/><text x="130" y="55" font-size="10">Incident</text><text x="250" y="145" font-size="10">Refracted</text><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="red"/></marker></defs></svg>""",

    "ripple tank": """<svg width="100%" viewBox="0 0 400 200" style="background:white;border:1px solid #ccc"><text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold">Ripple Tank</text><rect x="100" y="50" width="200" height="100" fill="lightblue" stroke="black"/><circle cx="200" cy="100" r="10" fill="gray"/><text x="200" y="105" text-anchor="middle" font-size="8">Dipper</text><circle cx="200" cy="100" r="20" fill="none" stroke="blue" stroke-width="1"/><circle cx="200" cy="100" r="35" fill="none" stroke="blue" stroke-width="1"/><circle cx="200" cy="100" r="50" fill="none" stroke="blue" stroke-width="1"/></svg>""",

    "density bottle": """<svg width="100%" viewBox="0 0 400 200" style="background:white;border:1px solid #ccc"><text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold">Density Bottle</text><ellipse cx="200" cy="120" rx="60" ry="80" fill="none" stroke="black" stroke-width="2"/><rect x="180" y="40" width="40" height="20" fill="black"/><text x="200" y="210" text-anchor="middle" font-size="10">Liquid</text></svg>""",

    "gas laws": """<svg width="100%" viewBox="0 0 400 200" style="background:white;border:1px solid #ccc"><text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold">Gas Laws Apparatus</text><rect x="150" y="60" width="100" height="80" fill="lightgray" stroke="black"/><text x="200" y="105" text-anchor="middle" font-size="10">Gas</text><line x1="200" y1="60" x2="200" y2="40" stroke="black" stroke-width="2"/><rect x="190" y="30" width="20" height="10" fill="black"/><text x="200" y="25" text-anchor="middle" font-size="10">Piston</text></svg>""",

    "wave": """<svg width="100%" viewBox="0 0 400 200" style="background:white;border:1px solid #ccc"><text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold">Transverse Wave</text><path d="M 50 100 Q 100 50 150 100 Q 200 150 250 100 Q 300 50 350 100" fill="none" stroke="blue" stroke-width="2"/><line x1="50" y1="100" x2="350" y2="100" stroke="black" stroke-dasharray="2,2"/><text x="200" y="110" text-anchor="middle" font-size="10">Equilibrium</text></svg>""",

    "magnet": """<svg width="100%" viewBox="0 0 400 200" style="background:white;border:1px solid #ccc"><text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold">Bar Magnet Field</text><rect x="150" y="90" width="100" height="20" fill="red"/><rect x="250" y="90" width="100" height="20" fill="blue"/><text x="200" y="105" text-anchor="middle" font-size="10">N</text><text x="300" y="105" text-anchor="middle" font-size="10">S</text><path d="M 200 90 Q 250 60 300 90" fill="none" stroke="black"/><path d="M 200 110 Q 250 140 300 110" fill="none" stroke="black"/></svg>""",

    "hooke's law": """<svg width="100%" viewBox="0 0 400 200" style="background:white;border:1px solid #ccc"><text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold">Hooke's Law Experiment</text><line x1="200" y1="40" x2="200" y2="160" stroke="black" stroke-width="2"/><path d="M 190 60 L 210 60 L 200 80 Z" fill="black"/><text x="200" y="170" text-anchor="middle" font-size="10">Spring</text><rect x="180" y="160" width="40" height="20" fill="gray"/><text x="200" y="190" text-anchor="middle" font-size="10">Weight</text></svg>"""
}

def get_diagram_svg(user_msg):
    msg = user_msg.lower()
    keywords = ["draw", "diagram", "graph", "experiment", "illustrate", "sketch", "plot"]
    if any(k in msg for k in keywords):
        for topic, svg_code in DIAGRAM_LIBRARY.items():
            if topic in msg:
                return svg_code, topic.title()
    return None, None

HTML = """<!DOCTYPE html><html><head><title>NCD Physics AI - NCDC S1-S4</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{font-family:Arial;background:#e8f0fe;margin:0;padding:20px}#chat{background:white;padding:20px;border-radius:12px;max-width:700px;margin:auto;box-shadow:0 4px 10px rgba(0,0,0,0.1)}
h2{color:#1a73e8;text-align:center}.badge{background:#1a73e8;color:white;padding:3px 8px;border-radius:5px;font-size:10px;margin-left:5px}
#messages{min-height:300px;max-height:500px;overflow-y:auto;border:1px solid #ddd;padding:10px;border-radius:8px;margin-bottom:10px}
.user{background:#1a73e8;color:white;padding:8px 12px;border-radius:10px;margin:5px 0;text-align:right}.bot{background:#f1f3f4;padding:8px 12px;border-radius:10px;margin:5px 0}
input{width:75%;padding:12px;border:1px solid #ddd;border-radius:8px}button{width:20%;padding:12px;background:#1a73e8;color:white;border:none;border-radius:8px;cursor:pointer}
button:hover{background:#155ab6}svg{max-width:100%;margin-top:10px;border:1px solid #eee}</style></head><body><div id="chat"><h2>NCD Physics AI - 15 Diagrams Ready</h2>
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
    RULES: Teach ONLY Physics. Give laws, formulas, calculations. Max 5 lines."""
    response = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":system_prompt},{"role":"user","content":user_msg}])
    ai_text = response.choices[0].message.content
    return jsonify({"reply": ai_text, "svg": svg})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
