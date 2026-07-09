from flask import Flask,request,send_file
from groq import Groq
import os,threading,time,requests,io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
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

# ====== 15 HARDCODED DIAGRAM FUNCTIONS S1-S4 ======
def draw_incline():
 fig,ax=plt.subplots(figsize=(6,5));angle=30;theta=np.radians(angle);length=6
 x_ramp=np.array([0,length*np.cos(theta)]);y_ramp=np.array([0,length*np.sin(theta)])
 ax.plot(x_ramp,y_ramp,'k-',lw=3);x_c=3*np.cos(theta);y_c=3*np.sin(theta)
 rect=plt.Rectangle((x_c-0.5,y_c-0.4),1,0.8,angle=angle,facecolor='lightblue',edgecolor='black');ax.add_patch(rect)
 ax.quiver(x_c,y_c,0,1.5,angles='xy',scale_units='xy',scale=1,color='red')
 ax.quiver(x_c,y_c,-1,0,angles='xy',scale_units='xy',scale=1,color='orange')
 ax.quiver(x_c,y_c,0,-2,angles='xy',scale_units='xy',scale=1,color='blue')
 ax.text(x_c+0.2,y_c+1.7,'N',color='red');ax.text(x_c-1.3,y_c+0.2,'f',color='orange');ax.text(x_c+0.2,y_c-2.5,'mg',color='blue')
 ax.set_title('FBD: Block on Incline 30°');ax.axis('off')
 img=io.BytesIO();plt.savefig(img,format='png',bbox_inches='tight');plt.close();img.seek(0);return img

def draw_lever():
 fig,ax=plt.subplots(figsize=(6,4));ax.plot([0,6],[1,1],'k-',lw=4);ax.plot([3,3],[0,1],'k--')
 ax.plot([1,1],[1,2],'k-',lw=3);ax.plot([5,5],[1,2.5],'k-',lw=3)
 ax.text(1,2.2,'Effort');ax.text(5,2.7,'Load');ax.text(3,0.2,'Fulcrum')
 ax.set_title('Simple Lever');ax.axis('off')
 img=io.BytesIO();plt.savefig(img,format='png',bbox_inches='tight');plt.close();img.seek(0);return img

def draw_wave():
 fig,ax=plt.subplots(figsize=(6,3));x=np.linspace(0,4*np.pi,200);y=np.sin(x)
 ax.plot(x,y,'b-',lw=2);ax.axhline(0,color='black',lw=0.5)
 ax.text(2,1.2,'Amplitude');ax.text(6,0.2,'Wavelength λ')
 ax.set_title('Transverse Wave');ax.axis('off')
 img=io.BytesIO();plt.savefig(img,format='png',bbox_inches='tight');plt.close();img.seek(0);return img

def draw_ohm():
 fig,ax=plt.subplots(figsize=(6,4));ax.plot([1,2],[2,2],'k-',lw=2);ax.plot([3,4],[2,2],'k-',lw=2)
 ax.add_patch(plt.Rectangle((2,1.7),0.5,0.6,fill=False,lw=2));ax.text(2.15,1.9,'R')
 ax.add_patch(plt.Rectangle((1,1.7),0.5,0.6,fill=False,lw=2));ax.text(1.15,1.9,'V')
 ax.plot([4,4],[2,1],[2,1],'k-',lw=2);ax.plot([2,1],[1,1],'k-',lw=2);ax.plot([1,1],[1,2],'k-',lw=2)
 ax.text(3.5,2.2,'A',bbox=dict(facecolor='white',edgecolor='black'));ax.set_title("Ohm's Law Circuit")
 ax.axis('off')
 img=io.BytesIO();plt.savefig(img,format='png',bbox_inches='tight');plt.close();img.seek(0);return img

