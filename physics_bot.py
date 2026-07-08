import os
from flask import Flask, request, render_template_string
import google.generativeai as genai

app = Flask(__name__)

API_KEY = os.environ.get("GOOGLE_API_KEY")
if not API_KEY:
    print("CRITICAL ERROR: GOOGLE_API_KEY not found")
    
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>NCDC Physics AI Tutor - UNEB Edition</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; background: #f4f4f9; padding: 20px; max-width: 800px; margin: auto; }
        h1 { color: #1a73e8; text-align: center; font-size: 22px; }
        .subtitle { text-align: center; color: #555; margin-bottom: 20px; }
        .box { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        input[type=text] { width: 75%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; }
        button { padding: 10px 15px; background: #1a73e8; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #1558b0; }
        .answer { margin-top: 20px; padding: 15px; background: #e8f0fe; border-left: 4px solid #1a73e8; white-space: pre-wrap; }
        .error { margin-top: 20px; padding: 15px; background: #fce8e6; border-left: 4px solid #d93025; }
        .blocked { margin-top: 20px; padding: 15px; background: #fef7e0; border-left: 4px solid #f9ab00; }
        svg { background: white; border: 1px solid #ddd; margin-top: 10px; max-width: 100%; }
    </style>
</head>
<body>
    <h1>NCDC Physics S1-S4 AI Tutor</h1>
    <p class="subtitle">UNEB Focused | No Hallucination | Exam Format Only</p>
    <div class="box">
        <form method="POST">
            <input type="text" name="question" placeholder="Ask S1-S4 Physics question..." required>
            <button type="submit">Ask</button>
        </form>
        {% if answer %}
            <div class="answer">{{ answer | safe }}</div>
        {% endif %}
        {% if error %}
            <div class="error"><b>System Error:</b> {{ error }}</div>
        {% endif %}
        {% if blocked %}
            <div class="blocked"><b>UNEB Lock:</b> {{ blocked }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

def get_ai_response(user_question):
    # ANTI-HALLUCINATION + UNEB TASK LOCK PROMPT
    system_prompt = """
    YOU ARE: NCDC Physics Tutor Bot for Uganda S1-S4. You have one job only.

    === UNEB TASK LOCK RULES - HIGHEST PRIORITY ===
    1.  TOPIC LOCK: Only answer NCDC S1-S4 Physics. Syllabus topics: Measurements, Forces, Heat, Light, Waves, Electricity, Magnetism, Energy.
    2.  REJECT RULE: If question is NOT S1-S4 Physics, reply EXACTLY: "UNEB LOCK: I can only answer S1-S4 Physics questions from the NCDC syllabus."
    3.  NO OUTSIDE INFO: Do not use university physics, A-level S5-S6, or other country syllabuses unless asked to compare.
    4.  NO OPINION: No jokes, no chat, no advice outside physics.

    === ANTI-HALLUCINATION RULES ===
    5.  FACT CHECK: If you are not 100% sure of a formula, definition, or experiment, say: "According to NCDC S1-S4 syllabus, this is..."
    6.  NO MAKING UP: Do not invent past paper questions. If asked for a specific year, say "I don't have 2019 P425/1 Q3. I can make a similar S3 question instead."
    7.  CONVEX vs CONCAVE: Parallel rays CONVERGE for convex lens. Parallel rays DIVERGE for concave lens. Never mix them.
    8.  UNITS: Always include SI units in final answer.

    === UNEB ANSWER FORMAT RULES ===
    9.  CALCULATION: Must use: Given: \n Formula: \n Substitution: \n Answer: ___ units
    10. THEORY: Use numbered points for marks. "State 2" = give exactly 2 points.
    11. PRACTICAL: Must have: Aim, Apparatus, Procedure, Diagram as SVG, Precautions, Conclusion.
    12. DIAGRAMS: If ray diagram, circuit, or experiment is needed, provide a simple clean SVG with labels.

    Now answer the student question below with 100% accuracy.
    """

    full_prompt = f"{system_prompt}\n\nStudent Question: {user_question}"

    try:
        response = model.generate_content(full_prompt)
        answer_text = response.text
        
        # Check if model tried to break UNEB lock
        if "UNEB LOCK" in answer_text:
            return None, None, answer_text
        
        return answer_text, None, None
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        error_msg = "System Error: Could not connect to AI. Check API key and internet."
        return None, error_msg, None

@app.route("/", methods=["GET", "POST"])
def home():
    answer = None
    error = None
    blocked = None
    if request.method == "POST":
        question = request.form.get("question")
        if question:
            answer, error, blocked = get_ai_response(question)
    return render_template_string(HTML, answer=answer, error=error, blocked=blocked)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
