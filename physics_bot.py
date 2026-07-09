from flask import Flask,request
from groq import Groq
import os
import traceback # ADD THIS
app=Flask(__name__)
GROQ_API_KEY=os.environ.get("GROQ_API_KEY")
client=Groq(api_key=GROQ_API_KEY)

NCDC_SYLLABUS="""NCDC UGANDA S1-S4 PHYSICS SYLLABUS: S1: Measurement Force Work Energy Pressure Heat Light Sound S2: Current Electricity Magnetism Waves Properties of Matter Static Electricity S3: Mirrors Lenses Optical Instruments Electrostatics Electromagnetism Gas Laws S4: Atomic Physics Nuclear Physics Electronics Modern Physics EXCLUDE: Biology Chemistry Agriculture"""

CONVEX_LENS_BEYOND_2F_SVG = """<svg width="500" height="280" style="background:white; border:1px solid #ccc"><text x="200" y="30" font-size="12" font-weight="bold">Convex Lens - Object beyond 2F</text><line x1="250" y1="40" x2="250" y2="240" stroke="black" stroke-width="4"/><line x1="50" y1="140" x2="450" y2="140" stroke="black"/><line x1="60" y1="70" x2="60" y2="210" stroke="black" stroke-width="3"/><line x1="380" y1="140" x2="380" y2="185" stroke="black" stroke-width="3"/></svg>"""

SYSTEM_PROMPT=f"""You are NCDC Uganda S1-S4 Physics Tutor AI. LAW 1-UNEB LOCK: If question NOT in this syllabus: {NCDC_SYLLABUS} then reply: UNEB LOCK: That topic is not in NCDC S1-S4 Physics. LAW 2-FORMULA FIRST: If numerical use Given: Formula: Substitution: Answer:. Be brief, UNEB style."""

@app.route("/",methods=["GET","POST"])
def chatbot():
 try:
  if request.method=="POST":
   user_input=request.form["question"].lower()
   diagram_to_show = ""
   if "convex" in user_input and "lens" in user_input:
       diagram_to_show = CONVEX_LENS_BEYOND_2F_SVG

   completion=client.chat.completions.create(
       model="llama-3.3-70b-versatile",
       messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":user_input}],
       temperature=0.2,max_tokens=500,timeout=25 # ADD TIMEOUT
   )
   ai_response=completion.choices[0].message.content

   if diagram_to_show:
    return f"<html><body style='font-family:Arial;padding:20px;background:#f0f4ff'><h2>NCDC Physics AI</h2><div style='background:white;padding:15px'>{ai_response.replace(chr(10),'<br>')}</div><div>{diagram_to_show}</div><br><a href='/'>Ask Another</a></body></html>"
   else:
    return f"<html><body style='font-family:Arial;padding:20px;background:#f0f4ff'><h2>NCDC Physics AI</h2><div style='background:white;padding:15px'>{ai_response.replace(chr(10),'<br>')}</div><br><a href='/'>Ask Another</a></body></html>"

  return """<html><body style='font-family:Arial;padding:20px;background:#f0f4ff'><h2>NCDC S1-S4 Physics AI Tutor 🇺🇬</h2><form method=post><input name=question placeholder='Enter physics question' style='width:400px;padding:10px'><button type=submit>Send</button></form></body></html>"""

 except Exception as e:
  print("ERROR OCCURRED:") # THIS WILL SHOW IN LOGS
  print(traceback.format_exc()) # THIS WILL SHOW IN LOGS
  return f"<html><body style='font-family:Arial;padding:20px'><h2>Error</h2><p>{str(e)}</p><a href='/'>Go Back</a></body></html>"

if __name__=="__main__":app.run(host="0.0.0.0",port=10000)
