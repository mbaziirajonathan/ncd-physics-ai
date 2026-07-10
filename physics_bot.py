import os
import time
import threading
import httpx
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)

# --- CONFIG & SYSTEM PROMPT ---
SYSTEM_PROMPT = """
You are NCD Physics AI. Provide concise, accurate physics explanations based on the 2026 NCDC syllabus.
"""

# --- TECHNICAL SETUP ---
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

# --- MASTER DIAGRAM LIBRARY - NCDC 2026 / UNEB S1-S4 ---
CRO_SVG = """<svg width="100%" viewBox="0 0 420 240" xmlns="http://www.w3.org/2000/svg"><rect width="420" height="240" fill="#f0f8ff" stroke="#004a99" stroke-width="2" rx="8"/><text x="210" y="25" text-anchor="middle" font-size="14" font-weight="bold" fill="#004a99">CATHODE RAY OSCILLOSCOPE</text><rect x="50" y="50" width="320" height="140" fill="black" stroke="#333" stroke-width="2" rx="5"/><text x="210" y="110" text-anchor="middle" font-size="11" fill="lime">SCREEN</text><path d="M 60 120 Q 210 90 360 120" stroke="lime" stroke-width="2" fill="none"/><polygon points="360,120 352,116 352,124" fill="lime"/><text x="20" y="60" font-size="9">ELECTRON GUN</text><text x="370" y="90" font-size="9">Y-PLATES</text><text x="200" y="210" font-size="9">X-PLATES</text></svg>"""

TRANSFORMER_SVG = """<svg width="100%" viewBox="0 0 420 240" xmlns="http://www.w3.org/2000/svg"><rect width="420" height="240" fill="#f0f8ff" stroke="#004a99" stroke-width="2" rx="8"/><text x="210" y="25" text-anchor="middle" font-size="14" font-weight="bold" fill="#004a99">SIMPLE TRANSFORMER</text><rect x="100" y="70" width="40" height="100" fill="#666"/><rect x="280" y="70" width="40" height="100" fill="#666"/><text x="120" y="65" text-anchor="middle" font-size="10">PRIMARY COIL</text><text x="300" y="65" text-anchor="middle" font-size="10">SECONDARY COIL</text><path d="M 100 90 Q 200 70 280 90" stroke="red" stroke-width="2" fill="none"/><path d="M 100 110 Q 200 130 280 110" stroke="blue" stroke-width="2" fill="none"/><text x="40" y="100" font-size="10">AC IN</text><text x="360" y="100" font-size="10">AC OUT</text></svg>"""

MOTOR_SVG = """<svg width="100%" viewBox="0 0 420 240" xmlns="http://www.w3.org/2000/svg"><rect width="420" height="240" fill="#f0f8ff" stroke="#004a99" stroke-width="2" rx="8"/><text x="210" y="25" text-anchor="middle" font-size="14" font-weight="bold" fill="#004a99">DC ELECTRIC MOTOR</text><rect x="80" y="60" width="40" height="80" fill="red"/><text x="100" y="55" text-anchor="middle" font-size="10" fill="red">N</text><rect x="300" y="60" width="40" height="80" fill="blue"/><text x="320" y="55" text-anchor="middle" font-size="10" fill="blue">S</text><circle cx="210" cy="100" r="35" fill="white" stroke="#333" stroke-width="2"/><text x="210" y="105" text-anchor="middle" font-size="9">ARMATURE COIL</text><line x1="210" y1="135" x2="210" y2="170" stroke="#333" stroke-width="2"/><line x1="170" y1="170" x2="250" y2="170" stroke="#333" stroke-width="2"/><text x="160" y="185" font-size="9">+ BATTERY</text><text x="250" y="185" font-size="9">- BATTERY</text></svg>"""

GENERATOR_SVG = """<svg width="100%" viewBox="0 0 420 240" xmlns="http://www.w3.org/2000/svg"><rect width="420" height="240" fill="#f0f8ff" stroke="#004a99" stroke-width="2" rx="8"/><text x="210" y="25" text-anchor="middle" font-size="14" font-weight="bold" fill="#004a99">AC GENERATOR</text><rect x="80" y="60" width="40" height="80" fill="red"/><rect x="300" y="60" width="40" height="80" fill="blue"/><circle cx="210" cy="100" r="35" fill="white" stroke="#333" stroke-width="2"/><circle cx="180" cy="100" r="5" fill="orange"/><circle cx="240" cy="100" r="5" fill="orange"/><text x="210" y="105" text-anchor="middle" font-size="9">COIL</text><path d="M 180 130 Q 210 150 240 130" stroke="orange" stroke-width="2" fill="none"/><text x="210" y="180" text-anchor="middle" font-size="9">SLIP RINGS -> AC OUTPUT</text></svg>"""