def draw_convex():
 fig,ax=plt.subplots(figsize=(6,4));ax.axhline(0,color='black')
 ax.plot([3,3],[-1,1],'k-',lw=3);ax.text(2.8,1.1,'Lens')
 ax.plot([1,0],[0.5,0],'r-');ax.plot([1,0],[-0.5,0],'r-');ax.text(1,0.6,'Object')
 ax.plot([3,5],[0,0.5],'b-');ax.plot([3,5],[0,-0.5],'b-');ax.text(5,0.6,'Real Image')
 ax.plot([2,3],[0,0],'k--');ax.plot([3,4],[0,0],'k--');ax.text(2,0.2,'F');ax.text(4,0.2,'F')
 ax.set_title('Convex Lens: Object beyond 2F');ax.axis('off')
 img=io.BytesIO();plt.savefig(img,format='png',bbox_inches='tight');plt.close();img.seek(0);return img

def draw_concave():
 fig,ax=plt.subplots(figsize=(6,4));ax.axhline(0,color='black')
 theta=np.linspace(-np.pi/2,np.pi/2,100);x=2+np.cos(theta);y=np.sin(theta);ax.plot(x,y,'k-',lw=3)
 ax.plot([0,0],[0.5,-0.5],'k-',lw=3);ax.text(-0.2,0.6,'Object')
 ax.plot([0,1],[0.5,0],'r-');ax.plot([0,1],[-0.5,0],'r-')
 ax.plot([1,2],[0,0],'b-');ax.text(1,0.2,'Virtual Image')
 ax.set_title('Concave Mirror');ax.axis('off')
 img=io.BytesIO();plt.savefig(img,format='png',bbox_inches='tight');plt.close();img.seek(0);return img

def draw_motor():
 fig,ax=plt.subplots(figsize=(6,4));ax.add_patch(plt.Rectangle((2,1.5),2,1,fill=False,lw=2))
 ax.text(2.8,2,'Coil');ax.plot([1,2],[2,2],'k-');ax.plot([4,5],[2,2],'k-')
 ax.text(0.8,2,'N');ax.text(5.2,2,'S');ax.arrow(3,1.5,0,-0.5,head_width=0.1,color='red')
 ax.set_title('DC Electric Motor');ax.axis('off')
 img=io.BytesIO();plt.savefig(img,format='png',bbox_inches='tight');plt.close();img.seek(0);return img

def draw_transformer():
 fig,ax=plt.subplots(figsize=(6,4));ax.add_patch(plt.Rectangle((1,1.5),0.5,1,fill='gray'))
 ax.add_patch(plt.Rectangle((4,1.5),0.5,1,fill='gray'));ax.text(1.1,2.6,'Primary');ax.text(4.1,2.6,'Secondary')
 for i in range(3):ax.plot([1.5,3.5],[1.7+i*0.3,1.7+i*0.3],'k-')
 ax.set_title('Step-up Transformer');ax.axis('off')
 img=io.BytesIO();plt.savefig(img,format='png',bbox_inches='tight');plt.close();img.seek(0);return img

def draw_nuclear():
 fig,ax=plt.subplots(figsize=(6,4));ax.add_patch(plt.Circle((3,2),0.5,color='orange'))
 ax.text(2.8,2,'U-235');ax.arrow(3,2.5,0,0.5,head_width=0.1,color='red');ax.text(2.8,3.1,'n')
 ax.arrow(2.5,2,-0.5,0,head_width=0.1,color='blue');ax.arrow(3.5,2,0.5,0,head_width=0.1,color='green')
 ax.text(1.8,2,'Ba');ax.text(4.2,2,'Kr');ax.text(2.5,1,'Energy')
 ax.set_title('Nuclear Fission');ax.axis('off')
 img=io.BytesIO();plt.savefig(img,format='png',bbox_inches='tight');plt.close();img.seek(0);return img

def draw_pendulum():
 fig,ax=plt.subplots(figsize=(6,4));ax.plot([3,2],[0,2],'k-');ax.add_patch(plt.Circle((2,2.2),0.2,color='gray'))
 ax.plot([3,3],[0,0.5],'k--');ax.text(2.9,0.2,'θ');ax.set_title('Simple Pendulum');ax.axis('off')
 img=io.BytesIO();plt.savefig(img,format='png',bbox_inches='tight');plt.close();img.seek(0);return img

