import os
import requests
import threading
import time
import re
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ========== KEEP ALIVE FOR RENDER ==========
def keep_alive():
    while True:
        try: requests.get("https://ncd-physics-ai.onrender.com/health", timeout=10)
        except: pass
        time.sleep(600)

def startup_ping():
    time.sleep(15)
    try: requests.get("https://ncd-physics-ai.onrender.com/health", timeout=10)
    except: pass

threading.Thread(target=keep_alive, daemon=True).start()
threading.Thread(target=startup_ping, daemon=True).start()

@app.route("/health")
def health():
    return "OK", 200

# ========== QC PASSED: 7 UNEB STANDARD HARDCODED DIAGRAMS ==========
def svg_lever(): return """<svg width="100%" viewBox="0 0 400 200" style="background:white;border-radius:8px"><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs><line x1="50" y1="100" x2="350" y2="100" stroke="black" stroke-width="3"/><polygon points="200,100 190,120 210,120" fill="gray"/><text x="200" y="140" text-anchor="middle" font-size="12">Fulcrum</text><line x1="100" y1="100" x2="100" y2="60" stroke="red" stroke-width="3" marker-end="url(#arrow)"/><text x="100" y="50" text-anchor="middle" fill="red" font-size="12">Effort</text><line x1="300" y1="100" x2="300" y2="50" stroke="blue" stroke-width="3" marker-end="url(#arrow)"/><text x="300" y="40" text-anchor="middle" fill="blue" font-size="12">Load</text><text x="200" y="25" text-anchor="middle" font-size="16" font-weight="bold">Class 1 Lever</text></svg>"""

def svg_incline(): return """<svg width="100%" viewBox="0 0 400 230" style="background:white;border-radius:8px"><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs><polygon points="50,200 350,200 350,100" fill="#d2b48c" stroke="black" stroke-width="2"/><rect x="180" y="140" width="40" height="30" fill="#8b4513" stroke="black"/><line x1="200" y1="155" x2="200" y2="120" stroke="black" stroke-width="2" marker-end="url(#arrow)"/><text x="210" y="135" font-size="12">W</text><line x1="200" y1="155" x2="170" y2="155" stroke="black" stroke-width="2" marker-end="url(#arrow)"/><text x="150" y="160" font-size="12">F</text><line x1="200" y1="155" x2="200" y2="185" stroke="black" stroke-width="2" marker-end="url(#arrow)"/><text x="210" y="195" font-size="12">R</text><text x="200" y="30" text-anchor="middle" font-size="16" font-weight="bold">Inclined Plane - Forces</text></svg>"""

def svg_ohm(): return """<svg width="100%" viewBox="0 0 400 200" style="background:white;border-radius:8px"><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs><text x="50" y="90" font-weight="bold" font-size="14">+</text><rect x="60" y="80" width="50" height="20" fill="#ffe066" stroke="black" stroke-width="2"/><text x="85" y="70" text-anchor="middle" font-size="10">Battery</text><line x1="110" y1="90" x2="140" y2="90" stroke="black" stroke-width="2" marker-end="url(#arrow)"/><rect x="140" y="80" width="50" height="20" fill="white" stroke="black" stroke-width="2"/><text x="165" y="70" text-anchor="middle" font-size="10">Ammeter A</text><line x1="190" y1="90" x2="220" y2="90" stroke="black" stroke-width="2" marker-end="url(#arrow)"/><rect x="220" y="80" width="50" height="20" fill="white" stroke="black" stroke-width="2"/><text x="245" y="70" text-anchor="middle" font-size="10">Resistor R</text><line x1="270" y1="90" x2="300" y2="90" stroke="black" stroke-width="2" marker-end="url(#arrow)"/><rect x="300" y="80" width="50" height="20" fill="white" stroke="black" stroke-width="2"/><text x="325" y="70" text-anchor="middle" font-size="10">Voltmeter V</text><polyline points="350,90 350,130 50,130 50,100" fill="none" stroke="black" stroke-width="2" marker-end="url(#arrow)"/><text x="50" y="150" font-weight="bold" font-size="14">-</text><text x="200" y="25" text-anchor="middle" font-size="16" font-weight="bold">Series Circuit: Ohm's Law V=IR</text></svg>"""

def svg_prism(): return """<svg width="100%" viewBox="0 0 400 200" style="background:white;border-radius:8px"><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="white"/></marker></defs><polygon points="100,150 300,150 250,50 150,50" fill="#add8e6" stroke="black" stroke-width="2"/><line x1="50" y1="100" x2="150" y2="80" stroke="white" stroke-width="3" marker-end="url(#arrow)"/><line x1="150" y1="80" x2="250" y2="120" stroke="red" stroke-width="2"/><line x1="150" y1="80" x2="250" y2="100" stroke="orange" stroke-width="2"/><line x1="150" y1="80" x2="250" y2="90" stroke="yellow" stroke-width="2"/><line x1="150" y1="80" x2="250" y2="80" stroke="green" stroke-width="2"/><line x1="150" y1="80" x2="250" y2="70" stroke="blue" stroke-width="2"/><line x1="150" y1="80" x2="250" y2="60" stroke="indigo" stroke-width="2"/><line x1="150" y1="80" x2="250" y2="50" stroke="violet" stroke-width="2"/><text x="200" y="25" text-anchor="middle" font-size="16" font-weight="bold">Triangular Prism - Dispersion</text></svg>"""

