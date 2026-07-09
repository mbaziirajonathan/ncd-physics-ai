from flask import Flask,request
from groq import Groq
import os,threading,time,requests
app=Flask(__name__)
def keep_alive():
    while True:time.sleep(840)
    try:requests.get("https://ncd-physics-ai.onrender.com")
    except:pass
threading.Thread(target=keep_alive,daemon=True).start()

GROQ_API_KEY=os.environ.get("GROQ_API_KEY")
client=Groq(api_key=GROQ_API_KEY)

NCDC_SYLLABUS="""S1:Measurement,Force,Work Energy Power,Pressure,Simple Machines,Heat,Light,Sound
S2:Current Electricity,Magnetism,Waves,Properties of Matter,Static Electricity
S3:Mirrors,Lenses,Optical Instruments,Electrostatics,Electromagnetism,Gas Laws
S4:Atomic Physics,Nuclear Physics,Electronics,Electricity,Ohm's Law,Transformers,Modern Physics
EXCLUDE:Biology Chemistry Agriculture"""

# MINIMIZED DIAGRAMS - 350x200
CONVEX= """<svg width="350" height="200"><text x="90" y="20" font-size="12">Convex Lens: Obj>2F</text><line x1="30" y1="100" x2="320" y2="100"/><line x1="175" y1="50" x2="175" y2="150" stroke-width="3"/><text x="165" y="45">Lens</text><line x1="115" y1="95" x2="115" y2="105"/><text x="110" y="90">F</text><line x1="235" y1="95" x2="235" y2="105"/><text x="240" y="90">F</text><line x1="50" y1="70" x2="50" y2="130" stroke-width="3"/><text x="10" y="65">Obj</text><line x1="260" y1="100" x2="260" y2="120" stroke-width="3"/><text x="265" y="95">Img</text><line x1="50" y1="70" x2="175" y2="70" stroke="red"/><line x1="175" y1="70" x2="235" y2="100" stroke="red"/><line x1="235" y1="100" x2="260" y2="120" stroke="red"/><line x1="50" y1="70" x2="175" y2="100" stroke="blue"/><line x1="175" y1="100" x2="260" y2="120" stroke="blue"/></svg>"""

CONCAVE= """<svg width="350" height="200"><text x="80" y="20" font-size="12">Concave Mirror: Obj>C</text><line x1="30" y1="100" x2="320" y2="100"/><path d="M 175 60 A 80 80 0 0 1 175 140" stroke-width="3" fill="none"/><text x="180" y="55">Mirror</text><circle cx="95" cy="100" r="2" fill="red"/><text x="90" y="95">F</text><circle cx="15" cy="100" r="2" fill="blue"/><text x="5" y="95">C</text><line x1="10" y1="70" x2="10" y2="130" stroke-width="3"/><text x="2" y="65">Obj</text><line x1="70" y1="100" x2="70" y2="115" stroke-width="3"/><text x="75" y="95">Img</text><line x1="10" y1="70" x2="95" y2="100" stroke="red"/><line x1="95" y1="100" x2="70" y2="115" stroke="red"/><line x1="10" y1="70" x2="175" y2="100" stroke="blue"/><line x1="175" y1="100" x2="70" y2="115" stroke="blue"/></svg>"""

OHM= """<svg width="350" height="200"><text x="110" y="20" font-size="12">Ohm's Law: V=IR</text><rect x="40" y="80" width="40" height="30" fill="white" stroke-width="2"/><text x="50" y="100">V</text><rect x="120" y="85" width="50" height="20" fill="white"/><text x="135" y="100">R</text><circle cx="220" cy="95" r="12" fill="white" stroke-width="2"/><text x="215" y="100">A</text><line x1="80" y1="95" x2="120" y2="95" stroke-width="2"/><line x1="170" y1="95" x2="208" y2="95" stroke-width="2"/><line x1="220" y1="107" x2="220" y2="150" stroke-width="2"/><line x1="220" y1="150" x2="60" y2="150" stroke-width="2"/><line x1="60" y1="150" x2="60" y2="110" stroke-width="2"/></svg>"""

MOTOR= """<svg width="350" height="200"><text x="90" y="20" font-size="12">DC Electric Motor</text><rect x="120" y="70" width="80" height="60" fill="lightgray" stroke-width="2"/><text x="140" y="105">Coil</text><line x1="100" y1="100" x2="120" y2="100" stroke-width="2"/><line x1="200" y1="100" x2="220" y2="100" stroke-width="2"/><text x="85" y="95">N</text><text x="225" y="95">S</text><circle cx="100" cy="100" r="15" fill="none" stroke="black"/><circle cx="220" cy="100" r="15" fill="none" stroke="black"/></svg>"""