LENS_SVG = """<svg width="100%" viewBox="0 0 420 240" xmlns="http://www.w3.org/2000/svg"><rect width="420" height="240" fill="#f0f8ff" stroke="#004a99" stroke-width="2" rx="8"/><text x="210" y="25" text-anchor="middle" font-size="14" font-weight="bold" fill="#004a99">CONVEX LENS - RAY DIAGRAM</text><path d="M 200 50 Q 220 120 200 190 Q 180 120 200 50" fill="lightblue" stroke="#333"/><line x1="210" y1="50" x2="210" y2="190" stroke="#999" stroke-dasharray="4"/><text x="210" y="200" text-anchor="middle" font-size="9">PRINCIPAL AXIS</text><line x1="80" y1="120" x2="340" y2="120" stroke="red" stroke-width="1.5"/><line x1="80" y1="120" x2="200" y2="70" stroke="blue" stroke-width="1.5"/><line x1="200" y1="70" x2="340" y2="120" stroke="blue" stroke-width="1.5"/><text x="70" y="115" font-size="9">OBJECT</text><text x="345" y="115" font-size="9">REAL IMAGE</text></svg>"""

CIRCUIT_SVG = """<svg width="100%" viewBox="0 0 420 240" xmlns="http://www.w3.org/2000/svg"><rect width="420" height="240" fill="#f0f8ff" stroke="#004a99" stroke-width="2" rx="8"/><text x="210" y="25" text-anchor="middle" font-size="14" font-weight="bold" fill="#004a99">SIMPLE CIRCUIT - OHM'S LAW</text><rect x="60" y="100" width="50" height="25" fill="yellow" stroke="#333"/><text x="85" y="117" text-anchor="middle" font-size="9">CELL</text><rect x="160" y="100" width="50" height="25" fill="lightgray" stroke="#333"/><text x="185" y="117" text-anchor="middle" font-size="9">RESISTOR</text><circle cx="260" cy="112" r="12" fill="white" stroke="#333"/><text x="260" y="116" text-anchor="middle" font-size="9">A</text><line x1="110" y1="112" x2="160" y2="112" stroke="#333" stroke-width="2"/><line x1="210" y1="112" x2="248" y2="112" stroke="#333" stroke-width="2"/><line x1="272" y1="112" x2="320" y2="112" stroke="#333" stroke-width="2"/><line x1="320" y1="112" x2="320" y2="160" stroke="#333" stroke-width="2"/><line x1="320" y1="160" x2="60" y2="160" stroke="#333" stroke-width="2"/><line x1="60" y1="160" x2="60" y2="112" stroke="#333" stroke-width="2"/></svg>"""

LEVER_SVG = """<svg width="100%" viewBox="0 0 420 240" xmlns="http://www.w3.org/2000/svg"><rect width="420" height="240" fill="#f0f8ff" stroke="#004a99" stroke-width="2" rx="8"/><text x="210" y="25" text-anchor="middle" font-size="14" font-weight="bold" fill="#004a99">CLASS 1 LEVER</text><line x1="80" y1="120" x2="340" y2="120" stroke="#8B4513" stroke-width="6"/><circle cx="210" cy="120" r="8" fill="#333"/><text x="210" y="140" text-anchor="middle" font-size="9">FULCRUM</text><polygon points="70,120 60,110 60,130" fill="#333"/><text x="40" y="105" font-size="9">EFFORT</text><polygon points="350,120 360,110 360,130" fill="#333"/><text x="350" y="105" font-size="9">LOAD</text></svg>"""

WAVE_SVG = """<svg width="100%" viewBox="0 0 420 240" xmlns="http://www.w3.org/2000/svg"><rect width="420" height="240" fill="#f0f8ff" stroke="#004a99" stroke-width="2" rx="8"/><text x="210" y="25" text-anchor="middle" font-size="14" font-weight="bold" fill="#004a99">TRANSVERSE WAVE</text><line x1="50" y1="120" x2="370" y2="120" stroke="#999" stroke-dasharray="4"/><path d="M 50 120 Q 80 70 110 120 Q 140 170 170 120 Q 200 70 230 120 Q 260 170 290 120 Q 320 70 350 120" stroke="#004a99" stroke-width="2" fill="none"/><text x="110" y="65" font-size="9">CREST</text><text x="170" y="180" font-size="9">TROUGH</text><line x1="50" y1="200" x2="170" y2="200" stroke="#333"/><text x="100" y="215" text-anchor="middle" font-size="9">WAVELENGTH</text></svg>"""

