import os
import re
import time
import threading
import httpx
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

# ==============================================================================
# NCD Physics AI Tutor - Uganda UNEB / NCDC Syllabus 2026 S1-S4
# FINAL V8.4 - RENDER DEPLOYMENT HOTFIX (Error Handling & Timeout)
# ==============================================================================

app = Flask(__name__)

# --- 1. CORE RULES ---
SYSTEM_PROMPT = """
You are NCD Physics AI. You are an UNEB/NCDC Physics Examiner from Uganda.
STRICT RULES:
1.  SYLLABUS SCOPE: You ONLY teach topics in NCDC Physics Syllabus 2026 S1-S4. 
2.  If asked outside syllabus: "That topic is not in the NCDC 2026 Physics Syllabus. I can help with: [list 3 related topics]"
3.  CALCULATIONS: For UNEB past papers, ALWAYS use G=10N/kg. Answer in 3 steps: 
    Step 1: Write Formula
    Step 2: Substitute values 
    Step 3: Final Answer = ... with correct SI units
4.  PAST PAPERS: When explaining, quote the concept as it appears in UNEB marking guide.
5.  VISUAL AID RULE: If the student question contains "draw", "show", "diagram", "illustrate", "experiment", "how does it look", you MUST generate a diagram description or acknowledge the illustration provided.
6.  EXPLANATION RULE: For every concept, give 1. Definition 2. Formula if any 3. UNEB Example 4. Real life application. Max 6 lines.
7.  ANTI-HALLUCINATION: Only use NCDC 2026 S1-S4 Physics Syllabus. If experiment not in syllabus, say: "This experiment is not in NCDC 2026. Related syllabus experiment: [name]"
"""

# --- 2. TECHNICAL SETUP ---
http_client = httpx.Client(proxies=None)
groq_api_key = os.environ.get("GROQ_API_KEY", "dummy_key_for_dev") 
try:
    groq_client = Groq(api_key=groq_api_key, http_client=http_client)
except Exception:
    groq_client = None

def keep_alive():
    while True:
        try:
            httpx.get("http://127.0.0.1:5000/health", timeout=5)
        except Exception:
            pass
        time.sleep(600)
threading.Thread(target=keep_alive, daemon=True).start()

# --- 3. AUTO-ILLUSTRATION ENGINE ---
def generate_fallback_svg(topic_name):
    topic = topic_name.upper()
    return f'''<svg width="100%" viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg" style="background:#f9f9f9;border:2px dashed #004a99;border-radius:8px">
    <text x="200" y="40" text-anchor="middle" font-size="15" font-weight="bold" fill="#004a99">Conceptual Diagram: {topic}</text>
    <rect x="80" y="70" width="240" height="70" fill="#fff" stroke="#004a99" stroke-width="2" rx="8"/>
    <text x="200" y="100" text-anchor="middle" font-size="12" fill="#333">NCDC 2026 Physics</text>
    <text x="200" y="120" text-anchor="middle" font-size="11" fill="#666">Ask: "draw with labels" for details</text>
    <text x="200" y="160" text-anchor="middle" font-size="10" fill="red">Diagram not in library yet</text>
    </svg>'''

