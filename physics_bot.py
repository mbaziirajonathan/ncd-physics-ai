import os
import requests
import threading
import time
import re
import json
import httpx
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)

# PROXY PATCH FOR GROQ 1.5.0 ON PYTHON 3.14
class NoProxyClient(httpx.Client):
    def __init__(self, *args, **kwargs):
        kwargs.pop('proxies', None)
        super().__init__(*args, **kwargs)

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
    http_client=NoProxyClient()
)

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
    "S3_S4": ["electrostatics", "magnetism", "linear motion", "elasticity", "thermal physics", "waves", "sound", "refraction", "current electricity", "electromagnetism", "transformers", "earth and space", "atomic and nuclear physics"],
    "PRACTICALS": ["density", "conduction", "pinhole camera", "principle of moments", "pulley", "hooke's law", "gas laws", "ripple tank", "resonance tube", "refractive index", "ohm's law", "electromagnet"]
}

DIAGRAM_LIBRARY = {
    "transformer": """<svg width="100%" viewBox="0 0 420 200" style="background:white;border:1px solid #ccc"><text x="210" y="20" text-anchor="middle" font-size="14" font-weight="bold">Simple Transformer - Step Down</text><rect x="180" y="50" width="60" height="100" fill="#8B4513" stroke="black" stroke-width="2"/><text x="210" y="105" text-anchor="middle" fill="white" font-size="10">Iron Core</text><path d="M 120 70 Q 130 70 130 80 Q 130 90 120 90 Q 110 90 110 100 Q 110 110 120 110" fill="none" stroke="red" stroke-width="2"/><path d="M 120 120 Q 130 120 130 130 Q 130 140 120 140 Q 110 140 110 150 Q 110 160 120 160" fill="none" stroke="red" stroke-width="2"/><text x="115" y="65" font-size="10" fill="red">P</text><line x1="100" y1="80" x2="120" y2="80" stroke="red" stroke-width="2"/><line x1="100" y1="150" x2="120" y2="150" stroke="red" stroke-width="2"/><text x="60" y="75" font-size="9">AC Source</text><path d="M 300 70 Q 290 70 290 80 Q 290 90 300 90 Q 310 90 310 100 Q 310 110 300 110" fill="none" stroke="blue" stroke-width="2"/><path d="M 300 120 Q 290 120 290 130 Q 290 140 300 140 Q 310 140 310 150 Q 310 160 300 160" fill="none" stroke="blue" stroke-width="2"/><text x="305" y="65" font-size="10" fill="blue">S</text><line x1="300" y1="80" x2="320" y2="80" stroke="blue" stroke-width="2"/><line x1="300" y1="150" x2="320" y2="150" stroke="blue" stroke-width="2"/><rect x="330" y="75" width="20" height="70" fill="gray"/><text x="340" y="120" font-size="9" text-anchor="middle">Load</text><path d="M 210 50 Q 210 30 150 30" fill="none" stroke="green" stroke-dasharray="3,3"/><path d="M 210 150 Q 210 170 150 170" fill="none" stroke="green" stroke-dasharray="3,3"/></svg>""",
    "convex lens": """<svg width="100%" viewBox="0 0 400 200" style="background:white;border:1px solid #ccc"><text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold">Convex Lens - Object beyond 2F</text><line x1="50" y1="100" x2="350" y2="100" stroke="black"/><path d="M 200 50 Q 215 100 200 150 Q 185 100 200 50" fill="none" stroke="black" stroke-width="2"/><line x1="130" y1="100" x2="130" y2="70" stroke="black" stroke-width="3"/><line x1="270" y1="100" x2="270" y2="130" stroke="black" stroke-width="3"/><text x="130" y="65" font-size="10" text-anchor="middle">Object</text><text x="270" y="145" font-size="10" text-anchor="middle">Image</text></svg>""",
    "pulley": """<svg width="100%" viewBox="0 0 400 200" style="background:white;border:1px solid #ccc"><text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold">Single Fixed Pulley</text><circle cx="200" cy="50" r="30" fill="none" stroke="black" stroke-width="2"/><line x1="170" y1="50" x2="170" y2="150" stroke="black" stroke-width="2" marker-end="url(#arrow)"/><line x1="230" y1="50" x2="230" y2="120" stroke="black" stroke-width="2" marker-end="url(#arrow)"/><rect x="160" y="150" width="20" height="20" fill="gray"/><rect x="220" y="120" width="20" height="20" fill="gray"/></svg>""",
    "ohm's law": """<svg width="100%" viewBox="0 0 400 220" style="background:white;border:1px solid #ccc"><text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold">Ohm's Law Circuit - V = IR</text><line x1="80" y1="100" x2="120" y2="100" stroke="black" stroke-width="2"/><line x1="115" y1="95" x2="125" y2="95" stroke="black" stroke-width="3"/><line x1="115" y1="105" x2="125" y2="105" stroke="black"/><text x="100" y="90" font-size="10">Battery</text><line x1="120" y1="100" x2="160" y2="100" stroke="black" stroke-width="2"/><circle cx="190" cy="100" r="15" fill="white" stroke="black" stroke-width="2"/><text x="190" y="105" text-anchor="middle" font-size="10">A</text><line x1="205" y1="100" x2="250" y2="100" stroke="black" stroke-width="2"/><rect x="280" y1="90" width="40" height="20" fill="white" stroke="black" stroke-width="2"/><text x="300" y="105" text-anchor="middle" font-size="10">R</text><line x1="320" y1="100" x2="340" y2="100" stroke="black" stroke-width="2"/><line x1="340" y1="100" x2="340" y2="160" stroke="black" stroke-width="2"/><line x1="340" y1="160" x2="80" y2="160" stroke="black" stroke-width="2"/><line x1="80" y1="160" x2="80" y2="100" stroke="black" stroke-width="2"/></svg>"""
}

