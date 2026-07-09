from flask import Flask,request
from groq import Groq
import os
app=Flask(__name__)
GROQ_API_KEY=os.environ.get("GROQ_API_KEY")
client=Groq(api_key=GROQ_API_KEY)

NCDC_SYLLABUS="""NCDC UGANDA S1-S4 PHYSICS SYLLABUS:
S1: Introduction to Physics, Measurement: Length Area Volume Mass Time Density, Force: Types Effects Friction Turning Effect, Work Energy Power: Kinetic Potential Conservation Machines, Pressure: Solids Liquids Gases Atmospheric, Simple Machines: Lever Pulley Inclined Plane Wheel & Axle, Heat: Temperature Expansion Heat Transfer Specific Heat, Light: Sources Rectilinear Propagation Reflection Refraction, Sound: Production Propagation Properties Echo
S2: Current Electricity: Cells Circuits Ohm's Law Series Parallel, Magnetism: Magnets Magnetic Field Electromagnets, Waves: Types Properties Sound Waves Light Waves, Properties of Matter: States Molecular Theory Evaporation Boiling, Static Electricity: Charges Field Lightning
S3: Reflection at Curved Surfaces: Concave Convex Mirrors Ray Diagrams, Refraction: Lenses Convex Concave Ray Diagrams Eye, Optical Instruments: Microscope Telescope Camera, Electrostatics: Charging Force Applications, Electromagnetism: EM Induction Electric Motor Generator Transformer, Heat: Gas Laws Thermal Expansion
S4: Atomic Physics: Structure of Atom Radioactivity Half-life, Nuclear Physics: Fission Fusion Applications Hazards, Electronics: Diodes Transistors Logic Gates Cathode Ray Oscilloscope, Modern Physics: Photoelectric Effect X-rays, Revision of S1-S3 Topics for UNEB
EXCLUDE: Biology Chemistry Agriculture"""

CONVEX_LENS_BEYOND_2F_SVG = """<svg width="500" height="280" style="background:white; border:1px solid #ccc">
<line x1="250" y1="40" x2="250" y2="240" stroke="black" stroke-width="4"/><text x="200" y="30" font-size="12" font-weight="bold">Convex Lens - Object beyond 2F</text>
<line x1="50" y1="140" x2="450" y2="140" stroke="black" stroke-width="1"/>
<line x1="170" y1="100" x2="170" y2="180" stroke="gray" stroke-dasharray="4"/><text x="165" y="95" font-size="10">F</text>
<line x1="330" y1="100" x2="330" y2="180" stroke="gray" stroke-dasharray="4"/><text x="335" y="95" font-size="10">F</text>
<line x1="90" y1="100" x2="90" y2="180" stroke="gray" stroke-dasharray="4"/><text x="85" y="95" font-size="10">2F</text>
<line x1="410" y1="100" x2="410" y2="180" stroke="gray" stroke-dasharray="4"/><text x="415" y="95" font-size="10">2F</text>
<line x1="60" y1="70" x2="60" y2="210" stroke="black" stroke-width="3"/><polygon points="60,70 55,80 65,80" fill="black"/><text x="35" y="65" font-size="12" font-weight="bold">Object</text>
<line x1="380" y1="140" x2="380" y2="185" stroke="black" stroke-width="3"/><polygon points="380,185 375,175 385,175" fill="black"/><text x="385" y="135" font-size="12" font-weight="bold">Image</text>
<line x1="60" y1="70" x2="250" y2="70" stroke="red" stroke-width="2"/><line x1="250" y1="70" x2="330" y2="140" stroke="red" stroke-width="2"/><line x1="330" y1="140" x2="380" y2="185" stroke="red" stroke-width="2"/>
<line x1="60" y1="70" x2="250" y2="140" stroke="blue" stroke-width="2"/><line x1="250" y1="140" x2="380" y2="185" stroke="blue" stroke-width="2"/>
<line x1="60" y1="70" x2="170" y2="140" stroke="green" stroke-width="2"/><line x1="170" y1="140" x2="250" y2="140" stroke="green" stroke-width="2"/><line x1="250" y1="140" x2="380" y2="185" stroke="green" stroke-width="2"/>
<circle cx="380" cy="185" r="3" fill="purple"/>
</svg>"""

CONCAVE_MIRROR_SVG = """<svg width="500" height="280" style="background:white; border:1px solid #ccc">
<text x="200" y="30" font-size="12" font-weight="bold">Concave Mirror - Object beyond C</text>
<line x1="50" y1="140" x2="450" y2="140" stroke="black" stroke-width="1"/><text x="455" y="145" font-size="10">Principal Axis</text>
<path d="M 250 40 A 100 100 0 0 1 250 240" stroke="black" stroke-width="3" fill="none"/>
<circle cx="150" cy="140" r="4" fill="red"/><text x="130" y="130" font-size="10">F</text>
<circle cx="50" cy="140" r="4" fill="blue"/><text x="30" y="130" font-size="10">C</text>
<line x1="20" y1="70" x2="20" y2="210" stroke="black" stroke-width="3"/><polygon points="20,70 15,80 25,80" fill="black"/><text x="5" y="65" font-size="12" font-weight="bold">Object</text>
<line x1="120" y1="140" x2="120" y2="170" stroke="black" stroke-width="3"/><polygon points="120,170 115,160 125,160" fill="black"/><text x="125" y="135" font-size="12" font-weight="bold">Image</text>
<line x1="20" y1="70" x2="150" y2="140" stroke="red" stroke-width="2"/><line x1="150" y1="140" x2="120" y2="170" stroke="red" stroke-width="2"/>
<line x1="20" y1="70" x2="250" y2="140" stroke="blue" stroke-width="2"/><line x1="250" y1="140" x2="120" y2="170" stroke="blue" stroke-width="2"/>
<line x1="20" y1="70" x2="150" y2="140" stroke="green" stroke-width="2"/><line x1="150" y1="140" x2="250" y2="140" stroke="green" stroke-width="2"/><line x1="250" y1="140" x2="120" y2="170" stroke="green" stroke-width="2"/>
</svg>"""