CONFIG = {
    "transformer": {"theory": "A transformer steps up or steps down alternating current (a.c) voltages."},
    "pulley": {"theory": "A single fixed pulley changes the direction of the effort applied, VR = 1."},
    "convex lens": {"theory": "A convex lens converges parallel rays of light to a principal focus."},
    "ohm's law": {"theory": "Ohm's Law: Current through a conductor is proportional to p.d across it."},
    "principle of moments": {"theory": "For a body in equilibrium, sum of clockwise moments = sum of anticlockwise moments."},
    "incline plane": {"theory": "An inclined plane reduces the effort needed by increasing distance moved."},
    "v-t graph": {"theory": "The area under a velocity-time graph gives the total distance covered."},
    "refraction": {"theory": "Snell's Law: The ratio of sin i to sin r is constant for a given pair of media."},
    "wave": {"theory": "A transverse wave has crests and troughs, vibrating perpendicular to wave travel."},
    "magnet": {"theory": "Magnetic field lines run from the North pole to the South pole."},
    "lever": {"theory": "In a Class 1 lever, the fulcrum is situated between the Load and the Effort."},
    "motor": {"theory": "Converts electrical energy to mechanical energy via Fleming's Left-Hand Rule."},
    "generator": {"theory": "Converts mechanical energy to electrical energy via Electromagnetic Induction."},
    "galvanometer": {"theory": "An instrument for detecting and measuring small electric currents."},
    "circuit": {"theory": "A closed loop path through which electric current can flow."},
    "density": {"theory": "Density = Mass / Volume. SI Unit: kg/m³."},
    "conduction": {"theory": "Heat transfer by vibrating particles in a solid."},
    "pinhole camera": {"theory": "Demonstrates rectilinear propagation (light travels in straight lines)."},
    "hooke's law": {"theory": "Extension of a spring is directly proportional to applied force (F = kx)."},
    "electromagnet": {"theory": "Current flowing through a coil produces a temporary magnetic field."},
    "ripple tank": {"theory": "Used to demonstrate wave reflection, refraction, and diffraction in the lab."}
}

