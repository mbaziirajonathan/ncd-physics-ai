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

CRO_SVG = """<svg width="100%" viewBox="0 0 420 260" xmlns="http://www.w3.org/2000/svg" id="cro-diagram">
<rect width="420" height="260" fill="#f0f8ff" stroke="#004a99" stroke-width="2" rx="8"/>
<text x="210" y="20" text-anchor="middle" font-size="14" font-weight="bold" fill="#004a99">CATHODE RAY OSCILLOSCOPE</text>
<path d="M 40 130 L 100 130 L 180 90 L 360 90 L 360 170 L 180 170 L 100 130" fill="white" stroke="#333" stroke-width="2"/>
<rect x="50" y="115" width="20" height="30" fill="#666" id="electron-gun"/>
<text x="60" y="105" text-anchor="middle" font-size="9">Electron Gun</text>
<rect x="130" y="105" width="20" height="5" fill="#000" id="y-plate-top"/>
<rect x="130" y="150" width="20" height="5" fill="#000" id="y-plate-bottom"/>
<text x="140" y="95" text-anchor="middle" font-size="9">Y-Plates</text>
<rect x="180" y="115" width="10" height="30" fill="#000" id="x-plates"/>
<text x="185" y="165" text-anchor="middle" font-size="9">X-Plates</text>
<path d="M 70 130 L 360 130" stroke="lime" stroke-width="2" stroke-dasharray="4" id="electron-beam"/>
<rect x="360" y="90" width="10" height="80" fill="lime" id="screen"/>
<text x="375" y="135" font-size="9">Screen</text>
</svg>"""

TRANSFORMER_SVG = """<svg width="100%" viewBox="0 0 420 260" xmlns="http://www.w3.org/2000/svg" id="transformer-diagram">
<rect width="420" height="260" fill="#f0f8ff" stroke="#004a99" stroke-width="2" rx="8"/>
<text x="210" y="20" text-anchor="middle" font-size="14" font-weight="bold" fill="#004a99">STEP-DOWN TRANSFORMER</text>
<rect x="120" y="50" width="180" height="160" fill="none" stroke="#666" stroke-width="30" id="iron-core"/>
<rect x="125" y="55" width="170" height="150" fill="none" stroke="#ccc" stroke-width="1"/>
<rect x="130" y="60" width="160" height="140" fill="none" stroke="#ccc" stroke-width="1"/>
<text x="210" y="135" text-anchor="middle" font-size="10">Laminated Iron Core</text>
<rect x="135" y="65" width="150" height="130" fill="none" stroke="red" stroke-dasharray="5" stroke-width="1"/>
<path d="M 80 80 Q 150 90 80 100 Q 150 110 80 120 Q 150 130 80 140 Q 150 150 80 160 Q 150 170 80 180" stroke="#b87333" stroke-width="3" fill="none" id="primary-coil"/>
<text x="60" y="135" text-anchor="middle" font-size="10">Primary</text>
<text x="60" y="145" text-anchor="middle" font-size="10">(8 turns)</text>
<path d="M 340 100 Q 270 115 340 130 Q 270 145 340 160" stroke="#b87333" stroke-width="3" fill="none" id="secondary-coil"/>
<text x="360" y="135" text-anchor="middle" font-size="10">Secondary</text>
<text x="360" y="145" text-anchor="middle" font-size="10">(4 turns)</text>
</svg>"""