def svg_convex(): return """<svg width="100%" viewBox="0 0 400 200" style="background:white;border-radius:8px"><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs><line x1="50" y1="100" x2="350" y2="100" stroke="black" stroke-width="1"/><ellipse cx="200" cy="100" rx="10" ry="80" fill="none" stroke="black" stroke-width="2"/><line x1="100" y1="130" x2="100" y2="70" stroke="red" stroke-width="3"/><text x="100" y="160" text-anchor="middle" font-size="12">Object</text><line x1="300" y1="80" x2="300" y2="120" stroke="blue" stroke-width="3"/><text x="300" y="60" text-anchor="middle" font-size="12">Real Image</text><text x="150" y="90" text-anchor="middle" font-size="12">F</text><text x="250" y="90" text-anchor="middle" font-size="12">F</text><line x1="100" y1="100" x2="200" y2="100" x2="300" y2="100" stroke="orange" stroke-width="1.5" stroke-dasharray="3,3" marker-end="url(#arrow)"/><line x1="100" y1="70" x2="200" y2="100" x2="300" y2="120" stroke="green" stroke-width="1.5" marker-end="url(#arrow)"/><text x="200" y="25" text-anchor="middle" font-size="16" font-weight="bold">Convex Lens - Real Image</text></svg>"""

def svg_concave(): return """<svg width="100%" viewBox="0 0 400 200" style="background:white;border-radius:8px"><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs><line x1="50" y1="100" x2="350" y2="100" stroke="black" stroke-width="1"/><path d="M 190 20 Q 200 100 190 180" fill="none" stroke="black" stroke-width="2"/><path d="M 210 20 Q 200 100 210 180" fill="none" stroke="black" stroke-width="2"/><line x1="100" y1="130" x2="100" y2="70" stroke="red" stroke-width="3"/><text x="100" y="160" text-anchor="middle" font-size="12">Object</text><line x1="50" y1="80" x2="50" y2="120" stroke="blue" stroke-width="3" stroke-dasharray="5,5"/><text x="50" y="60" text-anchor="middle" font-size="12">Virtual Image</text><text x="150" y="90" text-anchor="middle" font-size="12">F</text><text x="250" y="90" text-anchor="middle" font-size="12">F</text><line x1="100" y1="70" x2="200" y2="100" stroke="green" stroke-width="1.5" marker-end="url(#arrow)"/><line x1="200" y1="100" x2="250" y2="70" stroke="green" stroke-width="1.5" stroke-dasharray="3,3"/><line x1="100" y1="130" x2="200" y2="100" stroke="orange" stroke-width="1.5" marker-end="url(#arrow)"/><line x1="200" y1="100" x2="250" y2="130" stroke="orange" stroke-width="1.5" stroke-dasharray="3,3"/><text x="200" y="25" text-anchor="middle" font-size="16" font-weight="bold">Concave Lens - Virtual Image</text></svg>"""

def svg_transformer(): return """<svg width="100%" viewBox="0 0 400 200" style="background:white;border-radius:8px"><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs><rect x="120" y="50" width="40" height="100" fill="gray" stroke="black"/><text x="140" y="40" text-anchor="middle" font-size="10">Primary N1</text><rect x="240" y="50" width="40" height="100" fill="gray" stroke="black"/><text x="260" y="40" text-anchor="middle" font-size="10">Secondary N2</text><path d="M 100 70 Q 110 70 110 90 Q 100 90 100 110" stroke="red" fill="none" stroke-width="2"/><path d="M 100 80 Q 110 80 110 100 Q 100 100 100 120" stroke="red" fill="none" stroke-width="2"/><path d="M 300 70 Q 290 70 290 90 Q 300 90 300 110" stroke="blue" fill="none" stroke-width="2"/><path d="M 300 80 Q 290 80 290 100 Q 300 100 300 120" stroke="blue" fill="none" stroke-width="2"/><line x1="90" y1="90" x2="100" y2="90" stroke="red" stroke-width="2" marker-end="url(#arrow)"/><text x="80" y="95" font-size="10">Vin</text><line x1="300" y1="90" x2="310" y2="90" stroke="blue" stroke-width="2" marker-end="url(#arrow)"/><text x="315" y="95" font-size="10">Vout</text><text x="200" y="25" text-anchor="middle" font-size="16" font-weight="bold">Step-up Transformer</text></svg>"""