DIAGRAM_LIBRARY = {
    "transformer": '''<svg viewBox="0 0 300 200" xmlns="http://www.w3.org/2000/svg"><rect x="50" y="30" width="200" height="140" fill="none" stroke="#666" stroke-width="20" rx="10"/><path d="M 40 50 Q 10 90 40 130" fill="none" stroke="blue" stroke-width="3"/><path d="M 40 60 Q 10 100 40 140" fill="none" stroke="blue" stroke-width="3"/><path d="M 40 70 Q 10 110 40 150" fill="none" stroke="blue" stroke-width="3"/><text x="10" y="45" font-family="Arial" font-size="12">P</text><path d="M 260 80 Q 290 100 260 120" fill="none" stroke="red" stroke-width="3"/><path d="M 260 90 Q 290 110 260 130" fill="none" stroke="red" stroke-width="3"/><text x="280" y="75" font-family="Arial" font-size="12">S</text><rect x="290" y="90" width="10" height="20" fill="black"/><text x="290" y="125" font-family="Arial" font-size="10">Load</text><text x="120" y="100" font-family="Arial" font-size="14">Iron Core</text></svg>''',
    "pulley": '''<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"><line x1="100" y1="20" x2="100" y2="60" stroke="black" stroke-width="3"/><circle cx="100" cy="80" r="20" fill="none" stroke="black" stroke-width="3"/><line x1="80" y1="80" x2="80" y2="150" stroke="black" stroke-width="2"/><line x1="120" y1="80" x2="120" y2="120" stroke="black" stroke-width="2"/><rect x="65" y="150" width="30" height="30" fill="gray"/><text x="65" y="195" font-family="Arial" font-size="12">Load</text><text x="110" y="135" font-family="Arial" font-size="12">Effort</text><path d="M 120 120 L 115 110 L 125 110 Z" fill="black"/></svg>''',
    "convex lens": '''<svg viewBox="0 0 420 200" xmlns="http://www.w3.org/2000/svg"><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="red" /></marker></defs><text x="210" y="25" text-anchor="middle" font-size="12" font-weight="bold">Convex Lens - Parallel Rays</text><line x1="40" y1="110" x2="380" y2="110" stroke="black" stroke-dasharray="4,2"/><text x="370" y="105" font-size="9">Principal Axis</text><path d="M 210 20 Q 240 110 210 200 Q 180 110 210 20 Z" fill="lightblue" opacity="0.5" stroke="blue"/><circle cx="210" cy="110" r="3" fill="black"/><text x="215" y="115" font-size="9">O</text><circle cx="110" cy="110" r="3" fill="black"/><text x="100" y="105" font-size="9">2F</text><circle cx="310" cy="110" r="3" fill="black"/><text x="300" y="105" font-size="9">2F</text><circle cx="310" cy="110" r="5" fill="black"/><text x="320" y="115" font-size="10" font-weight="bold">F</text><path d="M40 60 L210 60 L310 110" stroke="red" stroke-width="2" marker-end="url(#arrow)"/><path d="M40 160 L210 160 L310 110" stroke="red" stroke-width="2" marker-end="url(#arrow)"/></svg>''',
    "ohm's law": '''<svg viewBox="0 0 300 200" xmlns="http://www.w3.org/2000/svg"><line x1="50" y1="50" x2="250" y2="50" stroke="black" stroke-width="2"/><line x1="50" y1="50" x2="50" y2="150" stroke="black" stroke-width="2"/><line x1="250" y1="50" x2="250" y2="150" stroke="black" stroke-width="2"/><line x1="50" y1="150" x2="100" y2="150" stroke="black" stroke-width="2"/><line x1="150" y1="150" x2="250" y2="150" stroke="black" stroke-width="2"/><line x1="130" y1="40" x2="130" y2="60" stroke="black" stroke-width="3"/><line x1="145" y1="30" x2="145" y2="70" stroke="black" stroke-width="3"/><circle cx="250" cy="100" r="15" fill="white" stroke="black" stroke-width="2"/><text x="245" y="105" font-family="Arial" font-size="14">A</text><path d="M 100 150 L 105 140 L 115 160 L 125 140 L 135 160 L 145 140 L 150 150" fill="none" stroke="black" stroke-width="2"/><line x1="90" y1="150" x2="90" y2="180" stroke="black" stroke-width="2"/><line x1="160" y1="150" x2="160" y2="180" stroke="black" stroke-width="2"/><line x1="90" y1="180" x2="110" y2="180" stroke="black" stroke-width="2"/><line x1="140" y1="180" x2="160" y2="180" stroke="black" stroke-width="2"/><circle cx="125" cy="180" r="15" fill="white" stroke="black" stroke-width="2"/><text x="120" y="185" font-family="Arial" font-size="14">V</text></svg>''',
    "incline plane": '''<svg viewBox="0 0 300 200" xmlns="http://www.w3.org/2000/svg"><polygon points="50,150 250,150 250,50" fill="none" stroke="black" stroke-width="2"/><rect x="120" y="90" width="40" height="30" transform="rotate(26.5 140 105)" fill="lightgray" stroke="black"/><line x1="140" y1="115" x2="140" y2="170" stroke="red" stroke-width="2"/><polygon points="140,175 137,165 143,165" fill="red"/><text x="145" y="170" font-family="Arial" font-size="12">W</text><line x1="140" y1="115" x2="115" y2="65" stroke="blue" stroke-width="2"/><polygon points="112,60 110,70 120,68" fill="blue"/><text x="100" y="65" font-family="Arial" font-size="12">R</text><line x1="140" y1="115" x2="190" y2="90" stroke="green" stroke-width="2"/><polygon points="195,87 185,87 190,95" fill="green"/><text x="195" y="85" font-family="Arial" font-size="12">F</text><text x="210" y="145" font-family="Arial" font-size="12">θ</text></svg>''',
    "v-t graph": '''<svg viewBox="0 0 300 200" xmlns="http://www.w3.org/2000/svg"><line x1="40" y1="20" x2="40" y2="160" stroke="black" stroke-width="2"/><line x1="40" y1="160" x2="280" y2="160" stroke="black" stroke-width="2"/><path d="M 40 160 L 100 60 L 200 60 L 250 160" fill="none" stroke="blue" stroke-width="3"/><text x="10" y="20" font-family="Arial" font-size="12">V(m/s)</text><text x="270" y="180" font-family="Arial" font-size="12">t(s)</text></svg>''',
    "refraction": '''<svg viewBox="0 0 300 200" xmlns="http://www.w3.org/2000/svg"><line x1="30" y1="100" x2="270" y2="100" stroke="black" stroke-width="3"/><line x1="150" y1="20" x2="150" y2="180" stroke="gray" stroke-dasharray="4,4"/><line x1="70" y1="20" x2="150" y2="100" stroke="red" stroke-width="2"/><path d="M 110 60 L 100 65 L 105 55 Z" fill="red"/><line x1="150" y1="100" x2="190" y2="180" stroke="blue" stroke-width="2"/><path d="M 170 140 L 165 130 L 175 135 Z" fill="blue"/><path d="M 150 70 A 30 30 0 0 0 120 70" fill="none" stroke="black"/><text x="135" y="60" font-family="Arial" font-size="12">i</text><path d="M 150 130 A 30 30 0 0 1 165 130" fill="none" stroke="black"/><text x="155" y="145" font-family="Arial" font-size="12">r</text><text x="40" y="90" font-family="Arial" font-size="12">Air</text><text x="40" y="120" font-family="Arial" font-size="12">Glass</text></svg>''',
    "wave": '''<svg viewBox="0 0 300 200" xmlns="http://www.w3.org/2000/svg"><line x1="20" y1="100" x2="280" y2="100" stroke="black" stroke-dasharray="2,2"/><path d="M 40 100 Q 70 20 100 100 T 160 100 T 220 100 T 280 100" fill="none" stroke="blue" stroke-width="3"/><line x1="100" y1="100" x2="100" y2="50" stroke="red" stroke-width="2"/><text x="105" y="80" font-family="Arial" font-size="12" fill="red">A</text><line x1="40" y1="30" x2="160" y2="30" stroke="green" stroke-width="2"/><text x="95" y="25" font-family="Arial" font-size="12" fill="green">λ</text></svg>''',
    "magnet": '''<svg viewBox="0 0 300 200" xmlns="http://www.w3.org/2000/svg"><rect x="100" y="80" width="100" height="40" fill="none" stroke="black" stroke-width="2"/><rect x="100" y="80" width="50" height="40" fill="red"/><rect x="150" y="80" width="50" height="40" fill="blue"/><text x="115" y="105" font-family="Arial" font-size="16" fill="white">N</text><text x="175" y="105" font-family="Arial" font-size="16" fill="white">S</text><path d="M 125 80 Q 150 30 175 80" fill="none" stroke="black" stroke-dasharray="4,4"/><path d="M 125 120 Q 150 170 175 120" fill="none" stroke="black" stroke-dasharray="4,4"/><path d="M 110 80 Q 150 0 190 80" fill="none" stroke="black" stroke-dasharray="4,4"/><path d="M 110 120 Q 150 200 190 120" fill="none" stroke="black" stroke-dasharray="4,4"/></svg>''',
    "lever": '''<svg viewBox="0 0 300 200" xmlns="http://www.w3.org/2000/svg"><line x1="50" y1="100" x2="250" y2="100" stroke="black" stroke-width="6"/><polygon points="150,100 130,140 170,140" fill="gray" stroke="black"/><rect x="50" y="60" width="40" height="40" fill="brown" stroke="black"/><text x="55" y="85" font-family="Arial" font-size="12" fill="white">Load</text><line x1="230" y1="50" x2="230" y2="100" stroke="blue" stroke-width="3"/><polygon points="230,100 220,90 240,90" fill="blue"/><text x="240" y="70" font-family="Arial" font-size="12">Effort</text></svg>''',
    "motor": generate_fallback_svg("MOTOR"),
    "generator": generate_fallback_svg("GENERATOR"),
    "circuit": generate_fallback_svg("CIRCUIT"),
    "galvanometer": generate_fallback_svg("GALVANOMETER")
}