def draw_electroscope():
 fig,ax=plt.subplots(figsize=(5,6));ax.plot([2.5,2.5],[0,4],'k-',lw=3)
 ax.add_patch(plt.Circle((2.5,4.5),0.5,color='yellow'));ax.text(2.3,4.4,'Knob')
 ax.plot([2.5,2.5],[4,3],'k-',lw=2);ax.plot([2.3,2.7],[3,3],'k-',lw=2)
 ax.plot([2.3,2.2],[3,2.5],'k-',lw=2);ax.plot([2.7,2.8],[3,2.5],'k-',lw=2)
 ax.text(2.6,2.6,'Leaves diverge');ax.set_title('Gold Leaf Electroscope');ax.axis('off')
 img=io.BytesIO();plt.savefig(img,format='png',bbox_inches='tight');plt.close();img.seek(0);return img

def draw_gas_law():
 fig,ax=plt.subplots(figsize=(6,4));ax.plot([1,1],[1,3],'k-',lw=3);ax.plot([1,3],[3,3],'k-',lw=3)
 ax.plot([3,3],[1,3],'k-',lw=3);ax.plot([1,3],[1,1],'k-',lw=3)
 ax.add_patch(plt.Rectangle((3,1.5),0.5,1,color='gray'));ax.text(3.1,2.6,'Piston')
 ax.plot([3.5,4],[2,2],'k-',lw=2);ax.text(4.1,1.9,'Weights')
 ax.text(2,0.5,"Gas: Boyle's Law P1V1=P2V2");ax.set_title('Gas Law Apparatus');ax.axis('off')
 img=io.BytesIO();plt.savefig(img,format='png',bbox_inches='tight');plt.close();img.seek(0);return img

def draw_calorimeter():
 fig,ax=plt.subplots(figsize=(5,6));ax.add_patch(plt.Rectangle((1,1),3,3,fill=False,lw=3))
 ax.add_patch(plt.Rectangle((1.2,1.2),2.6,2.6,color='lightblue'));ax.text(2.2,2.5,'Water')
 ax.plot([2.5,2.5],[4,5],'k-',lw=3);ax.add_patch(plt.Circle((2.5,5),0.2,color='red'));ax.text(2.6,5,'Thermometer')
 ax.add_patch(plt.Rectangle((1,0.5),3,0.5,color='gray'));ax.text(2.2,0.6,'Insulator')
 ax.set_title('Calorimeter Experiment');ax.axis('off')
 img=io.BytesIO();plt.savefig(img,format='png',bbox_inches='tight');plt.close();img.seek(0);return img

def draw_prism():
 fig,ax=plt.subplots(figsize=(6,4))
 tri=np.array([[2,1],[4,1],[3,3]]);ax.plot(tri[:,0],tri[:,1],'k-',lw=2)
 ax.plot([0,2],[2,2],'r-');ax.plot([2,3],[2,1.5],'r-');ax.plot([3,5],[1.5,1],'r-');ax.plot([3,5],[1.5,2],'r-');ax.plot([3,5],[1.5,3],'r-')
 ax.text(0.5,2.2,'White Light');ax.text(4.5,1,'Red');ax.text(4.5,2,'Green');ax.text(4.5,3,'Violet')
 ax.set_title('Dispersion by Prism');ax.axis('off')
 img=io.BytesIO();plt.savefig(img,format='png',bbox_inches='tight');plt.close();img.seek(0);return img

def draw_potential_divider():
 fig,ax=plt.subplots(figsize=(6,4));ax.plot([1,2],[2,2],'k-');ax.plot([3,4],[2,2],'k-');ax.plot([5,6],[2,2],'k-')
 ax.add_patch(plt.Rectangle((2,1.7),0.5,0.6,fill=False,lw=2));ax.text(2.1,1.9,'R1')
 ax.add_patch(plt.Rectangle((4,1.7),0.5,0.6,fill=False,lw=2));ax.text(4.1,1.9,'R2')
 ax.plot([6,6],[2,1],[3,1],'k-');ax.plot([1,1],[1,2],'k-');ax.text(3,0.8,'Vout')
 ax.add_patch(plt.Rectangle((0.5,1.7),0.5,0.6,fill=False,lw=2));ax.text(0.6,1.9,'Vin')
 ax.set_title('Potential Divider');ax.axis('off')
 img=io.BytesIO();plt.savefig(img,format='png',bbox_inches='tight');plt.close();img.seek(0);return img

