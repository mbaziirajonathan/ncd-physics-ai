import os
import time
import threading
import httpx
from flask import Flask, request, jsonify, render_template_string
from groq import Groq
import re

app = Flask(__name__)

# --- CONFIG & SYSTEM PROMPT ---
SYSTEM_PROMPT = "You are NCD Physics AI. Provide concise, accurate physics explanations based on the 2026 NCDC syllabus."

# --- UNIVERSAL SVG ENGINE ---
def generate_universal_svg(topic):
    return f'''<svg width="100%" viewBox="0 0 420 240" xmlns="http://www.w3.org/2000/svg" style="font-family:Arial">
    <rect width="420" height="240" fill="#f0f8ff" stroke="#004a99" stroke-width="3" rx="10"/>
    <text x="210" y="35" text-anchor="middle" font-size="16" font-weight="bold" fill="#004a99">NCDC DIAGRAM: {topic}</text>
    
    <rect x="60" y="60" width="300" height="90" fill="white" stroke="#004a99" stroke-width="2" rx="8"/>
    <text x="210" y="90" text-anchor="middle" font-size="14" fill="#333">{topic}</text>
    <text x="210" y="110" text-anchor="middle" font-size="11" fill="#666">Conceptual Representation</text>
    
    <line x1="210" y1="150" x2="120" y2="190" stroke="#28a745" stroke-width="2"/>
    <line x1="210" y1="150" x2="210" y2="190" stroke="#28a745" stroke-width="2"/>
    <line x1="210" y1="150" x2="300" y2="190" stroke="#28a745" stroke-width="2"/>
    <circle cx="120" cy="190" r="8" fill="#28a745"/><text x="120" y="210" text-anchor="middle" font-size="10">Label 1</text>
    <circle cx="210" cy="190" r="8" fill="#28a745"/><text x="210" y="210" text-anchor="middle" font-size="10">Label 2</text>
    <circle cx="300" cy="190" r="8" fill="#28a745"/><text x="300" y="210" text-anchor="middle" font-size="10">Label 3</text>
    
    <text x="210" y="230" text-anchor="middle" font-size="9" fill="red">* Ask "draw {topic.lower()} with labels" for details</text>
    </svg>'''

def get_diagram_svg(user_message):
    msg = user_message.lower()
    print(f"[DEBUG PLAN B] Input: {msg}")

    if not any(k in msg for k in ["draw", "diagram", "show", "illustrate", "experiment"]):
        return None, None

    # Extract topic
    words = re.sub(r'draw|diagram|show|illustrate|experiment|a|an|the|of', '', msg).strip()
    topic = words if words else "PHYSICS CONCEPT"
    topic_title = topic.upper()

    print(f"[DEBUG PLAN B] Generating universal SVG for: {topic_title}")
    svg = generate_universal_svg(topic_title)
    return svg, topic

# --- ROUTES ---
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get("message", "")
        svg, topic = get_diagram_svg(user_message)
        
        # Simple AI response
        ai_reply = f"Here is the conceptual diagram for {topic or 'your topic'}. I can provide more details if you ask for labels."
        
        return jsonify({"reply": ai_reply, "svg": svg})
    except Exception as e:
        return jsonify({"reply": "Error", "svg": None}), 500

# --- FRONTEND ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: sans-serif; padding: 10px; background: #f4f4f4; }
        .card {background:white; margin:10px; padding:15px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.1); width:calc(100% - 20px); box-sizing:border-box; overflow:visible}
        #canvas-container {width:100%; min-height:240px; display:flex; align-items:center; justify-content:center; overflow-x:auto; padding:5px}
        #canvas-container svg {width:100%!important; height:auto!important; max-width:100%}
        input { width: 70%; padding: 10px; }
    </style>
</head>
<body>
    <div id="chat"></div>
    <input id="msg" placeholder="Ask: draw motor">
    <button onclick="send()">Send</button>

    <script>
    async function send(){
        let m = document.getElementById('msg').value;
        let res = await fetch('/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message:m})});
        let data = await res.json();
        let chat = document.getElementById('chat');
        chat.innerHTML += `<div class="card">${data.reply}</div>`;
        if(data.svg) {
            chat.innerHTML += `<div class="card"><div id="canvas-container">${data.svg}</div></div>`;
        }
    }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