TRANS= """<svg width="350" height="200"><text x="100" y="20" font-size="12">Transformer</text><rect x="60" y="70" width="30" height="60" fill="lightgray"/><text x="65" y="105">P</text><rect x="200" y="70" width="30" height="60" fill="lightgray"/><text x="205" y="105">S</text><path d="M 90 80 Q 145 60 200 80" stroke="black" fill="none"/><path d="M 90 100 Q 145 100 200 100" stroke="black" fill="none"/><path d="M 90 120 Q 145 140 200 120" stroke="black" fill="none"/></svg>"""

PENDULUM= """<svg width="350" height="200"><text x="100" y="20" font-size="12">Simple Pendulum</text><line x1="175" y1="40" x2="175" y2="140" stroke-width="2"/><circle cx="175" cy="150" r="15" stroke-width="2" fill="gray"/><text x="160" y="35">Pivot</text><line x1="175" y1="40" x2="135" y2="140" stroke="red" stroke-dasharray="3"/><text x="120" y="90">θ</text></svg>"""

NUCLEAR= """<svg width="350" height="200"><text x="90" y="20" font-size="12">Nuclear Fission</text><circle cx="175" cy="100" r="25" fill="orange"/><text x="165" y="105">U-235</text><path d="M 175 75 L 175 40" stroke="red" stroke-width="2"/><text x="165" y="35">n</text><path d="M 155 100 L 120 100" stroke="blue" stroke-width="2"/><path d="M 195 100 L 230 100" stroke="green" stroke-width="2"/><text x="100" y="100">Ba</text><text x="235" y="100">Kr</text><text x="165" y="130">+3n +Energy</text></svg>"""

SYSTEM_PROMPT=f"""You are NCDC Uganda S1-S4 Physics Tutor AI.
LAW 1-UNEB LOCK: If NOT in {NCDC_SYLLABUS} reply: UNEB LOCK: That topic is not in NCDC S1-S4 Physics.
LAW 2-FORMULA FIRST: For Ohm's Law and numericals use Given: Formula: Substitution: Answer: with units.
LAW 3-DIAGRAMS: Explain in text. System shows diagram.
Be brief, UNEB style, max 120 words."""

@app.route("/",methods=["GET","POST"])
def chatbot():
 try:
  if request.method=="POST":
   q=request.form["question"].lower()
   d=""
   if "convex" in q and "lens" in q:d=CONVEX
   elif "concave" in q and "mirror" in q:d=CONCAVE
   elif "ohm" in q or "circuit" in q or "electricity" in q:d=OHM
   elif "motor" in q:d=MOTOR
   elif "transformer" in q:d=TRANS
   elif "pendulum" in q:d=PENDULUM
   elif "nuclear" in q or "fission" in q:d=NUCLEAR
   
   r=client.chat.completions.create(model="llama-3.3-70b-versatile",messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":q}],temperature=0.2,max_tokens=350,timeout=20).choices[0].message.content
   
   if d:return f"<html><body style='font-family:Arial;padding:20px;background:#f0f4ff'><h2>NCDC Physics AI 🇺🇬</h2><div style='background:white;padding:15px;border-radius:8px'>{r.replace(chr(10),'<br>')}</div><div style='background:white;padding:15px;border-radius:8px;margin-top:10px'>{d}</div><br><a href='/' style='background:#2563eb;color:white;padding:10px 15px;border-radius:5px;text-decoration:none'>Ask Another</a></body></html>"
   else:return f"<html><body style='font-family:Arial;padding:20px;background:#f0f4ff'><h2>NCDC Physics AI 🇺🇬</h2><div style='background:white;padding:15px;border-radius:8px'>{r.replace(chr(10),'<br>')}</div><br><a href='/' style='background:#2563eb;color:white;padding:10px 15px;border-radius:5px;text-decoration:none'>Ask Another</a></body></html>"
  return """<html><body style='font-family:Arial;padding:20px;background:#f0f4ff'><h2>NCDC S1-S4 Physics AI Tutor 🇺🇬</h2><p><b>Try S4:</b> ohm's law, transformer, nuclear fission<br><b>Try S1-S3:</b> convex lens, concave mirror, motor, pendulum</p><form method=post><input name=question style='width:400px;padding:10px'><button type=submit style='padding:10px;background:#2563eb;color:white;border:none'>Send</button></form></body></html>"""
 except Exception as e:return f"<html><body><h2>Error</h2><p>{e}</p></body></html>"
if __name__=="__main__":app.run(host="0.0.0.0",port=10000)