# ========== FULL NCDC S1-S4 SYLLABUS - THEORY + PRACTICAL ==========
SYLLABUS = """THEORY S1-S4: Measurement, Forces, Heat, Light, Kinetic Theory, Moments, Work Energy Power, Pressure, Curved Mirrors, Electrostatics, Magnetism, Linear Motion, Elasticity, Thermal Physics, Waves, Sound, Refraction, Current Electricity, Electromagnetism, Earth Space, Atomic Nuclear.
PRACTICAL S1-S4: Laboratory Safety, Density, Conduction, Convection, Radiation, Pinhole Camera, Reflection, Principle of Moments, Centre of Gravity, Pulley, Inclined Plane, Atmospheric Pressure, Gold Leaf Electroscope, Magnetic Field Lines, Hooke's Law, Thermometer Calibration, Gas Laws, Ripple Tank, Resonance Tube, Refractive Index, Ohm's Law, Resistivity, Electromagnet, Transformer, Half-life Simulation."""

def generate_svg_with_ai(user_msg):
    prompt = f"""You are an SVG generator for Uganda NCDC S1-S4 Physics THEORY and PRACTICAL.
    Full Syllabus: {SYLLABUS}
    Task: Generate clean, UNEB standard SVG diagram for: "{user_msg}"
    Rules: 1. Only if topic is in S1-S4 syllabus. Else return "null" 2. Use viewBox="0 0 400 200". White background with border-radius 3. Include labels and ARROWS using <marker id="arrow"> 4. For practical, show apparatus setup with labels 5. Simple, max 30 lines 6. Return ONLY <svg>...</svg> code, no explanation."""
    try:
        response = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}], temperature=0.1, max_tokens=700)
        svg_code = response.choices[0].message.content
        match = re.search(r'<svg.*?</svg>', svg_code, re.DOTALL)
        return match.group(0) if match else None
    except: return None

def get_diagram_svg(user_msg):
    msg = user_msg.lower()
    # QC Layer 1: 7 Perfect Hardcoded Diagrams
    if "lever" in msg: return svg_lever(), "Class 1 Lever"
    if "incline" in msg: return svg_incline(), "Inclined Plane"
    if "ohm" in msg or "series circuit" in msg: return svg_ohm(), "Series Circuit"
    if "prism" in msg: return svg_prism(), "Triangular Prism"
    if "convex" in msg and "lens" in msg: return svg_convex(), "Convex Lens"
    if "concave" in msg and "lens" in msg: return svg_concave(), "Concave Lens"
    if "transformer" in msg: return svg_transformer(), "Transformer"
    # QC Layer 2: AI generates any other S1-S4 Theory or Practical
    if "draw" in msg or "diagram" in msg or "illustration" in msg or "practical" in msg or "experiment" in msg:
        ai_svg = generate_svg_with_ai(user_msg)
        if ai_svg: return ai_svg, "AI Generated Diagram"
    return None, None

HTML = """<!DOCTYPE html><html><head><title>NCD Physics AI - NCDC S1-S4</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{font-family:Arial;background:#e8f0fe;margin:0;padding:20px}#chat{background:white;padding:20px;border-radius:12px;max-width:700px;margin:auto;box-shadow:0 4px 10px rgba(0,0,0,0.1)}
h2{color:#1a73e8;text-align:center}#messages{min-height:300px;max-height:500px;overflow-y:auto;border:1px solid #ddd;padding:10px;border-radius:8px;margin-bottom:10px}
.user{background:#1a73e8;color:white;padding:8px 12px;border-radius:10px;margin:5px 0;text-align:right}.bot{background:#f1f3f4;padding:8px 12px;border-radius:10px;margin:5px 0}
input{width:75%;padding:12px;border:1px solid #ddd;border-radius:8px}button{width:20%;padding:12px;background:#1a73e8;color:white;border:none;border-radius:8px;cursor:pointer}
button:hover{background:#155ab6}svg{max-width:100%;margin-top:10px}</style></head><body><div id="chat"><h2>NCD Physics AI - NCDC S1-S4 Theory + Practical</h2>
<div id="messages"></div><input id="msg" placeholder="e.g: draw pulley experiment, draw ohm's law practical" onkeypress="if(event.key==='Enter')send()">
<button onclick="send()">Send</button></div><script>
async function send(){let input=document.getElementById('msg');let text=input.value;if(!text)return;
document.getElementById('messages').innerHTML+='<div class="user">'+text+'</div>';input.value='';
let res=await fetch("/",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:text})});
let data=await res.json();document.getElementById('messages').innerHTML+='<div class="bot">'+data.reply+(data.svg?data.svg:'')+'</div>';
document.getElementById('messages').scrollTop=document.getElementById('messages').scrollHeight;}</script></body></html>"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML)

@app.route("/", methods=["POST"])
def chat():
    data = request.json
    user_msg = data.get("message", "")
    svg, diagram_name = get_diagram_svg(user_msg)
    system_prompt = f"""You are NCD Physics AI for Uganda NCDC S1-S4. Full Syllabus: {SYLLABUS}
    Rules: 1. Teach ONLY S1-S4 topics. If not in syllabus say: 'This topic is not in NCDC S1-S4 Physics' then explain briefly.
    2. For practical questions give: Apparatus, Method, Precautions, Observation for UNEB P3.
    3. Describe any diagram in UNEB exam style. 4. Be concise and use Ugandan examples."""
    response = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":system_prompt},{"role":"user","content":user_msg}])
    ai_text = response.choices[0].message.content
    return jsonify({"reply": ai_text, "svg": svg, "diagram": diagram_name})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
