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

# HARDCODED FALLBACKS FOR COMMON DIAGRAMS - THIS FIXES THE BUG
FALLBACK_SVGS = {
    "convex lens": """<svg width="100%" viewBox="0 0 400 200" style="background:white;border:1px solid #ccc"><text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold">Convex Lens Ray Diagram</text><line x1="50" y1="100" x2="350" y2="100" stroke="black"/><circle cx="200" cy="100" r="40" fill="none" stroke="black" stroke-width="2"/><text x="200" y="105" text-anchor="middle" font-size="10">Lens</text><line x1="150" y1="100" x2="150" y2="60" stroke="black" stroke-width="3"/><text x="150" y="55" font-size="10">Object</text><line x1="250" y1="100" x2="250" y2="140" stroke="black" stroke-width="3"/><text x="250" y="155" font-size="10">Image</text><line x1="150" y1="60" x2="200" y2="100" stroke="blue" marker-end="url(#arrow)"/><line x1="200" y1="100" x2="250" y2="140" stroke="blue" marker-end="url(#arrow)"/><text x="100" y="100" font-size="10">F</text><text x="300" y="100" font-size="10">F</text><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="blue"/></marker></defs></svg>""",
    "pulley": """<svg width="100%" viewBox="0 0 400 200" style="background:white;border:1px solid #ccc"><text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold">Pulley Experiment</text><circle cx="200" cy="50" r="30" fill="none" stroke="black" stroke-width="2"/><line x1="170" y1="50" x2="170" y2="150" stroke="black" stroke-width="2" marker-end="url(#arrow)"/><line x1="230" y1="50" x2="230" y2="120" stroke="black" stroke-width="2" marker-end="url(#arrow)"/><rect x="160" y="150" width="20" height="20" fill="gray"/><rect x="220" y="120" width="20" height="20" fill="gray"/><text x="150" y="165" font-size="10">Load</text><text x="210" y="135" font-size="10">Effort</text><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs></svg>""",
    "v-t graph": """<svg width="100%" viewBox="0 0 400 200" style="background:white;border:1px solid #ccc"><text x="200" y="20" text-anchor="middle" font-size="14" font-weight="bold">Velocity-Time Graph</text><line x1="50" y1="170" x2="350" y2="170" stroke="black"/><line x1="50" y1="170" x2="50" y2="30" stroke="black"/><line x1="50" y1="100" x2="350" y2="100" stroke="blue" stroke-width="2"/><text x="360" y="175" font-size="12">t</text><text x="30" y="35" font-size="12">v</text><text x="200" y="190" font-size="10" text-anchor="middle">Time</text><text x="10" y="100" font-size="10" text-anchor="middle">Velocity</text></svg>"""
}

FORCE_SVG_RULES = """
YOU MUST RETURN ONLY A VALID <svg>...</svg> TAG. NO TEXT.
Draw for NCDC Physics: "{user_msg}"
Rules: white background, viewBox 0 0 400 200, include labels and arrows.
"""

def generate_svg_with_ai(user_msg):
    msg = user_msg.lower()
    # STEP 1: CHECK FALLBACK FIRST
    for key in FALLBACK_SVGS:
        if key in msg: return FALLBACK_SVGS[key]
    
    # STEP 2: ASK AI
    prompt = FORCE_SVG_RULES.format(user_msg=user_msg)
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[{"role": "user", "content": prompt}], 
            temperature=0.0,
            max_tokens=700
        )
        svg_code = response.choices[0].message.content
        svg_code = svg_code.replace("```svg", "").replace("```", "").strip()
        match = re.search(r'<svg.*?</svg>', svg_code, re.DOTALL)
        return match.group(0) if match else None
    except: return None

def get_diagram_svg(user_msg):
    msg = user_msg.lower()
    keywords = ["draw", "diagram", "graph", "experiment", "illustrate", "sketch"]
    if any(k in msg for k in keywords):
        return generate_svg_with_ai(user_msg), "Physics Diagram"
    return None, None

HTML = """<!DOCTYPE html><html><head><title>NCD Physics AI - NCDC S1-S4</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>body{font-family:Arial;background:#e8f0fe;margin:0;padding:20px}#chat{background:white;padding:20px;border-radius:12px;max-width:700px;margin:auto;box-shadow:0 4px 10px rgba(0,0,0,0.1)}
h2{color:#1a73e8;text-align:center}.badge{background:#1a73e8;color:white;padding:3px 8px;border-radius:5px;font-size:10px;margin-left:5px}
#messages{min-height:300px;max-height:500px;overflow-y:auto;border:1px solid #ddd;padding:10px;border-radius:8px;margin-bottom:10px}
.user{background:#1a73e8;color:white;padding:8px 12px;border-radius:10px;margin:5px 0;text-align:right}.bot{background:#f1f3f4;padding:8px 12px;border-radius:10px;margin:5px 0}
input{width:75%;padding:12px;border:1px solid #ddd;border-radius:8px}button{width:20%;padding:12px;background:#1a73e8;color:white;border:none;border-radius:8px;cursor:pointer}
button:hover{background:#155ab6}svg{max-width:100%;margin-top:10px;border:1px solid #eee}</style></head><body><div id="chat"><h2>NCD Physics AI - NCDC S1-S4</h2>
<div id="messages"></div><input id="msg" placeholder="e.g: draw pulley experiment, draw V-T graph, ohm's law" onkeypress="if(event.key==='Enter')send()">
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
    RULES: Teach ONLY Physics. Give laws, formulas, calculations. Max 5 lines. If diagram requested, just explain it. SVG is handled separately."""
    response = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":system_prompt},{"role":"user","content":user_msg}])
    ai_text = response.choices[0].message.content
    return jsonify({"reply": ai_text, "svg": svg})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