GENERATOR_SVG = """<svg width="100%" viewBox="0 0 420 260" xmlns="http://www.w3.org/2000/svg" id="generator-diagram">
<rect width="420" height="260" fill="#f0f8ff" stroke="#004a99" stroke-width="2" rx="8"/>
<text x="210" y="20" text-anchor="middle" font-size="14" font-weight="bold" fill="#004a99">AC GENERATOR</text>
<rect x="50" y="70" width="50" height="100" fill="red" id="magnet-n"/>
<text x="75" y="125" text-anchor="middle" fill="white" font-weight="bold">N</text>
<rect x="320" y="70" width="50" height="100" fill="blue" id="magnet-s"/>
<text x="345" y="125" text-anchor="middle" fill="white" font-weight="bold">S</text>
<rect x="150" y="80" width="120" height="60" fill="none" stroke="#b87333" stroke-width="3" id="coil"/>
<path d="M 190 60 Q 210 40 230 60" fill="none" stroke="green" stroke-width="2"/>
<polygon points="230,60 225,50 235,50" fill="green"/>
<text x="210" y="45" text-anchor="middle" font-size="10" fill="green">Rotation</text>
<ellipse cx="170" cy="180" rx="10" ry="20" fill="none" stroke="#d4af37" stroke-width="3" id="slip-ring-1"/>
<ellipse cx="250" cy="180" rx="10" ry="20" fill="none" stroke="#d4af37" stroke-width="3" id="slip-ring-2"/>
<line x1="150" y1="140" x2="150" y2="180" stroke="#b87333" stroke-width="3"/>
<line x1="270" y1="140" x2="270" y2="180" stroke="#b87333" stroke-width="3"/>
<rect x="140" y="170" width="10" height="20" fill="#333" id="brush-1"/>
<rect x="270" y="170" width="10" height="20" fill="#333" id="brush-2"/>
<text x="130" y="165" font-size="9">Carbon Brushes</text>
<path d="M 140 180 L 100 180 L 100 230 L 140 230" fill="none" stroke="#000"/>
<path d="M 280 180 L 320 180 L 320 230 L 280 230" fill="none" stroke="#000"/>
<circle cx="140" cy="230" r="3"/><circle cx="280" cy="230" r="3"/>
<text x="210" y="235" text-anchor="middle" font-size="10">AC Output ~</text>
</svg>"""

CIRCUIT_SVG = """<svg width="100%" viewBox="0 0 420 260" xmlns="http://www.w3.org/2000/svg" id="circuit-diagram">
<rect width="420" height="260" fill="#f0f8ff" stroke="#004a99" stroke-width="2" rx="8"/>
<text x="210" y="20" text-anchor="middle" font-size="14" font-weight="bold" fill="#004a99">SIMPLE CIRCUIT</text>
<path d="M 100 80 L 320 80 L 320 200 L 100 200 Z" fill="none" stroke="#333" stroke-width="2" id="main-circuit"/>
<rect x="180" y="70" width="60" height="20" fill="#f0f8ff"/>
<line x1="200" y1="60" x2="200" y2="100" stroke="#333" stroke-width="3" id="cell-positive"/>
<line x1="220" y1="70" x2="220" y2="90" stroke="#333" stroke-width="6" id="cell-negative"/>
<text x="190" y="55" font-size="12">+</text><text x="225" y="55" font-size="12">-</text>
<text x="210" y="115" text-anchor="middle" font-size="10">Cell</text>
<rect x="180" y="190" width="60" height="20" fill="#f0f8ff"/>
<path d="M 180 200 L 185 190 L 195 210 L 205 190 L 215 210 L 225 190 L 235 210 L 240 200" fill="none" stroke="#333" stroke-width="2" id="resistor"/>
<text x="210" y="225" text-anchor="middle" font-size="10">Resistor (R)</text>
<circle cx="320" cy="140" r="15" fill="white" stroke="#333" stroke-width="2" id="ammeter"/>
<text x="320" y="145" text-anchor="middle" font-size="12">A</text>
<text x="350" y="145" font-size="10">Ammeter</text>
<text x="300" y="125" font-size="10">+</text><text x="300" y="165" font-size="10">-</text>
<path d="M 160 200 L 160 160 L 260 160 L 260 200" fill="none" stroke="#333" stroke-width="2"/>
<circle cx="210" cy="160" r="15" fill="white" stroke="#333" stroke-width="2" id="voltmeter"/>
<text x="210" y="165" text-anchor="middle" font-size="12">V</text>
<text x="210" y="140" text-anchor="middle" font-size="10">Voltmeter</text>
</svg>"""

