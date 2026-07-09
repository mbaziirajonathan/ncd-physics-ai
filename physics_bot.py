from flask import Flask,request
from groq import Groq
import os,threading,time,requests
app=Flask(__name__)

def keep_alive():
 while True:
  time.sleep(840)
  try:requests.get("https://ncd-physics-ai.onrender.com")
  except:pass
threading.Thread(target=keep_alive,daemon=True).start()

GROQ_API_KEY=os.environ.get("GROQ_API_KEY")
client=Groq(api_key=GROQ_API_KEY)

NCDC_SYLLABUS="""S1:Measurement,Force,Work Energy Power,Pressure,Simple Machines,Heat,Light,Sound
S2:Current Electricity,Magnetism,Waves,Properties of Matter,Static Electricity
S3:Mirrors,Lenses,Optical Instruments,Electrostatics,Electromagnetism,Gas Laws
S4:Atomic Physics,Nuclear Physics,Electronics,Electricity,Ohm's Law,Transformers,Modern Physics"""

# ====== LOGIC: SVG GENERATOR FUNCTIONS ======
def svg_lever():
 return '''<svg width="100%" viewBox="0 0 400 200" style="background:white;border-radius:8px">
 <line x1="50" y1="100" x2="350" y2="100" stroke="black" stroke-width="5"/>
 <polygon points="200,100 190,120 210,120" fill="gray"/><text x="195" y="135">Fulcrum</text>
 <line x1="100" y1="100" x2="100" y2="60" stroke="#e63946" stroke-width="4"/><text x="85" y="50" fill="#e63946" font-weight="bold">Effort</text>
 <line x1="300" y1="100" x2="300" y2="50" stroke="#457b9d" stroke-width="4"/><text x="285" y="40" fill="#457b9d" font-weight="bold">Load</text>
 <text x="200" y="25" text-anchor="middle" font-size="18" font-weight="bold">Simple Lever</text></svg>'''

def svg_incline():
 return '''<svg width="100%" viewBox="0 0 400 250" style="background:white;border-radius:8px">
 <polygon points="50,200 350,200 350,100" fill="#f1faee" stroke="black" stroke-width="3"/>
 <rect x="180" y="140" width="40" height="30" fill="#a8dadc" stroke="black" transform="rotate(-18 200 155)"/>
 <line x1="200" y1="155" x2="200" y2="125" stroke="#e63946" stroke-width="3"/><text x="205" y="120" fill="#e63946">N</text>
 <line x1="200" y1="155" x2="170" y2="155" stroke="#f4a261" stroke-width="3"/><text x="145" y="160" fill="#f4a261">f</text>
 <line x1="200" y1="155" x2="200" y2="185" stroke="#457b9d" stroke-width="3"/><text x="205" y="200" fill="#457b9d">mg</text>
 <text x="200" y="30" text-anchor="middle" font-size="18" font-weight="bold">Block on Incline</text></svg>'''

def svg_ohm():
 return '''<svg width="100%" viewBox="0 0 400 200" style="background:white;border-radius:8px">
 <rect x="50" y="90" width="60" height="20" fill="white" stroke="black" stroke-width="2"/><text x="70" y="104" text-anchor="middle">V</text>
 <line x1="110" y1="100" x2="160" y2="100" stroke="black" stroke-width="2"/>
 <rect x="160" y="90" width="60" height="20" fill="white" stroke="black" stroke-width="2"/><text x="190" y="104" text-anchor="middle">R</text>
 <line x1="220" y1="100" x2="270" y2="100" stroke="black" stroke-width="2"/>
 <rect x="270" y="90" width="60" height="20" fill="white" stroke="black" stroke-width="2"/><text x="300" y="104" text-anchor="middle">A</text>
 <polyline points="330,100 330,150 50,150 50,110" fill="none" stroke="black" stroke-width="2"/>
 <text x="200" y="25" text-anchor="middle" font-size="18" font-weight="bold">Series Circuit</text></svg>'''

def svg_prism():
 return '''<svg width="100%" viewBox="0 0 400 200" style="background:white;border-radius:8px">
 <polygon points="200,50 280,150 120,150" fill="none" stroke="black" stroke-width="3"/>
 <line x1="50" y1="100" x2="200" y2="100" stroke="black" stroke-width="3"/>
 <line x1="200" y1="100" x2="320" y2="70" stroke="red" stroke-width="2"/>
 <line x1="200" y1="100" x2="320" y2="100" stroke="green" stroke-width="2"/>
 <line x1="200" y1="100" x2="320" y2="130" stroke="blue" stroke-width="2"/>
 <text x="30" y="105">White</text><text x="330" y="75" fill="red">R</text>
 <text x="330" y="105" fill="green">G</text><text x="330" y="135" fill="blue">V</text>
 <text x="200" y="25" text-anchor="middle" font-size="18" font-weight="bold">Prism Dispersion</text></svg>'''