DIAGRAM_TEMPLATES = ["principle of moments", "incline plane", "inclined plane", "v-t graph", "refraction", "wave", "lever", "magnet", "circuit"]

def get_diagram_json(user_msg):
    system_instruction = (
        "CRITICAL: You MUST output ONLY valid JSON. No text. "
        "If 'lever', output: {\"type\": \"Class 1\"} "
        "If 'incline plane', output: {\"angle\": 45, \"mass\": 10} "
        "If 'principle of moments', output: {\"w1\": 10, \"w2\": 20, \"d1\": 80, \"d2\": 40} "
        "If 'v-t graph', output: {\"type\": \"Uniform Acceleration\", \"acc\": 2} "
        "If 'refraction', output: {\"medium\": \"Glass\", \"i\": 40, \"r\": 25} "
        "If 'wave', output: {\"type\": \"Transverse\", \"wl\": 10, \"freq\": 5} "
        "If 'magnet', output: {\"poles\": 2} "
        "If 'circuit', output: {\"v\": 12, \"r\": 4} "
        "OUTPUT ONLY THE JSON OBJECT."
    )
    try:
        response = client.chat.completions.create(
            messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": user_msg}],
            model="llama-3.1-8b-instant", temperature=0.0, max_tokens=120
        )
        json_text = response.choices[0].message.content.replace("```json", "").replace("```", "").strip()
        match = re.search(r'\{.*\}', json_text, re.DOTALL)
        return json.loads(match.group(0)) if match else None
    except Exception as e:
        print("JSON Parse Error:", e)
        return None

def get_diagram_svg(user_msg):
    msg = user_msg.lower()
    keywords = ["draw", "diagram", "graph", "experiment", "illustrate", "sketch", "plot"]
    if not any(k in msg for k in keywords):
        return None, None, None

    # PRIORITY 1: Static SVG with word boundaries to prevent cross-matching
    static_priority = ["transformer", "ohm's law", "pulley", "convex lens"]
    for topic in static_priority:
        if re.search(r'\b' + re.escape(topic) + r'\b', msg):
            return DIAGRAM_LIBRARY[topic], topic, None

    # PRIORITY 2: Dynamic templates with word boundaries
    for topic in DIAGRAM_TEMPLATES:
        if re.search(r'\b' + re.escape(topic) + r'\b', msg):
            json_data = get_diagram_json(user_msg)
            return None, topic, json_data
            
    return None, None, None