OHMS_CIRCUIT_SVG = """<svg width="500" height="280" style="background:white; border:1px solid #ccc">
<text x="180" y="40" font-size="14" font-weight="bold">Ohm's Law Circuit: V = IR</text>
<rect x="60" y="120" width="50" height="40" stroke="black" fill="white" stroke-width="2"/><text x="70" y="145" font-size="14">V</text>
<rect x="180" y="130" width="70" height="20" stroke="black" fill="white" stroke-width="2"/><text x="195" y="145" font-size="12">R</text>
<circle cx="320" cy="140" r="18" stroke="black" fill="white" stroke-width="2"/><text x="314" y="145" font-size="12">A</text>
<line x1="110" y1="140" x2="180" y2="140" stroke="black" stroke-width="2"/>
<line x1="250" y1="140" x2="302" y2="140" stroke="black" stroke-width="2"/>
<line x1="320" y1="158" x2="320" y2="220" stroke="black" stroke-width="2"/>
<line x1="320" y1="220" x2="85" y2="220" stroke="black" stroke-width="2"/>
<line x1="85" y1="220" x2="85" y2="160" stroke="black" stroke-width="2"/>
</svg>"""

SYSTEM_PROMPT=f"""You are NCDC Uganda S1-S4 Physics Tutor AI.
LAW 1-UNEB LOCK: If question NOT in this syllabus: {NCDC_SYLLABUS} then reply exactly: UNEB LOCK: That topic is not in NCDC S1-S4 Physics.
LAW 2-FORMULA FIRST: If numerical, use format: Given: Formula: Substitution: Answer: with units.
LAW 3-DIAGRAMS: For ray diagrams or circuits, explain in text. Do NOT output SVG code. The system will show diagram.
Be brief, clear, UNEB marking style."""

@app.route("/",methods=["GET","POST"])
def chatbot():
 try:
  if request.method=="POST":
   user_input=request.form["question"].lower()
   diagram_to_show = ""

   if "convex" in user_input and "lens" in user_input:
       diagram_to_show = CONVEX_LENS_BEYOND_2F_SVG
   elif "concave" in user_input and "mirror" in user_input:
       diagram_to_show = CONCAVE_MIRROR_SVG
   elif "ohm" in user_input or "circuit" in user_input or "current" in user_input:
       diagram_to_show = OHMS_CIRCUIT_SVG

   completion=client.chat.completions.create(
       model="llama-3.3-70b-versatile",
       messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":user_input}],
       temperature=0.2,max_tokens=800
   )
   ai_response=completion.choices[0].message.content

   if diagram_to_show:
    return f"<html><body style='font-family:Arial;padding:20px;background:#f0f4ff'><h2>NCDC S1-S4 Physics AI</h2><div style='background:white;padding:15px;border-radius:8px;margin-bottom:15px'>{ai_response.replace(chr(10),'<br>')}</div><div style='background:white;padding:15px;border-radius:8px'><b>Diagram:</b><br>{diagram_to_show}</div><br><a href='/' style='text-decoration:none;background:#2563eb;color:white;padding:10px 15px;border-radius:5px'>Ask Another</a></body></html>"
   else:
    return f"<html><body style='font-family:Arial;padding:20px;background:#f0f4ff'><h2>NCDC S1-S4 Physics AI</h2><div style='background:white;padding:15px;border-radius:8px'>{ai_response.replace(chr(10),'<br>')}</div><br><a href='/' style='text-decoration:none;background:#2563eb;color:white;padding:10px 15px;border-radius:5px'>Ask Another</a></body></html>"

  return """<html><body style='font-family:Arial;padding:20px;background:#f0f4ff'>
  <h2>NCDC S1-S4 Physics AI Tutor 🇺🇬</h2>
  <p><b>Ask any S1-S4 Physics Topic</b><br>Examples: convex lens, concave mirror, ohm circuit, transformer, radioactivity</p>
  <form method=post>
  <input name=question placeholder='Enter your physics question' style='width:400px;padding:10px;border-radius:5px;border:1px solid #ccc'>
  <button type=submit style='padding:10px 15px;background:#2563eb;color:white;border:none;border-radius:5px'>Send</button>
  </form></body></html>"""

 except Exception as e:
  return f"<html><body style='font-family:Arial;padding:20px'><h2>Error</h2><p>{str(e)}</p><a href='/'>Go Back</a></body></html>"

if __name__=="__main__":app.run(host="0.0.0.0",port=10000)