LEVER_SVG = """<svg width="100%" viewBox="0 0 420 260" xmlns="http://www.w3.org/2000/svg" id="lever-diagram">
<rect width="420" height="260" fill="#f0f8ff" stroke="#004a99" stroke-width="2" rx="8"/>
<text x="210" y="20" text-anchor="middle" font-size="14" font-weight="bold" fill="#004a99">CLASS 1 LEVER</text>
<rect x="60" y="120" width="300" height="10" fill="#8b4513" stroke="#333" id="lever-arm"/>
<polygon points="210,130 190,170 230,170" fill="#777" stroke="#333" id="fulcrum"/>
<text x="210" y="185" text-anchor="middle" font-size="12">Fulcrum</text>
<rect x="70" y="80" width="40" height="40" fill="#666" stroke="#333" id="load-box"/>
<text x="90" y="105" text-anchor="middle" font-size="10" fill="white">Load</text>
<line x1="330" y1="80" x2="330" y2="115" stroke="red" stroke-width="3" id="effort-arrow"/>
<polygon points="330,120 325,110 335,110" fill="red"/>
<text x="330" y="70" text-anchor="middle" font-size="12" fill="red">Effort</text>
<line x1="90" y1="140" x2="210" y2="140" stroke="#000" stroke-width="1" stroke-dasharray="4"/>
<line x1="90" y1="135" x2="90" y2="145" stroke="#000"/><line x1="210" y1="135" x2="210" y2="145" stroke="#000"/>
<text x="150" y="155" text-anchor="middle" font-size="10">Load Arm</text>
<line x1="210" y1="140" x2="330" y2="140" stroke="#000" stroke-width="1" stroke-dasharray="4"/>
<line x1="330" y1="135" x2="330" y2="145" stroke="#000"/>
<text x="270" y="155" text-anchor="middle" font-size="10">Effort Arm</text>
</svg>"""

WAVE_SVG = """<svg width="100%" viewBox="0 0 420 260" xmlns="http://www.w3.org/2000/svg" id="wave-diagram">
<rect width="420" height="260" fill="#f0f8ff" stroke="#004a99" stroke-width="2" rx="8"/>
<text x="210" y="20" text-anchor="middle" font-size="14" font-weight="bold" fill="#004a99">TRANSVERSE WAVE</text>
<line x1="40" y1="130" x2="380" y2="130" stroke="#333" stroke-width="1" stroke-dasharray="4" id="equilibrium-line"/>
<path d="M 60 130 Q 100 50 140 130 T 220 130 T 300 130 T 380 130" fill="none" stroke="#004a99" stroke-width="3" id="wave-profile"/>
<line x1="100" y1="130" x2="100" y2="90" stroke="red" stroke-width="2" id="amplitude-indicator"/>
<polygon points="100,90 97,95 103,95" fill="red"/>
<text x="110" y="115" font-size="12" fill="red">Amplitude (A)</text>
<line x1="100" y1="60" x2="260" y2="60" stroke="#000" stroke-width="1" id="wavelength-indicator"/>
<polygon points="100,60 105,57 105,63" fill="#000"/>
<polygon points="260,60 255,57 255,63" fill="#000"/>
<text x="180" y="55" text-anchor="middle" font-size="12">Wavelength (λ)</text>
<line x1="100" y1="65" x2="100" y2="90" stroke="#000" stroke-width="1" stroke-dasharray="2"/>
<line x1="260" y1="65" x2="260" y2="90" stroke="#000" stroke-width="1" stroke-dasharray="2"/>
<line x1="330" y1="180" x2="380" y2="180" stroke="green" stroke-width="3" id="propagation-arrow"/>
<polygon points="380,180 370,175 370,185" fill="green"/>
<text x="355" y="200" text-anchor="middle" font-size="12" fill="green">Direction of Propagation</text>
<text x="140" y="220" font-size="12">Trough</text>
<text x="260" y="80" font-size="12">Crest</text>
</svg>"""