HTML = """<!DOCTYPE html><html><head><title>NCD Physics AI - v7.7 Final</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{font-family:Arial;background:#e8f0fe;margin:0;padding:20px}#chat{background:white;padding:20px;border-radius:12px;max-width:700px;margin:auto;box-shadow:0 4px 10px rgba(0,0,0,0.1)}
h2{color:#1a73e8;text-align:center}.badge{background:#1a73e8;color:white;padding:3px 8px;border-radius:5px;font-size:10px;margin-left:5px}
#messages{min-height:300px;max-height:500px;overflow-y:auto;border:1px solid #ddd;padding:10px;border-radius:8px;margin-bottom:10px}
.user{background:#1a73e8;color:white;padding:8px 12px;border-radius:10px;margin:5px 0;text-align:right}.bot{background:#f1f3f4;padding:8px 12px;border-radius:10px;margin:5px 0}
input{width:75%;padding:12px;border:1px solid #ddd;border-radius:8px}button{width:20%;padding:12px;background:#1a73e8;color:white;border:none;border-radius:8px;cursor:pointer}
#canvas-container{margin-top:10px;text-align:center;display:none} svg{max-width:100%;border:1px solid #eee;background:#fff}</style></head><body><div id="chat"><h2>NCD Physics AI - v7.7 Final</h2>
<div id="messages"></div><input id="msg" placeholder="draw lever, draw transformer" onkeypress="if(event.key==='Enter')send()">
<button onclick="send()">Send</button>
<div id="canvas-container"></div>
</div><script>
const TEMPLATES = {
  "incline plane": `<line x1="50" y1="150" x2="350" y2="150" stroke="black" stroke-width="2"/><polygon id="slope" points="50,150 350,150 350,50" fill="#ddd" stroke="black"/><g id="mass-group"><rect x="-20" y="-20" width="40" height="40" fill="gray"/><text x="0" y="5" fill="white" text-anchor="middle" font-size="12"></text></g>`,
  "inclined plane": `<line x1="50" y1="150" x2="350" y2="150" stroke="black" stroke-width="2"/><polygon id="slope" points="50,150 350,150 350,50" fill="#ddd" stroke="black"/><g id="mass-group"><rect x="-20" y="-20" width="40" height="40" fill="gray"/><text x="0" y="5" fill="white" text-anchor="middle" font-size="12"></text></g>`,
  "lever": `<line x1="50" y1="150" x2="350" y2="150" stroke="black" stroke-width="3"/><polygon points="200,150 195,140 205,140" fill="black"/><text x="200" y="165" text-anchor="middle" font-size="10">Fulcrum</text><line id="effort-arrow" x1="320" y1="150" x2="320" y2="120" stroke="green" stroke-width="2" marker-end="url(#arrow)"/><text x="320" y="115" font-size="10" text-anchor="middle">Effort</text><line id="load-arrow" x1="80" y1="150" x2="80" y2="120" stroke="red" stroke-width="2" marker-end="url(#arrow)"/><text x="80" y="115" font-size="10" text-anchor="middle">Load</text><text id="lever-info" x="200" y="30" text-anchor="middle" font-weight="bold"></text>`,
  "principle of moments": `<line x1="50" y1="100" x2="350" y2="100" stroke="black" stroke-width="4"/><polygon points="200,100 195,90 205,90" fill="black"/><text x="200" y="115" text-anchor="middle" font-size="10">Fulcrum</text><line id="w1-line" x1="120" y1="100" x2="120" y2="140" stroke="black" stroke-width="2"/><text id="w1-text" x="120" y="160" font-size="11" text-anchor="middle" font-weight="bold"></text><line id="d1-line" x1="120" y1="105" x2="200" y2="105" stroke="blue" stroke-width="1"/><text id="d1-text" x="160" y="102" font-size="9" text-anchor="middle" fill="blue"></text><line id="w2-line" x1="280" y1="100" x2="280" y2="140" stroke="black" stroke-width="2"/><text id="w2-text" x="280" y="160" font-size="11" text-anchor="middle" font-weight="bold"></text><line id="d2-line" x1="200" y1="105" x2="280" y2="105" stroke="blue" stroke-width="1"/><text id="d2-text" x="240" y="102" font-size="9" text-anchor="middle" fill="blue"></text><text id="moment-check" x="200" y="185" text-anchor="middle" font-size="11" font-weight="bold"></text>`,
  "v-t graph": `<line x1="50" y1="170" x2="350" y2="170" stroke="black"/><line x1="50" y1="170" x2="50" y2="30" stroke="black"/><path id="graph-path" d="" stroke="blue" stroke-width="2" fill="none"/><text x="360" y="175" font-size="12">t</text><text x="30" y="35" font-size="12">v</text><text id="acc-text" x="200" y="190" font-size="10" text-anchor="middle"></text>`,
  "refraction": `<line x1="50" y1="100" x2="350" y2="100" stroke="black"/><line x1="200" y1="40" x2="200" y2="160" stroke="black" stroke-dasharray="2,2"/><text x="200" y="35" text-anchor="middle" font-size="10">Normal</text><text x="200" y="55" text-anchor="middle" font-size="10">Air</text><text x="200" y="155" text-anchor="middle" font-size="10"></text><line id="incident" x1="120" y1="60" x2="200" y2="100" stroke="red" stroke-width="2"/><line id="refracted" x1="200" y1="100" x2="240" y2="140" stroke="red" stroke-width="2"/><text id="angle-text" x="200" y="180" text-anchor="middle" font-size="10"></text>`,
  "wave": `<line x1="50" y1="100" x2="350" y2="100" stroke="gray" stroke-dasharray="3,3"/><text x="355" y="105" font-size="10">X</text><text x="200" y="25" font-size="10" text-anchor="middle">direction of wave propagation</text><path id="wave-path" d="" fill="none" stroke="blue" stroke-width="2"/><line x1="110" y1="100" x2="170" y2="100" stroke="red" stroke-width="2"/><text x="140" y="95" font-size="9" text-anchor="middle" fill="red">λ</text><line x1="110" y1="40" x2="110" y2="100" stroke="green" stroke-width="1" stroke-dasharray="2,2"/><text x="110" y="35" font-size="9" text-anchor="middle" fill="green">A</text><text x="110" y="20" font-size="9" text-anchor="middle">Crest</text><text x="170" y="175" font-size="9" text-anchor="middle">Trough</text><text id="wave-info" x="200" y="190" text-anchor="middle" font-size="11" font-weight="bold"></text>`,
  "magnet": `<rect x="150" y="90" width="100" height="20" fill="red"/><rect x="250" y="90" width="100" height="20" fill="blue"/><text x="200" y="105" text-anchor="middle" font-size="10">N</text><text x="300" y="105" text-anchor="middle" font-size="10">S</text><path d="M 200 90 Q 250 60 300 90" fill="none" stroke="black"/><path d="M 200 110 Q 250 140 300 110" fill="none" stroke="black"/>`,
  "circuit": `<line x1="80" y1="100" x2="120" y2="100" stroke="black" stroke-width="2"/><line x1="115" y1="95" x2="125" y2="95" stroke="black" stroke-width="3"/><line x1="115" y1="105" x2="125" y2="105" stroke="black"/><text x="100" y="90" font-size="10">Battery</text><line x1="120" y1="100" x2="160" y2="100" stroke="black" stroke-width="2"/><circle cx="190" cy="100" r="15" fill="white" stroke="black" stroke-width="2"/><text x="190" y="105" text-anchor="middle" font-size="10">A</text><line x1="205" y1="100" x2="250" y2="100" stroke="black" stroke-width="2"/><rect x="280" y="90" width="40" height="20" fill="white" stroke="black" stroke-width="2"/><text x="300" y="105" text-anchor="middle" font-size="10">R</text><line x1="320" y1="100" x2="340" y2="100" stroke="black" stroke-width="2"/><line x1="340" y1="100" x2="340" y2="160" stroke="black" stroke-width="2"/><line x1="340" y1="160" x2="80" y2="160" stroke="black" stroke-width="2"/><line x1="80" y1="160" x2="80" y2="100" stroke="black" stroke-width="2"/><text id="circuit-info" x="200" y="200" text-anchor="middle" font-size="12" font-weight="bold"></text>`
}
function drawDiagram(name, data) {
    // CRITICAL: Clear old diagram first to prevent transformer bug
    document.getElementById('canvas-container').innerHTML = '<svg id="dynamic-svg" width="400" height="200" viewBox="0 0 400 200"></svg>';
    const svg = document.getElementById('dynamic-svg');
    svg.innerHTML = TEMPLATES[name] + '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs>';
    document.getElementById('canvas-container').style.display = 'block';
    
    if(name === "incline plane" || name === "inclined plane") {
        const angle = Math.max(0, Math.min(75, data.angle || 30)); const rad = angle * Math.PI / 180;
        const topX = 50 + 300 * Math.cos(rad); const topY = 150 - 300 * Math.sin(rad);
        document.getElementById('slope').setAttribute('points', `50,150 350,150 ${topX},${topY}`);
        const midX = (50 + topX)/2; const midY = (150 + topY)/2;
        const posX = midX + 20 * Math.sin(rad); const posY = midY - 20 * Math.cos(rad);
        document.getElementById('mass-group').setAttribute('transform', `translate(${posX}, ${posY}) rotate(${-angle})`);
        document.querySelector('#mass-group text').textContent = (data.mass || 10) + "kg";
    }
    if(name === "lever") { document.getElementById('lever-info').textContent = `Lever: ${data.type || "Class 1"}`; }
    if(name === "principle of moments") {
        const w1 = data.w1 || 10; const w2 = data.w2 || 20; 
        const d1 = data.d1 || 80; const d2 = data.d2 || 40;
        const pos1 = 200 - d1; const pos2 = 200 + d2;
        document.getElementById('w1-line').setAttribute('x1', pos1); document.getElementById('w1-line').setAttribute('x2', pos1);
        document.getElementById('w1-text').setAttribute('x', pos1); document.getElementById('w1-text').textContent = `W1=${w1}N`;
        document.getElementById('d1-line').setAttribute('x1', pos1); document.getElementById('d1-line').setAttribute('x2', 200);
        document.getElementById('d1-text').setAttribute('x', (pos1+200)/2); document.getElementById('d1-text').textContent = `d1=${d1}cm`;
        document.getElementById('w2-line').setAttribute('x1', pos2); document.getElementById('w2-line').setAttribute('x2', pos2);
        document.getElementById('w2-text').setAttribute('x', pos2); document.getElementById('w2-text').textContent = `W2=${w2}N`;
        document.getElementById('d2-line').setAttribute('x1', 200); document.getElementById('d2-line').setAttribute('x2', pos2);
        document.getElementById('d2-text').setAttribute('x', (200+pos2)/2); document.getElementById('d2-text').textContent = `d2=${d2}cm`;
        const m1 = w1 * d1; const m2 = w2 * d2;
        const result = m1 === m2? "IN EQUILIBRIUM" : "NOT BALANCED";
        document.getElementById('moment-check').textContent = `${w1}x${d1} = ${w2}x${d2} → ${m1} = ${m2}Nm → ${result}`;
    }
    if(name === "v-t graph") {
        const type = data.type || "Uniform Acceleration";
        let path = "M 50 170 L 350 50"; if(type.includes("Deceleration")) path = "M 50 50 L 350 170";
        document.getElementById('graph-path').setAttribute('d', path);
        document.getElementById('acc-text').textContent = `a = ${data.acc || 2} m/s²`;
    }
    if(name === "refraction") {
        const i = data.i || 40; const r = data.r || 25;
        const riX = 200 + 60 * Math.sin(r * Math.PI/180); const riY = 100 + 60 * Math.cos(r * Math.PI/180);
        document.getElementById('refracted').setAttribute('x2', riX); document.getElementById('refracted').setAttribute('y2', riY);
        document.querySelector('text[x="200"][y="155"]').textContent = data.medium || "Glass";
        document.getElementById('angle-text').textContent = `i=${i}° r=${r}°`;
    }
    if(name === "wave") {
        const wl = data.wl || 10; const points = `M 50 100 Q ${50+wl} 50 ${50+wl*2} 100 Q ${50+wl*3} 150 ${50+wl*4} 100`;
        document.getElementById('wave-path').setAttribute('d', points);
        document.getElementById('wave-info').textContent = `λ=${wl}cm f=${data.freq||5}Hz`;
    }
    if(name === "circuit") {
        const v = data.v || 12; const r = data.r || 4; const i = (v/r).toFixed(2);
        document.getElementById('circuit-info').textContent = `V=${v}V R=${r}Ω I=${i}A`;
    }
}
async function send(){
    let input=document.getElementById('msg');let text=input.value;if(!text)return;
    document.getElementById('messages').innerHTML+='<div class="user">'+text+'</div>';input.value='';
    let res=await fetch("/",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:text})});
    let data=await res.json();
    document.getElementById('messages').innerHTML+='<div class="bot"><span class="badge">[Physics]</span> '+data.reply+'</div>';
    if(data.json_data && data.template) { drawDiagram(data.template, data.json_data); } 
    else if(data.svg) { document.getElementById('canvas-container').innerHTML = data.svg; document.getElementById('canvas-container').style.display = 'block'; }
    document.getElementById('messages').scrollTop=document.getElementById('messages').scrollHeight;
}
</script></body></html>"""

@app.route("/", methods=["GET"])
def home(): return render_template_string(HTML)

@app.route("/", methods=["POST"])
def chat():
    data = request.json
    user_msg = data.get("message", "")
    svg, template, json_data = get_diagram_svg(user_msg)
    
    system_prompt = f"You are NCD Physics AI for Uganda NCDC S1-S4. Syllabus: {json.dumps(PHYSICS_SYLLABUS)}. Teach ONLY Physics. Max 5 lines. If user asks to draw, tell them diagram is shown below."
    response = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":system_prompt},{"role":"user","content":user_msg}])
    ai_text = response.choices[0].message.content
    return jsonify({"reply": ai_text, "svg": svg, "json_data": json_data, "template": template})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
