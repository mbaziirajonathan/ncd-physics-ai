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

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<title>Meta AI Physics Diagram Generator v7.9</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body{font-family:Arial;max-width:800px;margin:0 auto;padding:20px;background:#f5f5f5}
h2{color:#0084ff}
#input{width:70%;padding:10px;font-size:16px;border:1px solid #ddd;border-radius:5px}
#btn{padding:10px 20px;font-size:16px;background:#0084ff;color:white;border:none;border-radius:5px;cursor:pointer}
#btn:hover{background:#006acc}
#canvas{background:white;border:1px solid #ddd;margin-top:20px;border-radius:8px;padding:10px;box-shadow:0 2px 4px rgba(0,0,0,0.1)}
</style>
</head>
<body>
<h2>Physics Diagram Generator v7.9 - NCDC Uganda</h2>
<input id="input" placeholder="draw principle of moments w1 10 w2 20 d1 80 d2 40">
<button id="btn" onclick="generate()">Generate</button>
<div id="canvas"></div>

<script>
function generate(){
  const cmd = document.getElementById('input').value.toLowerCase();
  document.getElementById('canvas').innerHTML = drawDiagram(cmd);
}

function drawDiagram(cmd){
  let svg = `<svg width="420" height="220" viewBox="0 0 420 220" xmlns="http://www.w3.org/2000/svg">
  <defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0 0 L0 6 L9 3 z" fill="black"/></marker></defs>`;
  
  // 1. PRINCIPLE OF MOMENTS - BUGFIX: y=95
  if(cmd.includes('principle of moments')){
    const w1 = cmd.match(/w1 (\\d+)/)?.[1] || 10;
    const w2 = cmd.match(/w2 (\\d+)/)?.[1] || 20;
    const d1 = cmd.match(/d1 (\\d+)/)?.[1] || 80;
    const d2 = cmd.match(/d2 (\\d+)/)?.[1] || 40;
    const m1 = w1*d1; const m2 = w2*d2; const status = m1==m2?'IN EQUILIBRIUM':'NOT IN EQUILIBRIUM';
    const pos1 = 200-d1; const pos2 = 200+d2;
    svg += `<line x1="50" y1="100" x2="350" y2="100" stroke="black" stroke-width="3"/>
    <polygon points="200 90 205 100 195 100" fill="black"/>
    <text x="200" y="120" text-anchor="middle">Fulcrum</text>
    <line x1="${pos1}" y1="70" x2="${pos1}" y2="100" stroke="red" stroke-width="2"/><text x="${pos1}" y="65" text-anchor="middle">W1=${w1}N</text>
    <line x1="${pos2}" y1="70" x2="${pos2}" y2="100" stroke="red" stroke-width="2"/><text x="${pos2}" y="65" text-anchor="middle">W2=${w2}N</text>
    <text id="d1-text" x="${(pos1+200)/2}" y="95" text-anchor="middle" fill="blue">d1=${d1}cm</text>
    <text id="d2-text" x="${(200+pos2)/2}" y="95" text-anchor="middle" fill="blue">d2=${d2}cm</text>
    <text x="200" y="180" text-anchor="middle">${w1}x${d1} = ${w2}x${d2} → ${m1} = ${m2}Nm → ${status}</text>`;
  }
  
  // 2. PULLEY
  else if(cmd.includes('pulley')){
    svg += `<circle cx="200" cy="50" r="30" fill="none" stroke="black" stroke-width="2"/>
    <line x1="170" y1="50" x2="170" y2="150" stroke="black"/><line x1="230" y1="50" x2="230" y2="150" stroke="black"/>
    <rect x="150" y="150" width="40" height="30" fill="gray"/><rect x="210" y="150" width="40" height="30" fill="gray"/>
    <text x="170" y="195" text-anchor="middle">Effort</text><text x="230" y="195" text-anchor="middle">Load</text>`;
  }
  
  // 3. TRANSFORMER
  else if(cmd.includes('transformer')){
    svg += `<rect x="80" y="70" width="60" height="60" fill="none" stroke="black" stroke-width="2"/>
    <rect x="260" y="70" width="60" height="60" fill="none" stroke="black" stroke-width="2"/>
    <text x="110" y="105" text-anchor="middle">P</text><text x="290" y="105" text-anchor="middle">S</text>
    <text x="110" y="180" text-anchor="middle">Primary</text><text x="290" y="180" text-anchor="middle">Secondary</text>`;
  }
  
  // 4. CONVEX LENS
  else if(cmd.includes('convex lens')){
    svg += `<line x1="50" y1="100" x2="350" y2="100" stroke="black"/>
    <path d="M200 50 Q210 100 200 150 Q190 100 200 50" fill="none" stroke="black" stroke-width="2"/>
    <line x1="120" y1="80" x2="120" y2="120" stroke="red" stroke-width="2"/><text x="120" y="140">Object</text>
    <line x1="280" y1="120" x2="280" y2="80" stroke="red" stroke-width="2"/><text x="280" y="60">Image</text>`;
  }
  
  // 5. V-T GRAPH - BUGFIX: axis labels
  else if(cmd.includes('v-t graph') || cmd.includes('vt graph')){
    svg += `<line x1="50" y1="150" x2="370" y2="150" stroke="black"/><line x1="50" y1="150" x2="50" y2="50" stroke="black"/>
    <line x1="50" y1="150" x2="350" y2="50" stroke="blue" stroke-width="2"/>
    <text id="vt-y-label" x="15" y="100" text-anchor="middle" transform="rotate(-90 15 100)">V (m/s)</text>
    <text id="vt-x-label" x="360" y="165">t (s)</text>
    <text x="200" y="190" text-anchor="middle">a = 2 m/s²</text>`;
  }
  
  // 6. WAVE - BUGFIX: 2 cycles
  else if(cmd.includes('wave')){
    const wl = cmd.match(/wl (\\d+)/)?.[1] || 10;
    const f = cmd.match(/freq (\\d+)/)?.[1] || 5;
    svg += `<line x1="50" y1="100" x2="350" y2="100" stroke="gray" stroke-dasharray="2"/>
    <path d="M50 100 Q75 50 100 100 T150 100 T200 100 T250 100 T300 100" fill="none" stroke="blue" stroke-width="2"/>
    <line x1="100" y1="100" x2="200" y2="100" stroke="red"/><text x="150" y="95" text-anchor="middle">λ=${wl}cm</text>
    <line x1="100" y1="100" x2="100" y2="50" stroke="green" stroke-dasharray="2"/><text x="110" y="75">A</text>
    <text x="100" y="40">Crest</text><text x="200" y="140">Trough</text>
    <text x="200" y="180" text-anchor="middle">λ=${wl}cm f=${f}Hz</text>`;
  }
  
  // 7. BAR MAGNET - BUGFIX: 4 lines + arrows
  else if(cmd.includes('magnet')){
    svg += `<rect x="100" y="90" width="100" height="20" fill="red"/><text x="150" y="104" text-anchor="middle" fill="black" font-size="14">N</text>
    <rect x="200" y="90" width="100" height="20" fill="blue"/><text x="250" y="104" text-anchor="middle" fill="white" font-size="14">S</text>
    <path d="M150 90 Q200 40 250 90" stroke="black" fill="none" marker-end="url(#arrow)"/>
    <path d="M150 110 Q200 160 250 110" stroke="black" fill="none" marker-end="url(#arrow)"/>
    <path d="M150 90 Q175 60 200 90 Q225 60 250 90" stroke="black" fill="none" marker-end="url(#arrow)"/>
    <path d="M150 110 Q175 140 200 110 Q225 140 250 110" stroke="black" fill="none" marker-end="url(#arrow)"/>`;
  }
  
  // 8. REFRACTION - BUGFIX: arcs + arrows
  else if(cmd.includes('refraction')){
    const i = cmd.match(/i (\\d+)/)?.[1] || 40;
    const r = cmd.match(/r (\\d+)/)?.[1] || 25;
    svg += `<line x1="50" y1="100" x2="350" y2="100" stroke="black"/><text x="100" y="90">Air</text><text x="280" y="120">Glass</text>
    <line x1="200" y1="50" x2="200" y2="150" stroke="black" stroke-dasharray="2"/><text x="210" y="60">Normal</text>
    <line x1="150" y1="65" x2="200" y2="100" stroke="red" stroke-width="2" marker-end="url(#arrow)"/>
    <line x1="200" y1="100" x2="250" y2="125" stroke="red" stroke-width="2" marker-end="url(#arrow)"/>
    <circle cx="200" cy="100" r="30" fill="none" stroke="gray" stroke-dasharray="2"/>
    <path d="M200 70 A30 30 0 0 1 221 76" fill="none" stroke="red"/>
    <path d="M200 100 A30 30 0 0 1 214 123" fill="none" stroke="red"/>
    <text x="160" y="75">i=${i}°</text><text x="230" y="115">r=${r}°</text>`;
  }
  
  // 9. OHM'S LAW - BUGFIX: zigzag + V + title
  else if(cmd.includes('ohm')){
    svg += `<text x="210" y="30" text-anchor="middle" font-size="16" font-weight="bold">Ohm's Law Circuit - V = IR</text>
    <line x1="80" y1="100" x2="140" y2="100" stroke="black"/>
    <text x="110" y="85" text-anchor="middle">Battery</text>
    <line x1="110" y1="95" x2="110" y2="105" stroke="black" stroke-width="3"/>
    <line x1="110" y1="98" x2="110" y2="102" stroke="black"/>
    <circle cx="180" cy="100" r="15" fill="none" stroke="black"/><text x="180" y="105" text-anchor="middle">A</text>
    <line x1="195" y1="100" x2="250" y2="100" stroke="black"/>
    <path d="M250 100 L260 90 L270 110 L280 90 L290 110 L300 90 L310 100" stroke="black" fill="none"/>
    <text x="280" y="85" text-anchor="middle">R</text>
    <circle cx="340" cy="100" r="15" fill="none" stroke="black"/><text x="340" y="105" text-anchor="middle">V</text>
    <line x1="355" y1="100" x2="355" y2="140" stroke="black"/>
    <line x1="355" y1="140" x2="80" y2="140" stroke="black"/>
    <line x1="80" y1="140" x2="80" y2="100" stroke="black"/>`;
  }
  
  // 10. INCLINED PLANE - BUGFIX: forces + theta
  else if(cmd.includes('inclined plane')){
    svg += `<text x="210" y="20" text-anchor="middle" font-size="16" font-weight="bold">Inclined Plane - 5kg block</text>
    <polygon points="50 150 350 150 350 50" fill="lightgray" stroke="black"/>
    <rect x="170" y="90" width="30" height="20" fill="gray" transform="rotate(-18 185 100)"/><text x="185" y="104" text-anchor="middle" fill="white" font-size="10">5kg</text>
    <line x1="185" y1="100" x2="185" y2="130" stroke="red" marker-end="url(#arrow)"/><text x="190" y="125">W</text>
    <line x1="185" y1="100" x2="165" y2="85" stroke="blue" marker-end="url(#arrow)"/><text x="155" y="80">R</text>
    <line x1="185" y1="100" x2="215" y2="90" stroke="green" marker-end="url(#arrow)"/><text x="220" y="88">F</text>
    <path d="M200 150 A50 50 0 0 0 185 100" fill="none" stroke="black"/><text x="190" y="145">θ</text>`;
  }
  
  // 11. LEVER
  else if(cmd.includes('lever')){
    svg += `<text x="210" y="30" text-anchor="middle" font-size="16" font-weight="bold">Lever: Class 1</text>
    <line x1="50" y1="100" x2="350" y2="100" stroke="black" stroke-width="3"/>
    <polygon points="200 90 205 100 195 100" fill="black"/><text x="200" y="120" text-anchor="middle">Fulcrum</text>
    <line x1="100" y1="100" x2="100" y2="70" stroke="red" stroke-width="2" marker-end="url(#arrow)"/><text x="100" y="60" text-anchor="middle">Load</text>
    <line x1="300" y1="100" x2="300" y2="70" stroke="green" stroke-width="2" marker-end="url(#arrow)"/><text x="300" y="60" text-anchor="middle">Effort</text>`;
  }
  
  svg += `</svg>`;
  return svg;
}
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    return jsonify({"svg": drawDiagram(data['command'])})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