PULLEY_SVG = """<svg width="100%" viewBox="0 0 420 260" xmlns="http://www.w3.org/2000/svg" id="pulley-diagram">
<rect width="420" height="260" fill="#f0f8ff" stroke="#004a99" stroke-width="2" rx="8"/>
<text x="210" y="20" text-anchor="middle" font-size="14" font-weight="bold" fill="#004a99">SINGLE FIXED PULLEY</text>
<rect x="150" y="40" width="120" height="10" fill="#333" id="overhead-support"/>
<path d="M 150 40 L 160 30 M 170 40 L 180 30 M 190 40 L 200 30 M 210 40 L 220 30 M 230 40 L 240 30 M 250 40 L 260 30" stroke="#333" stroke-width="1"/>
<line x1="210" y1="50" x2="210" y2="90" stroke="#333" stroke-width="4" id="pulley-hanger"/>
<circle cx="210" cy="110" r="30" fill="none" stroke="#666" stroke-width="5" id="pulley-wheel"/>
<circle cx="210" cy="110" r="5" fill="#333"/>
<line x1="180" y1="110" x2="180" y2="180" stroke="#000" stroke-width="2" id="rope-left"/>
<line x1="240" y1="110" x2="240" y2="180" stroke="#000" stroke-width="2" id="rope-right"/>
<rect x="165" y="180" width="30" height="30" fill="#8b4513" id="load-mass"/>
<text x="180" y="225" text-anchor="middle" font-size="12">Load (L)</text>
<line x1="180" y1="230" x2="180" y2="250" stroke="#000" stroke-width="2"/>
<polygon points="180,250 177,245 183,245" fill="#000"/>
<line x1="240" y1="180" x2="240" y2="220" stroke="red" stroke-width="2" id="effort-line"/>
<polygon points="240,220 237,215 243,215" fill="red"/>
<text x="240" y="235" text-anchor="middle" font-size="12" fill="red">Effort (E)</text>
<line x1="180" y1="140" x2="180" y2="120" stroke="blue" stroke-width="2"/>
<polygon points="180,120 177,125 183,125" fill="blue"/>
<line x1="240" y1="140" x2="240" y2="120" stroke="blue" stroke-width="2"/>
<polygon points="240,120 237,125 243,125" fill="blue"/>
<text x="170" y="135" font-size="10" fill="blue">T</text>
<text x="250" y="135" font-size="10" fill="blue">T</text>
<text x="350" y="60" font-size="14" font-weight="bold">MA = 1</text>
<text x="350" y="80" font-size="12">V.R = 1</text>
</svg>"""

MOTOR_SVG = """<svg width="100%" viewBox="0 0 420 260" xmlns="http://www.w3.org/2000/svg" id="motor-diagram">
<rect width="420" height="260" fill="#f0f8ff" stroke="#004a99" stroke-width="2" rx="8"/>
<text x="210" y="20" text-anchor="middle" font-size="14" font-weight="bold" fill="#004a99">DC MOTOR</text>
<rect x="50" y="80" width="50" height="80" fill="red" id="magnet-n"/>
<text x="75" y="125" text-anchor="middle" fill="white" font-weight="bold">N</text>
<rect x="320" y="80" width="50" height="80" fill="blue" id="magnet-s"/>
<text x="345" y="125" text-anchor="middle" fill="white" font-weight="bold">S</text>
<path d="M 100 120 L 320 120" stroke="#ccc" stroke-dasharray="4" stroke-width="1"/>
<polygon points="210,120 205,117 205,123" fill="#ccc"/>
<rect x="140" y="90" width="140" height="60" fill="none" stroke="#b87333" stroke-width="3" id="coil"/>
<path d="M 190 170 A 10 10 0 0 1 205 170" fill="none" stroke="#d4af37" stroke-width="4"/>
<path d="M 215 170 A 10 10 0 0 1 230 170" fill="none" stroke="#d4af37" stroke-width="4"/>
<line x1="140" y1="150" x2="140" y2="170" stroke="#b87333" stroke-width="3"/>
<line x1="280" y1="150" x2="280" y2="170" stroke="#b87333" stroke-width="3"/>
<line x1="140" y1="170" x2="190" y2="170" stroke="#b87333" stroke-width="3"/>
<line x1="280" y1="170" x2="230" y2="170" stroke="#b87333" stroke-width="3"/>
<rect x="180" y="165" width="10" height="10" fill="#333" id="brush-positive"/>
<rect x="230" y="165" width="10" height="10" fill="#333" id="brush-negative"/>
<text x="185" y="190" text-anchor="middle" font-size="9">Brushes</text>
<text x="210" y="160" text-anchor="middle" font-size="9" id="commutator">Commutator</text>
<line x1="180" y1="170" x2="150" y2="170" stroke="#000" stroke-width="1"/>
<line x1="150" y1="170" x2="150" y2="230" stroke="#000" stroke-width="1"/>
<line x1="150" y1="230" x2="190" y2="230" stroke="#000" stroke-width="1"/>
<line x1="240" y1="170" x2="270" y2="170" stroke="#000" stroke-width="1"/>
<line x1="270" y1="170" x2="270" y2="230" stroke="#000" stroke-width="1"/>
<line x1="270" y1="230" x2="230" y2="230" stroke="#000" stroke-width="1"/>
<line x1="190" y1="220" x2="190" y2="240" stroke="#333" stroke-width="2"/>
<line x1="205" y1="225" x2="205" y2="235" stroke="#333" stroke-width="4"/>
<line x1="205" y1="230" x2="230" y2="230" stroke="#333" stroke-width="1"/>
<text x="180" y="215" font-size="10">+</text>
<text x="215" y="215" font-size="10">-</text>
<polygon points="140,110 137,115 143,115" fill="#000"/>
<polygon points="280,115 277,110 283,110" fill="#000"/>
<text x="120" y="115" font-size="10">I</text>
<text x="290" y="115" font-size="10">I</text>
<line x1="140" y1="90" x2="140" y2="60" stroke="green" stroke-width="2"/>
<polygon points="140,60 137,65 143,65" fill="green"/>
<text x="145" y="70" font-size="10" fill="green">Force (Up)</text>
</svg>"""