def svg_convex():
 return '''<svg width="100%" viewBox="0 0 400 200" style="background:white;border-radius:8px">
 <line x1="0" y1="100" x2="400" y2="100" stroke="gray" stroke-dasharray="5,5"/>
 <path d="M200,50 Q220,100 200,150 Q180,100 200,50" fill="none" stroke="black" stroke-width="4"/>
 <text x="205" y="105">Lens</text>
 <line x1="80" y1="100" x2="80" y2="70" stroke="#e63946" stroke-width="3"/><text x="65" y="65" fill="#e63946">Object</text>
 <line x1="80" y1="70" x2="200" y2="100" stroke="#e63946" stroke-width="2"/>
 <line x1="200" y1="100" x2="320" y2="70" stroke="#457b9d" stroke-width="2"/>
 <line x1="320" y1="70" x2="320" y2="70" stroke="#457b9d" stroke-width="3"/><text x="325" y="65" fill="#457b9d">Image</text>
 <line x1="120" y1="100" x2="120" y2="95" stroke="black"/><text x="115" y="90">F</text>
 <line x1="280" y1="100" x2="280" y2="95" stroke="black"/><text x="275" y="90">F</text>
 <text x="200" y="25" text-anchor="middle" font-size="18" font-weight="bold">Convex Lens</text></svg>'''

def svg_concave():
 return '''<svg width="100%" viewBox="0 0 400 200" style="background:white;border-radius:8px">
 <line x1="0" y1="100" x2="400" y2="100" stroke="gray" stroke-dasharray="5,5"/>
 <path d="M200,50 Q180,100 200,150 Q220,100 200,50" fill="none" stroke="black" stroke-width="4"/>
 <text x="205" y="105">Mirror</text>
 <line x1="80" y1="100" x2="80" y2="70" stroke="#e63946" stroke-width="3"/><text x="65" y="65" fill="#e63946">Object</text>
 <line x1="80" y1="70" x2="200" y2="100" stroke="#e63946" stroke-width="2"/>
 <line x1="200" y1="100" x2="120" y2="70" stroke="#457b9d" stroke-width="2" stroke-dasharray="5,5"/>
 <line x1="120" y1="70" x2="120" y2="70" stroke="#457b9d" stroke-width="3"/><text x="90" y="65" fill="#457b9d">Virtual Image</text>
 <text x="200" y="25" text-anchor="middle" font-size="18" font-weight="bold">Concave Mirror</text></svg>'''

def svg_transformer():
 return '''<svg width="100%" viewBox="0 0 400 200" style="background:white;border-radius:8px">
 <rect x="80" y="70" width="40" height="60" fill="#8d99ae" stroke="black" stroke-width="2"/>
 <rect x="280" y="70" width="40" height="60" fill="#8d99ae" stroke="black" stroke-width="2"/>
 <text x="85" y="110" font-size="12">N1</text><text x="285" y="110" font-size="12">N2</text>
 <path d="M120,80 Q160,80 160,100 Q160,120 120,120" fill="none" stroke="#e63946" stroke-width="2"/>
 <path d="M120,90 Q170,90 170,100 Q170,110 120,110" fill="none" stroke="#e63946" stroke-width="2"/>
 <path d="M280,80 Q240,80 240,100 Q240,120 280,120" fill="none" stroke="#457b9d" stroke-width="2"/>
 <path d="M280,90 Q230,90 230,100 Q230,110 280,110" fill="none" stroke="#457b9d" stroke-width="2"/>
 <line x1="50" y1="100" x2="80" y2="100" stroke="black" stroke-width="2"/>
 <line x1="320" y1="100" x2="350" y2="100" stroke="black" stroke-width="2"/>
 <text x="30" y="105">Vin</text><text x="355" y="105">Vout</text>
 <text x="200" y="25" text-anchor="middle" font-size="18" font-weight="bold">Step-up Transformer</text></svg>'''

def get_svg(name):
 svgs={"lever":svg_lever(),"incline":svg_incline(),"ohm":svg_ohm(),"prism":svg_prism(),
       "convex":svg_convex(),"concave":svg_concave(),"transformer":svg_transformer()}
 return svgs.get(name,"")

SYSTEM_PROMPT=f"""You are NCDC Uganda S1-S4 Physics Tutor. 
If question NOT in {NCDC_SYLLABUS} reply: UNEB LOCK: That topic is not in NCDC S1-S4 Physics.
For numericals use: Given: Formula: Substitution: Answer:
Be brief. Max 120 words."""

@app.route("/",methods=["GET","POST"])
def chatbot():
 try:
  if request.method=="POST":
   q=request.form["question"].lower()
   svg=""
   if "incline" in q:svg=get_svg("incline")
   elif "lever" in q:svg=get_svg("lever")
   elif "ohm" in q or "circuit" in q:svg=get_svg("ohm")
   elif "prism" in q:svg=get_svg("prism")
   elif "convex" in q:svg=get_svg("convex")
   elif "concave" in q:svg=get_svg("concave")
   elif "transformer" in q:svg=get_svg("transformer")
   
   r=client.chat.completions.create(model="llama-3.3-70b-versatile",messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":q}],temperature=0.2,max_tokens=350).choices[0].message.content
    
   return f"<html><body style='font-family:Arial;padding:20px;background:#f0f4ff'><h2>NCDC Physics AI 🇺🇬</h2><div style='background:white;padding:15px;border-radius:8px'>{r.replace(chr(10),'<br>')}</div>{svg}<br><a href='/'>Ask Another</a></body></html>"
  return """<html><body style='font-family:Arial;padding:20px;background:#f0f4ff'><h2>NCDC S1-S4 Physics AI 🇺🇬</h2>
  <p><b>Working Diagrams:</b> lever, incline, ohm, prism, convex, concave, transformer</p>
  <form method=post><input name=question style='width:400px;padding:10px' placeholder='Ask: draw convex lens diagram'>
  <button type=submit>Send</button></form></body></html>"""
 except Exception as e:return f"<h2>Error</h2><p>{e}</p><br><a href='/'>Back</a>"
if __name__=="__main__":app.run(host="0.0.0.0",port=10000)
