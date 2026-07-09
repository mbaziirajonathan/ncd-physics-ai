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

# ========== NCDC S1-S4 PHYSICS SYLLABUS ONLY ==========
PHYSICS_SYLLABUS = {
    "S1_S2": ["measurement", "forces", "heat", "light", "moments", "work", "energy", "power", "pressure", "curved mirrors"],
    "S3_S4": ["electrostatics", "magnetism", "linear motion", "elasticity", "thermal physics", "waves", "sound", "refraction", "current electricity", "electromagnetism", "earth and space", "atomic and nuclear physics"],
    "PRACTICALS": ["density", "conduction", "pinhole camera", "principle of moments", "pulley", "hooke's law", "gas laws", "ripple tank", "resonance tube", "refractive index", "ohm's law", "electromagnet"]
}

# ========== FORCE AI TO DRAW SVG - PHYSICS ONLY ==========
FORCE_SVG_RULES = """
YOU ARE AN SVG GENERATOR FOR UGANDAN NCDC S1-S4 PHYSICS.
CRITICAL: YOU MUST RETURN ONLY A VALID <svg>...</svg> TAG. NO TEXT, NO EXPLANATION.

SVG RULES:
1. <svg width="100%" viewBox="0 0 400 250" style="background:white;border-radius:8px">
2. Include <defs><marker id="arrow"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs>
3. FOR GRAPHS: Draw X-axis, Y-axis with labels, plot line/curve, add Title. e.g V-T graph, I-V graph
4. FOR DIAGRAMS: Label all parts. Use arrows for forces, current, light rays
5. FOR PRACTICALS: Show apparatus setup with labels
6. End with </svg>

TOPIC TO DRAW: "{user_msg}"
SYLLABUS: {syllabus}
"""

def generate_svg_with_ai(user_msg):
    prompt = FORCE_SVG_RULES.format(user_msg=user_msg, syllabus=json.dumps(PHYSICS_SYLLABUS))
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[{"role": "user", "content": prompt}], 
            temperature=0.0, # FORCE IT TO FOLLOW RULES
            max_tokens=900
        )
        svg_code = response.choices[0].message.content
        svg_code = svg_code.replace("```svg", "").replace("```", "").strip()
        match = re.search(r'<svg.*?</svg>', svg_code, re.DOTALL)
        return match.group(0) if match else None
    except Exception as e: 
        print("SVG Error:", e)
        return None

def get_diagram_svg(user_msg):
    msg = user_msg.lower()
    keywords = ["draw", "diagram", "graph", "experiment", "illustrate", "sketch", "plot"]
    if any(k in msg for k in keywords):
        ai_svg = generate_svg_with_ai(user_msg)
        if ai_svg: return ai_svg, "Physics Diagram"
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
    
    system_prompt = f"""You are NCD Physics AI for Uganda NCDC S1-S4. 
    Syllabus: {json.dumps(PHYSICS_SYLLABUS)}
    
    RULES: 
    1. Teach ONLY Physics. If asked other subjects, say "I only teach Physics".
    2. Give laws, formulas, calculations, and step-by-step solutions.
    3. For practicals: give Apparatus, Method, Precautions, Observation.
    4. For diagrams: explain what the diagram shows in 2 lines. SVG is handled separately.
    5. Be concise. UNEB exam style. Max 6 lines.
    """
    response = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":system_prompt},{"role":"user","content":user_msg}])
    ai_text = response.choices[0].message.content
    return jsonify({"reply": ai_text, "svg": svg})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