PULLEY_SVG = """<svg width="100%" viewBox="0 0 420 240" xmlns="http://www.w3.org/2000/svg"><rect width="420" height="240" fill="#f0f8ff" stroke="#004a99" stroke-width="2" rx="8"/><text x="210" y="25" text-anchor="middle" font-size="14" font-weight="bold" fill="#004a99">SINGLE FIXED PULLEY</text><circle cx="210" cy="60" r="25" fill="none" stroke="#333" stroke-width="3"/><line x1="185" y1="60" x2="185" y2="180" stroke="#333" stroke-width="2"/><line x1="235" y1="60" x2="235" y2="180" stroke="#333" stroke-width="2"/><rect x="170" y="180" width="30" height="20" fill="#8B4513"/><text x="185" y="195" text-anchor="middle" font-size="9">LOAD</text><text x="250" y="190" font-size="9">EFFORT</text></svg>"""

DIAGRAM_LIBRARY = {
    "cathode ray oscilloscope": CRO_SVG,
    "cro": CRO_SVG,
    "transformer": TRANSFORMER_SVG,
    "motor": MOTOR_SVG,
    "dc motor": MOTOR_SVG,
    "generator": GENERATOR_SVG,
    "ac generator": GENERATOR_SVG,
    "convex lens": LENS_SVG,
    "lens": LENS_SVG,
    "simple circuit": CIRCUIT_SVG,
    "ohms law": CIRCUIT_SVG,
    "circuit": CIRCUIT_SVG,
    "lever": LEVER_SVG,
    "class 1 lever": LEVER_SVG,
    "wave": WAVE_SVG,
    "transverse wave": WAVE_SVG,
    "pulley": PULLEY_SVG,
    "single pulley": PULLEY_SVG
}

def get_diagram_svg(user_message):
    msg = user_message.lower()

    if not any(k in msg for k in ["draw", "diagram", "show", "illustrate"]):
        return None, None

    for keyword, svg in DIAGRAM_LIBRARY.items():
        if keyword in msg:
            return svg, keyword.upper()
            
    return None, None

# --- FRONTEND HTML + CSS + JS ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NCD Physics AI Tutor</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; }
        #app-container { width: 100%; max-width: 900px; background: #fff; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); overflow: hidden; display: flex; flex-direction: column; height: 90vh; }
        .header { background: #0056b3; color: white; padding: 15px; text-align: center; }
        .header h1 { margin: 0; font-size: 1.5rem; }
        
        .main-content { display: flex; flex: 1; overflow: hidden; }
        @media (max-width: 768px) {
            .main-content { flex-direction: column; }
        }
        
        .card {background:white; margin:10px; padding:15px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.1); width:calc(100% - 20px); box-sizing:border-box; overflow:visible}
        #canvas-container {width:100%; min-height:240px; display:flex; align-items:center; justify-content:center; overflow-x:auto; padding:5px}
        #canvas-container svg {width:100%!important; height:auto!important; max-width:100%}
        
        #chat-window { flex: 2; padding: 20px; overflow-y: auto; background: #fafafa; border-right: 1px solid #ddd; }
        .message { margin-bottom: 15px; padding: 10px 15px; border-radius: 8px; max-width: 90%; line-height: 1.4; word-wrap: break-word; }
        .user-msg { background: #007bff; color: white; align-self: flex-end; margin-left: auto; border-bottom-right-radius: 0; }
        .ai-msg { background: #e9ecef; color: #333; align-self: flex-start; margin-right: auto; border-bottom-left-radius: 0; }
        
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
    </div>
    
    <div class="main-content">
        <div id="chat-window">
            <div class="message ai-msg">Welcome! I can explain topics and <b>draw diagrams</b>. Try asking: "draw a motor" or "draw a simple circuit".</div>
        </div>
    </div>
    
    <div class="loader" id="loader"></div>
    
    <div class="input-area">
        <input type="text" id="user-input" placeholder="Ask a physics question or say 'draw cro'..." onkeypress="handleKeyPress(event)">
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
    
    function drawDiagram(container, svgData) {
        if (!svgData || svgData === "None" || svgData.trim() === "") return;
        const diagDiv = document.createElement('div');
        diagDiv.className = 'card';
        const svgWrapper = document.createElement('div');
        svgWrapper.id = 'canvas-container';
        svgWrapper.innerHTML = svgData;
        diagDiv.appendChild(svgWrapper);
        container.appendChild(diagDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
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
            const aiMsgDiv = appendMessage(data.reply, false);
            
            if (data.svg) { 
                drawDiagram(aiMsgDiv, data.svg); 
            }
            
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

# --- ROUTES ---
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
        
        svg, topic = get_diagram_svg(user_message)
        
        if groq_client:
            completion = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.2, 
                max_tokens=250,
                timeout=20
            )
            ai_response = completion.choices[0].message.content
        else:
            ai_response = f"Here is the information for {topic}." if topic else "Here is the explanation. (Groq API Key missing or invalid)"
            
        return jsonify({
            "reply": ai_response,
            "svg": svg,
            "topic": topic
        })

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({
            "reply": f"Server Error: {str(e)}. Check GROQ_API_KEY and Render logs.", 
            "svg": None,
            "topic": None
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