SYSTEM_PROMPT=f"""You are NCDC Uganda S1-S4 Physics Tutor. 
If question NOT in {NCDC_SYLLABUS} reply: UNEB LOCK: That topic is not in NCDC S1-S4 Physics.
For numericals use: Given: Formula: Substitution: Answer:
Be brief. Max 120 words."""

@app.route("/diagram/<name>")
def serve_diagram(name):
 diagrams={"incline":draw_incline,"lever":draw_lever,"wave":draw_wave,"ohm":draw_ohm,
           "convex":draw_convex,"concave":draw_concave,"motor":draw_motor,
           "transformer":draw_transformer,"nuclear":draw_nuclear,"pendulum":draw_pendulum,
           "electroscope":draw_electroscope,"gas":draw_gas_law,"calorimeter":draw_calorimeter,
           "prism":draw_prism,"divider":draw_potential_divider}
 if name in diagrams:return send_file(diagrams[name](),mimetype='image/png')
 return "No diagram"

@app.route("/",methods=["GET","POST"])
def chatbot():
 try:
  if request.method=="POST":
   q=request.form["question"].lower()
   diagram_url=""
   if "incline" in q:diagram_url="/diagram/incline"
   elif "lever" in q:diagram_url="/diagram/lever"
   elif "wave" in q:diagram_url="/diagram/wave"
   elif "ohm" in q or "circuit" in q:diagram_url="/diagram/ohm"
   elif "convex" in q:diagram_url="/diagram/convex"
   elif "concave" in q:diagram_url="/diagram/concave"
   elif "motor" in q:diagram_url="/diagram/motor"
   elif "transformer" in q:diagram_url="/diagram/transformer"
   elif "nuclear" in q or "fission" in q:diagram_url="/diagram/nuclear"
   elif "pendulum" in q:diagram_url="/diagram/pendulum"
   elif "electroscope" in q:diagram_url="/diagram/electroscope"
   elif "gas" in q:diagram_url="/diagram/gas"
   elif "calorimeter" in q or "heat" in q:diagram_url="/diagram/calorimeter"
   elif "prism" in q:diagram_url="/diagram/prism"
   elif "potential divider" in q:diagram_url="/diagram/divider"
   
   r=client.chat.completions.create(model="llama-3.3-70b-versatile",messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":q}],temperature=0.2,max_tokens=350).choices[0].message.content
   
   img_tag=f"<img src='{diagram_url}' style='max-width:100%;border:1px solid #ccc;border-radius:8px;margin-top:10px'>" if diagram_url else ""
   return f"<html><body style='font-family:Arial;padding:20px;background:#f0f4ff'><h2>NCDC Physics AI 🇺🇬</h2><div style='background:white;padding:15px;border-radius:8px'>{r.replace(chr(10),'<br>')}</div>{img_tag}<br><a href='/'>Ask Another</a></body></html>"
  return """<html><body style='font-family:Arial;padding:20px;background:#f0f4ff'><h2>NCDC S1-S4 Physics AI 🇺🇬</h2>
  <p><b>S1:</b> lever, incline, calorimeter<br>
  <b>S2:</b> wave, motor, pendulum, ohm, electroscope<br>
  <b>S3:</b> convex, concave, prism, gas<br>
  <b>S4:</b> transformer, nuclear, divider</p>
  <form method=post><input name=question style='width:400px;padding:10px' placeholder='Ask: draw convex lens diagram'>
  <button type=submit>Send</button></form></body></html>"""
 except Exception as e:return f"<h2>Error</h2><p>{e}</p>"
if __name__=="__main__":app.run(host="0.0.0.0",port=10000)
