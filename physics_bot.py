import os
import json
from flask import Flask, request, render_template_string
from groq import Groq

app = Flask(__name__)

# LOAD TOPICS DICTIONARY - CHANGED FILENAME HERE
with open('ncdc_physics.json', 'r', encoding='utf-8') as f:
    NCDC_TOPICS = json.load(f)
ALL_TOPICS = [topic for grade in NCDC_TOPICS.values() for topic in grade]

# GROQ SETUP
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

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
    .answer { margin-top: 20px; padding: 15px; background: #e8f0fe; border-left: 4px solid #1a73e8; white-space: pre-wrap; font-size: 14px; line-height: 1.6; }
    .error { margin-top: 20px; padding: 15px; background: #fce8e6; border-left: 4px solid #d93025; }
      svg { max-width: 100%; border: 1px solid #ccc; margin-top: 10px; background: white; }
    </style>
</head>
<body>
    <h1>NCDC Physics S1-S4 AI Tutor</h1>
    <p class="subtitle">UNEB Focused | Diagrams + Practicals | No Hallucination</p>
    <div class="box">
        <form method="POST">
            <input type="text" name="question" placeholder="Ask S1-S4 Physics theory, calculation, practical or diagram..." required>
            <button type="submit">Ask</button>
        </form>
        {% if answer %}
            <div class="answer">{{ answer | safe }}</div>
        {% endif %}
        {% if error %}
            <div class="error"><b>System Error:</b> {{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

def get_ai_response(user_question):
    topics_list = ", ".join(ALL_TOPICS)

    system_prompt = f"""
YOU ARE: NCDC Physics Tutor Bot for Uganda S1-S4.

=== UNEB TASK LOCK RULES ===
1. ALLOWED TOPICS ONLY: {topics_list}
2. REJECT RULE: If topic is NOT in the list above, reply EXACTLY:
    "UNEB LOCK: That topic is not in NCDC S1-S4 Physics."
3. ANTI-HALLUCINATION: Only use info from NCDC syllabus. Do not invent formulas.

=== ANSWER FORMAT RULES ===
4. THEORY QUESTION: Use numbered points for marks. 1 point = 1 mark.
5. CALCULATION QUESTION: Use this EXACT format:
   Given:
   Formula:
   Substitution:
   Answer: ___ units
6. PRACTICAL/ACTIVITY OF INTEGRATION QUESTION: Use this EXACT NCDC Report Structure:
   ITEM NUMBER:
   THE AIM:
   HYPOTHESIS:
   VARIABLES IDENTIFIED:
   - Independent Variable:
   - Dependent Variable:
   - Controlled/Fixed Variables:
   APPARATUS:
   PROCEDURE: Numbered steps including safety precautions
   RESULTS & MANIPULATION: Data table with correct SI units and precision
   GRAPH WORK: Describe scale, labeled axes, line of best fit
   CALCULATIONS/SLOPE: Show mathematical steps
   SOURCES OF ERROR: State limitation + mitigation step
   CONCLUSION: Final verdict matching aim + advice

   PRECISION MANDATES:
   Metre Rule: 1dp in cm e.g. 25.0 cm. Digital Stopwatch: 2dp e.g. 12.34 s.
   Protractor: 0dp e.g. 42°. Ammeter/Voltmeter: 2dp e.g. 0.50 A, 3.25 V.
   Thermometer: 1dp ending.0 or.5 e.g. 28.5°C

7. DIAGRAM CONSTRUCTION RULES: If question asks for "draw", "diagram", "ray diagram", "circuit":
   a. First give STEP-BY-STEP construction instructions as per NCDC practical guidelines
   b. Then output a clean SVG diagram inside a ```svg code block
   c. NCDC Diagram Rules: Use ruler and sharp pencil. Label all parts. Use arrows for rays/current.
      Show normal with dotted line. Show angles. Use scale where applicable.

Student Question: {user_question}
"""
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": system_prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.2
        )
        return chat_completion.choices[0].message.content, None
    except Exception as e:
        return None, str(e)


@app.route("/", methods=["GET", "POST"])
def home():
    answer = None
    error = None
    if request.method == "POST":
        question = request.form.get("question")
        if question:
            answer, error = get_ai_response(question)
    return render_template_string(HTML, answer=answer, error=error)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