def get_diagram_svg(user_message):
    msg = user_message.lower()
    if not any(k in msg for k in ["draw", "diagram", "show", "illustrate", "experiment"]):
        return None, None, {}

    for topic in DIAGRAM_LIBRARY:
        if topic in msg:
            theory = CONFIG.get(topic, {}).get("theory", "")
            return DIAGRAM_LIBRARY[topic], topic, {"theory": theory, "extra_text": ""}

    words = re.sub(r'draw|diagram|show|illustrate|experiment', '', msg).strip()
    fallback_topic = words if words else "PHYSICS CONCEPT"
    
    return generate_fallback_svg(fallback_topic), fallback_topic, {"theory": f"Conceptual Diagram representing {fallback_topic}.", "extra_text": ""}


# --- 4. FRONTEND HTML + CSS + JS ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NCD Physics AI Tutor - Uganda</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; }
        #app-container { width: 100%; max-width: 900px; background: #fff; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); overflow: hidden; display: flex; flex-direction: column; height: 90vh; }
        .header { background: #0056b3; color: white; padding: 15px; text-align: center; }
        .header h1 { margin: 0; font-size: 1.5rem; }
        
        .main-content { display: flex; flex: 1; overflow: hidden; }
        @media (max-width: 768px) {
            .main-content { flex-direction: column; }
            #theory-panel { border-left: none; border-top: 2px solid #e0e0e0; flex: 0.8 !important; }
        }
        
        .card { width: 100%; max-width: 100%; box-sizing: border-box; overflow: visible; padding: 10px; margin-top: 10px; background: white; border: 1px solid #ccc; border-radius: 5px; text-align: center; }
        #canvas-container { width: 100%; min-height: 200px; overflow-x: auto; }
        svg { width: 100% !important; height: auto !important; max-width: 100%; }
        
        #chat-window { flex: 2; padding: 20px; overflow-y: auto; background: #fafafa; border-right: 1px solid #ddd; }
        .message { margin-bottom: 15px; padding: 10px 15px; border-radius: 8px; max-width: 90%; line-height: 1.4; word-wrap: break-word; }
        .user-msg { background: #007bff; color: white; align-self: flex-end; margin-left: auto; border-bottom-right-radius: 0; }
        .ai-msg { background: #e9ecef; color: #333; align-self: flex-start; margin-right: auto; border-bottom-left-radius: 0; }
        
        #theory-panel { flex: 1; padding: 20px; background: #fdfdfd; overflow-y: auto; border-left: 2px solid #e0e0e0; }
        #theory { font-size: 0.95rem; color: #333; line-height: 1.6; }
        
        .diagram-theory { margin-top: 10px; font-weight: bold; font-size: 0.9em; color: #0056b3; }
        .diagram-extra { margin-top: 5px; font-size: 0.85em; color: #d9534f; font-weight: bold; }
        
        .input-area { display: flex; padding: 15px; background: #fff; border-top: 1px solid #ddd; }
        #user-input { flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 5px; font-size: 1rem; }
        #send-btn { margin-left: 10px; padding: 10px 20px; border: none; background: #28a745; color: white; border-radius: 5px; cursor: pointer; font-size: 1rem; }
        .loader { display: none; margin: 10px auto; border: 4px solid #f3f3f3; border-top: 4px solid #0056b3; border-radius: 50%; width: 20px; height: 20px; animation: spin 1s linear infinite; }
        @keyframes spin { 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>

<div id="app-container">
    <div class="header">
        <h1>NCD Physics AI Tutor</h1>
        <p>Uganda UNEB Past Papers & NCDC 2026 Syllabus (S1-S4) | v8.4</p>
    </div>
    
    <div class="main-content">
        <div id="chat-window">
            <div class="message ai-msg">Welcome! I can solve UNEB questions, explain topics, and <b>draw diagrams</b> on demand. Try asking: "draw a motor" or "UNEB 2019 Q3".</div>
        </div>
        
        <div id="theory-panel">
            <h3>UNEB Concept Board</h3>
            <div id="theory"><i>Explanations and formulas will appear here...</i></div>
        </div>
    </div>
    
    <div class="loader" id="loader"></div>
    
    <div class="input-area">
        <input type="text" id="user-input" placeholder="Ask a physics question or say 'draw [topic]'..." onkeypress="handleKeyPress(event)">
        <button id="send-btn" onclick="sendMessage()">Send</button>
    </div>
</div>

<script>
    const chatWindow = document.getElementById('chat-window');
    const userInput = document.getElementById('user-input');
    const loader = document.getElementById('loader');

    function handleKeyPress(e) { if (e.key === 'Enter') sendMessage(); }

    function appendMessage(text, isUser) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message ' + (isUser ? 'user-msg' : 'ai-msg');
        msgDiv.innerHTML = text.replace(/\\n/g, '<br>');
        chatWindow.appendChild(msgDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        return msgDiv;
    }
    
    function showExplanation(text) {
        document.getElementById("theory").innerHTML = "<b>UNEB Explanation:</b><br><br>" + text.replace(/\\n/g, '<br>');
    }
    
    function drawDiagram(container, diagramData) {
        try {
            if (!diagramData || !diagramData.svg) throw new Error("No SVG data");
            const diagDiv = document.createElement('div');
            diagDiv.className = 'card';
            
            const svgWrapper = document.createElement('div');
            svgWrapper.id = 'canvas-container';
            svgWrapper.innerHTML = diagramData.svg;
            
            const theoryDiv = document.createElement('div');
            theoryDiv.className = 'diagram-theory';
            theoryDiv.innerText = diagramData.theory || "";
            
            diagDiv.appendChild(svgWrapper);
            if (diagramData.extra_text) {
                const extraDiv = document.createElement('div');
                extraDiv.className = 'diagram-extra';
                extraDiv.innerText = diagramData.extra_text;
                diagDiv.appendChild(extraDiv);
            }
            diagDiv.appendChild(theoryDiv);
            container.appendChild(diagDiv);
            
        } catch (error) {
            console.error("Diagram failed:", error);
            container.innerHTML += `<div class="card"><div id="canvas-container"><svg viewBox="0 0 300 200" xmlns="http://www.w3.org/2000/svg"><rect x="10" y="10" width="280" height="180" fill="#f8f9fa" stroke="#ccc" stroke-dasharray="5,5"/><text x="150" y="100" text-anchor="middle" font-family="Arial" fill="#d9534f">Error Rendering Diagram</text></svg></div></div>`;
        } finally {
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }
    }

    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        appendMessage(text, true);
        userInput.value = '';
        loader.style.display = 'block';

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            
            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.text || "Server returned status " + response.status);
            }
            
            const data = await response.json();
            const aiMsgDiv = appendMessage(data.text, false);
            
            if (data.diagram && data.diagram.svg) { drawDiagram(aiMsgDiv, data.diagram); }
            if (data.text) { showExplanation(data.text); }
            
        } catch (error) {
            console.error(error);
            chatWindow.innerHTML += `<div class="card" style="color:red; border-color:red; margin-bottom: 15px;">Error: Could not connect to AI Tutor. ${error.message}. Try refreshing.</div>`;
            chatWindow.scrollTop = chatWindow.scrollHeight;
        } finally {
            loader.style.display = 'none';
        }
    }
</script>
</body>
</html>
"""

# --- 5. ROUTES ---
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health():
    return jsonify({"status": "ok", "timestamp": time.time()})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get("message", "")
        
        diagram_json = None
        svg_data, topic, json_meta = get_diagram_svg(user_message)
        if svg_data:
            diagram_json = {
                "svg": svg_data,
                "theory": json_meta.get("theory", ""),
                "extra_text": json_meta.get("extra_text", "")
            }
            
        if groq_client:
            completion = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.2, 
                max_tokens=250,
                timeout=20  # Added timeout for robust connection handling
            )
            ai_response = completion.choices[0].message.content
        else:
            ai_response = "System warning: Groq client not initialized. Ensure valid API key."
            
        return jsonify({
            "text": ai_response,
            "diagram": diagram_json
        })

    except Exception as e:
        print(f"[ERROR] {e}") # This will show in Render logs
        return jsonify({
            "text": f"Server Error: {str(e)}. Check GROQ_API_KEY and Render logs.", 
            "diagram": None
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