LENS_SVG = """<svg width="100%" viewBox="0 0 420 260" xmlns="http://www.w3.org/2000/svg" id="lens-diagram">
<rect width="420" height="260" fill="#f0f8ff" stroke="#004a99" stroke-width="2" rx="8"/>
<text x="210" y="25" text-anchor="middle" font-size="14" font-weight="bold" fill="#004a99">CONVEX LENS - RAY DIAGRAM</text>
<path d="M 200 50 Q 220 120 200 190 Q 180 120 200 50" fill="lightblue" stroke="#333" id="convex-lens"/>
<line x1="210" y1="50" x2="210" y2="190" stroke="#999" stroke-dasharray="4"/>
<text x="210" y="210" text-anchor="middle" font-size="9">PRINCIPAL AXIS</text>
<line x1="80" y1="120" x2="340" y2="120" stroke="red" stroke-width="1.5" id="principal-axis-line"/>
<line x1="80" y1="120" x2="200" y2="70" stroke="blue" stroke-width="1.5" id="incident-ray"/>
<line x1="200" y1="70" x2="340" y2="120" stroke="blue" stroke-width="1.5" id="refracted-ray"/>
<text x="70" y="115" font-size="9">OBJECT</text>
<text x="345" y="115" font-size="9">REAL IMAGE</text>
</svg>"""

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
        
        .card { background: white; margin: 10px; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); width: calc(100% - 20px); box-sizing: border-box; overflow: visible; position: relative; }
        #canvas-container { width: 100%; min-height: 240px; display: flex; align-items: center; justify-content: center; overflow-x: auto; padding: 5px; }
        #canvas-container svg { width: 100%!important; height: auto!important; max-width: 100%; cursor: pointer; }
        
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
            <div class="message ai-msg">Welcome! I can explain topics and <b>draw diagrams</b>. Try asking: "draw a motor" or "draw a simple circuit". Click on a diagram box to see dynamic action elements if applicable.</div>
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
        
        // Add interactive dynamic flow on circuit click if the main circuit elements exist
        const targetSvg = svgWrapper.querySelector('svg');
        if (targetSvg) {
            targetSvg.addEventListener('click', function() {
                const circuitPath = targetSvg.querySelector('#main-circuit');
                if (circuitPath) {
                    let dotsGroup = targetSvg.querySelector('#flow-dots-group');
                    if (!dotsGroup) {
                        dotsGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
                        dotsGroup.id = "flow-dots-group";
                        targetSvg.appendChild(dotsGroup);
                        
                        // Create flowing red dots
                        for (let i = 0; i < 5; i++) {
                            const dot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
                            dot.setAttribute("r", "4");
                            dot.setAttribute("fill", "red");
                            dotsGroup.appendChild(dot);
                        }
                    }
                    
                    let progress = 0;
                    function animateFlow() {
                        progress += 1;
                        const len = 880; // approximate perimeter length
                        const dots = dotsGroup.querySelectorAll('circle');
                        dots.forEach((dot, index) => {
                            let offset = (progress + (index * (len / dots.length))) % len;
                            // Basic coordinate mapping along rectangle box bounds [100, 80] to [320, 200]
                            let x = 100, y = 80;
                            if (offset < 220) { x = 100 + offset; y = 80; }
                            else if (offset < 340) { x = 320; y = 80 + (offset - 220); }
                            else if (offset < 560) { x = 320 - (offset - 340); y = 200; }
                            else { x = 100; y = 200 - (offset - 560); }
                            
                            dot.setAttribute("cx", x);
                            dot.setAttribute("cy", y);
                        });
                        if (progress < 400) {
                            requestAnimationFrame(animateFlow);
                        } else {
                            dotsGroup.remove();
                        }
                    }
                    animateFlow();
                }
            });
        }
        
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
