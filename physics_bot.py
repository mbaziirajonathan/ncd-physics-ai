import os
import json
from flask import Flask, request, render_template_string
from groq import Groq # CHANGED

app = Flask(__name__)

# LOAD TOPICS DICTIONARY
with open('topics.json', 'r') as f:
    NCDC_TOPICS = json.load(f)
ALL_TOPICS = [topic for grade in NCDC_TOPICS.values() for topic in grade]

# GROQ SETUP
GROQ_API_KEY = os.environ.get("GROQ_API_KEY") # CHANGED
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
       .answer { margin-top: 20px; padding: 15px; background: #e8f0fe; border-left: 4px solid #1a73e8; white-space: pre-wrap; }
       .error { margin-top: 20px; padding: 15px; background: #fce8e6; border-left: 4px solid #d93025; }
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
    3. ANTI-HALLUCINATION: Only use info from NCDC syllabus.
    
    === ANSWER FORMAT RULES ===
    4. CALCULATION: Given: \n Formula: \n Substitution: \n Answer: ___ units
    5. THEORY: Use numbered points for marks.
    
    Student Question: {user_question}
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": system_prompt}],
            model="llama-3.1-8b-instant", # Fastest Groq model
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
