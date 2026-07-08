from flask import Flask,request
from groq import Groq
import os
app=Flask(__name__)
GROQ_API_KEY=os.environ.get("GROQ_API_KEY")
client=Groq(api_key=GROQ_API_KEY)
NCDC_SYLLABUS="NCDC UGANDA S1-S4 PHYSICS: S1:Force,Work,Energy,Power,Pressure,Simple Machines,Heat,Light,Sound. S2:Current Electricity,Magnetism,Waves,Properties of Matter. S3:Reflection,Refraction,Lenses,Mirrors,Electrostatics,EM Induction. S4:Atomic,Nuclear,Electronics. EXCLUDE Bio/Chem."

CONVEX_LENS_SVG = """<svg width="500" height="280" style="background:white; border:1px solid #ccc">
<line x1="250" y1="40" x2="250" y2="240" stroke="black" stroke-width="4"/>
<text x="235" y="30" font-size="12">Convex Lens</text>
<line x1="250" y1="100" x2="250" y2="180" stroke="gray" stroke-dasharray="3"/>
<text x="255" y="110" font-size="10">F</text>
<line x1="170" y1="100" x2="170" y2="180" stroke="gray" stroke-dasharray="3"/>
<text x="175" y="110" font-size="10">2F</text>
<line x1="330" y1="100" x2="330" y2="180" stroke="gray" stroke-dasharray="3"/>
<text x="335" y="110" font-size="10">2F</text>
<line x1="90" y1="60" x2="90" y2="220" stroke="black" stroke-width="3"/>
<text x="60" y="50" font-size="12">Object</text>
<line x1="410" y1="140" x2="410" y2="220" stroke="black" stroke-width="3"/>
<text x="415" y="130" font-size="12">Image</text>
<line x1="90" y1="60" x2="250" y2="140" stroke="red" stroke-width="2"/>
<line x1="250" y1="140" x2="410" y2="140" stroke="red" stroke-width="2"/>
<line x1="90" y1="60" x2="250" y2="140" stroke="blue" stroke-width="2"/>
<line x1="250" y1="140" x2="410" y2="180" stroke="blue" stroke-width="2"/>
</svg>"""

OHMS_CIRCUIT_SVG = """<svg width="500" height="280" style="background:white; border:1px solid #ccc">
<rect x="60" y="120" width="50" height="40" stroke="black" fill="white" stroke-width="2"/>
<text x="70" y="145" font-size="14">V</text>
<rect x="180" y="130" width="70" height="20" stroke="black" fill="white" stroke-width="2"/>
<text x="195" y="145" font-size="12">R</text>
<circle cx="320" cy="140" r="18" stroke="black" fill="white" stroke-width="2"/>
<text x="314" y="145" font-size="12">A</text>
<line x1="110" y1="140" x2="180" y2="140" stroke="black" stroke-width="2"/>
<line x1="250" y1="140" x2="302" y2="140" stroke="black" stroke-width="2"/>
<line x1="320" y1="158" x2="320" y2="220" stroke="black" stroke-width="2"/>
<line x1="320" y1="220" x2="85" y2="220" stroke="black" stroke-width="2"/>
<line x1="85" y1="220" x2="85" y2="140" stroke="black" stroke-width="2"/>
<text x="200" y="100" font-size="14">Ohm's Law Circuit: V=IR</text>
</svg>"""

CONCAVE_MIRROR_SVG = """<svg width="500" height="280" style="background:white; border:1px solid #ccc">
<path d="M 250 40 A 100 100 0 0 1 250 240" stroke="black" stroke-width="3" fill="none"/>
<text x="260" y="150" font-size="12">Concave Mirror</text>
<line x1="150" y1="140" x2="350" y2="140" stroke="gray" stroke-dasharray="3"/>
<text x="355" y="145" font-size="10">Principal Axis</text>
<circle cx="150" cy="140" r="4" fill="red"/>
<text x="130" y="130" font-size="10">F</text>
<circle cx="50" cy="140" r="4" fill="blue"/>
<text x="30" y="130" font-size="10">C</text>
<line x1="50" y1="80" x2="50" y2="200" stroke="black" stroke-width="3"/>
<text x="20" y="70" font-size="12">Object</text>
<line x1="50" y1="80" x2="150" y2="140" stroke="red" stroke-width="2"/>
<line x1="150" y1="140" x2="50" y2="200" stroke="red" stroke-width="2"/>
</svg>"""

SYSTEM_PROMPT=f"""You are NCDC Uganda S1-S4 Physics Tutor AI.
LAW 1-UNEB LOCK: If NOT in {NCDC_SYLLABUS} reply: UNEB LOCK: That topic is not in NCDC S1-S4 Physics.
LAW 2-FORMULA FIRST: Given: Formula: Substitution: Answer: with units.
LAW 3: For diagrams, just explain the steps. Do NOT output SVG. The system will show the diagram."""

@app.route("/",methods=["GET","POST"])
def chatbot():
 if request.method=="POST":
  user_input=request.form["question"].lower()
  diagram_to_show = ""
  
  if "convex" in user_input and "lens" in user_input:
      diagram_to_show = CONVEX_LENS_SVG
  elif "ohm" in user_input or "circuit" in user_input:
      diagram_to_show = OHMS_CIRCUIT_SVG
  elif "concave" in user_input and "mirror" in user_input:
      diagram_to_show = CONCAVE_MIRROR_SVG
  
  try:
   completion=client.chat.completions.create(model="llama-3.3-70b-versatile",messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":user_input}],temperature=0.2,max_tokens=800)
   ai_response=completion.choices[0].message.content
   
   if diagram_to_show:
    return f"<html><body style='font-family:Arial;padding:20px;background:#f0f4ff'><h2>NCDC Physics AI</h2><div style='background:white;padding:15px;border-radius:8px;margin-bottom:15px'>{ai_response.replace(chr(10),'<br>')}</div><div style='background:white;padding:15px;border-radius:8px'><b>Diagram:</b><br>{diagram_to_show}</div><br><a href='/' style='text-decoration:none;background:#2563eb;color:white;padding:10px 15px;border-radius:5px'>Ask Another</a></body></html>"
   else: 
    return f"<html><body style='font-family:Arial;padding:20px;background:#f0f4ff'><h2>NCDC Physics AI</h2><div style='background:white;padding:15px;border-radius:8px'>{ai_response.replace(chr(10),'<br>')}</div><br><a href='/' style='text-decoration:none;background:#2563eb;color:white;padding:10px 15px;border-radius:5px'>Ask Another</a></body></html>"
  except Exception as e: return f"Error: {str(e)}<br><a href='/'>Go Back</a>"
 return "<html><body style='font-family:Arial;padding:20px;background:#f0f4ff'><h2>NCDC S1-S4 Physics AI Tutor</h2><p><b>Ask any S1-S4 Physics. Try: convex lens, ohm circuit, concave mirror</b></p><form method=post><input name=question placeholder='Draw ray diagram for convex lens' style='width:400px;padding:10px;border-radius:5px;border:1px solid #ccc'><button type=submit style='padding:10px 15px;background:#2563eb;color:white;border:none;border-radius:5px'>Send</button></form></body></html>"
if __name__=="__main__":app.run(host="0.0.0.0",port=10000)
