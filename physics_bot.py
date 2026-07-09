from flask import Flask,request
from groq import Groq
import os,threading,time,requests
app=Flask(__name__)

# Keep Render awake
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
S4:Atomic Physics,Nuclear Physics,Electronics,Electricity,Ohm's Law,Transformers,Modern Physics
EXCLUDE:Biology Chemistry Agriculture"""

SYSTEM_PROMPT=f"""You are an Expert Physics Tutor and Technical Illustrator for NCDC Uganda S1-S4.

CORE RULES:
1. UNEB LOCK: If question is NOT in this syllabus: {NCDC_SYLLABUS} then reply exactly: UNEB LOCK: That topic is not in NCDC S1-S4 Physics.
2. FORMULA FIRST: For numericals use format: Given: Formula: Substitution: Answer: with units.
3. DIAGRAM CODE: When user asks for ANY diagram, DO NOT generate an image. Instead output BOTH:
   A. PYTHON: A complete runnable Matplotlib code block with numpy. Calculate vector components. Label vectors N, f, mg, T. Mark angles. Use ax.axis('off')
   B. LATEX: The complete TikZ code block in \\begin{{tikzpicture}}... \\end{{tikzpicture}} for academic publishing.
4. Keep explanations brief. UNEB 4-mark style. Max 250 words total.

Example: For "Block on incline with friction" calculate mg*sin(theta) and mg*cos(theta) internally first."""

@app.route("/",methods=["GET","POST"])
def chatbot():
 try:
  if request.method=="POST":
   q=request.form["question"]
   completion=client.chat.completions.create(
       model="llama-3.3-70b-versatile",
       messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":q}],
       temperature=0.1,max_tokens=1200,timeout=25
   )
   ai_response=completion.choices[0].message.content

   return f"""<!DOCTYPE html><html><head><title>NCDC Physics AI</title>
   <style>body{{font-family:Arial;padding:20px;background:#f0f4ff}}
  .box{{background:white;padding:20px;border-radius:10px;white-space:pre-wrap}}
   input{{width:70%;padding:12px}} button{{padding:12px 20px;background:#2563eb;color:white;border:none;border-radius:5px}}</style>
   </head><body>
   <h2>NCDC S1-S4 Physics AI + Technical Illustrator 🇺🇬</h2>
   <div class="box">{ai_response}</div><br>
   <a href="/" style="text-decoration:none">Ask Another Question</a>
   </body></html>"""

  return """<!DOCTYPE html><html><head><title>NCDC Physics AI</title>
  <style>body{{font-family:Arial;padding:20px;background:#f0f4ff}}
  input{{width:70%;padding:12px}} button{{padding:12px 20px;background:#2563eb;color:white;border:none;border-radius:5px}}</style>
  </head><body>
  <h2>NCDC S1-S4 Physics AI + Technical Illustrator 🇺🇬</h2>
  <p><b>Examples:</b><br>1. Draw free body diagram of block on incline 30 degrees with friction<br>
    2. Draw ray diagram for convex lens<br>3. State Ohm's Law and solve: V=10V, R=5ohm</p>
  <form method=post>
  <input name="question" placeholder="Enter your physics question">
  <button type="submit">Send</button>
  </form></body></html>"""

 except Exception as e:
  return f"<h2>Error</h2><p>{str(e)}</p><a href='/'>Go Back</a>"

if __name__=="__main__":
    app.run(host="0.0.0.0",port=10000)
