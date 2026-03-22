from flask import Flask, request, jsonify, render_template_string
import time

app = Flask(__name__)

# ── In-memory metrics ──
metrics = {"requests": 0, "passes": 0, "fails": 0}
start_time = time.time()

# ── Quiz Data ──
QUIZ = {
    "title": "DevSecOps Fundamentals Quiz",
    "questions": [
        {
            "id": 1,
            "question": "What does CI stand for in DevSecOps?",
            "options": ["Continuous Integration", "Continuous Inspection", "Code Integration", "Container Interface"],
            "answer": 0
        },
        {
            "id": 2,
            "question": "Which tool is used for GitOps continuous delivery in this project?",
            "options": ["Jenkins", "ArgoCD", "Harness", "Spinnaker"],
            "answer": 1
        },
        {
            "id": 3,
            "question": "What does mTLS stand for?",
            "options": ["Multi Transport Layer Security", "Mutual TLS", "Managed TLS", "Micro TLS"],
            "answer": 1
        },
        {
            "id": 4,
            "question": "Which tool provides service mesh capabilities in this project?",
            "options": ["Prometheus", "Grafana", "Istio", "Terraform"],
            "answer": 2
        },
        {
            "id": 5,
            "question": "What is SLO in SRE?",
            "options": ["Service Level Objective", "System Load Output", "Secure Login Operation", "Software Lifecycle Overview"],
            "answer": 0
        }
    ]
}

PASS_SCORE = 60  # percent

# ── HTML Templates ──
HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>DevSecOps Quiz</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: Arial, sans-serif; background: #f0f4f8; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
    .card { background: white; border-radius: 12px; padding: 40px; max-width: 500px; width: 90%; box-shadow: 0 4px 20px rgba(0,0,0,0.08); text-align: center; }
    h1 { color: #1f3864; font-size: 26px; margin-bottom: 8px; }
    .subtitle { color: #6b7280; font-size: 14px; margin-bottom: 30px; }
    .badge { display: inline-block; background: #dbeafe; color: #1e40af; padding: 4px 12px; border-radius: 20px; font-size: 12px; margin-bottom: 20px; }
    .info { background: #f8fafc; border-radius: 8px; padding: 16px; margin-bottom: 24px; text-align: left; }
    .info p { font-size: 13px; color: #374151; margin-bottom: 6px; }
    input { width: 100%; padding: 10px 14px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; margin-bottom: 12px; outline: none; }
    input:focus { border-color: #2e75b6; }
    button { width: 100%; padding: 12px; background: #1f3864; color: white; border: none; border-radius: 8px; font-size: 15px; font-weight: bold; cursor: pointer; }
    button:hover { background: #2e75b6; }
    .footer { margin-top: 20px; font-size: 11px; color: #9ca3af; }
  </style>
</head>
<body>
  <div class="card">
    <span class="badge">DevSecOps Capstone Project</span>
    <h1>{{ quiz_title }}</h1>
    <p class="subtitle">Test your DevSecOps knowledge</p>
    <div class="info">
      <p>📝 {{ question_count }} questions</p>
      <p>✅ Pass mark: {{ pass_score }}%</p>
      <p>⏱️ No time limit</p>
    </div>
    <form action="/quiz" method="POST">
      <input type="text" name="name" placeholder="Your Name" required />
      <input type="email" name="email" placeholder="Your Email" required />
      <button type="submit">Start Quiz →</button>
    </form>
    <p class="footer">Built with Flask · Secured by Istio · Deployed via ArgoCD · Orchestrated by Kubernetes</p>
  </div>
</body>
</html>
"""

QUIZ_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Quiz — {{ name }}</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: Arial, sans-serif; background: #f0f4f8; padding: 30px 16px; }
    .wrap { max-width: 600px; margin: 0 auto; }
    .header { background: #1f3864; color: white; border-radius: 12px 12px 0 0; padding: 20px 24px; }
    .header h2 { font-size: 18px; }
    .header p { font-size: 13px; opacity: 0.7; margin-top: 4px; }
    .card { background: white; border-radius: 0 0 12px 12px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
    .question { margin-bottom: 28px; border-bottom: 1px solid #f1f5f9; padding-bottom: 24px; }
    .question:last-child { border-bottom: none; margin-bottom: 0; }
    .q-text { font-size: 15px; font-weight: bold; color: #1f3864; margin-bottom: 14px; }
    .q-num { display: inline-block; background: #dbeafe; color: #1e40af; border-radius: 20px; padding: 2px 10px; font-size: 12px; margin-bottom: 8px; }
    label { display: flex; align-items: center; gap: 10px; padding: 10px 14px; border: 1px solid #e5e7eb; border-radius: 8px; margin-bottom: 8px; cursor: pointer; font-size: 14px; color: #374151; }
    label:hover { background: #f0f4f8; border-color: #2e75b6; }
    input[type=radio] { accent-color: #1f3864; }
    button { width: 100%; padding: 14px; background: #1f3864; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; margin-top: 16px; }
    button:hover { background: #2e75b6; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="header">
      <h2>{{ quiz_title }}</h2>
      <p>Hello {{ name }} · Answer all questions and submit</p>
    </div>
    <div class="card">
      <form action="/submit" method="POST">
        <input type="hidden" name="name" value="{{ name }}" />
        <input type="hidden" name="email" value="{{ email }}" />
        {% for q in questions %}
        <div class="question">
          <span class="q-num">Q{{ q.id }}</span>
          <p class="q-text">{{ q.question }}</p>
          {% for i, opt in enumerate(q.options) %}
          <label>
            <input type="radio" name="q{{ q.id }}" value="{{ i }}" required />
            {{ opt }}
          </label>
          {% endfor %}
        </div>
        {% endfor %}
        <button type="submit">Submit Answers →</button>
      </form>
    </div>
  </div>
</body>
</html>
"""

RESULT_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Result — {{ name }}</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: Arial, sans-serif; background: #f0f4f8; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
    .card { background: white; border-radius: 12px; padding: 36px; max-width: 500px; width: 100%; box-shadow: 0 4px 20px rgba(0,0,0,0.08); text-align: center; }
    .result-badge { font-size: 48px; margin-bottom: 12px; }
    h2 { font-size: 24px; color: {% if passed %}#166534{% else %}#991b1b{% endif %}; margin-bottom: 8px; }
    .score { font-size: 42px; font-weight: bold; color: {% if passed %}#166534{% else %}#991b1b{% endif %}; margin: 16px 0; }
    .score span { font-size: 20px; color: #6b7280; }
    .info { background: #f8fafc; border-radius: 8px; padding: 16px; margin: 20px 0; text-align: left; }
    .info p { font-size: 13px; color: #374151; margin-bottom: 6px; }
    .tag { display: inline-block; padding: 6px 16px; border-radius: 20px; font-size: 14px; font-weight: bold;
      background: {% if passed %}#dcfce7{% else %}#fee2e2{% endif %};
      color: {% if passed %}#166534{% else %}#991b1b{% endif %}; margin-bottom: 16px; }
    a { display: inline-block; margin-top: 16px; padding: 10px 24px; background: #1f3864; color: white; border-radius: 8px; text-decoration: none; font-size: 14px; }
    a:hover { background: #2e75b6; }
  </style>
</head>
<body>
  <div class="card">
    <div class="result-badge">{% if passed %}🎉{% else %}📚{% endif %}</div>
    <h2>{% if passed %}Congratulations!{% else %}Keep Learning!{% endif %}</h2>
    <p style="color:#6b7280;font-size:14px;">{{ name }} · {{ email }}</p>
    <div class="score">{{ score }}% <span>/ 100</span></div>
    <span class="tag">{% if passed %}PASS{% else %}FAIL{% endif %}</span>
    <div class="info">
      <p>✅ Correct answers: {{ correct }} / {{ total }}</p>
      <p>📊 Score: {{ score }}%</p>
      <p>🎯 Pass mark: {{ pass_score }}%</p>
    </div>
    <a href="/">Try Again</a>
  </div>
</body>
</html>
"""

# ── Routes ──

@app.route("/")
def home():
    metrics["requests"] += 1
    return render_template_string(HOME_HTML,
        quiz_title=QUIZ["title"],
        question_count=len(QUIZ["questions"]),
        pass_score=PASS_SCORE)

@app.route("/quiz", methods=["POST"])
def quiz():
    metrics["requests"] += 1
    name = request.form.get("name", "Trainee")
    email = request.form.get("email", "")
    return render_template_string(QUIZ_HTML,
        name=name, email=email,
        quiz_title=QUIZ["title"],
        questions=QUIZ["questions"],
        enumerate=enumerate)

@app.route("/submit", methods=["POST"])
def submit():
    metrics["requests"] += 1
    name = request.form.get("name", "Trainee")
    email = request.form.get("email", "")
    correct = 0
    total = len(QUIZ["questions"])
    for q in QUIZ["questions"]:
        answer = request.form.get(f"q{q['id']}")
        if answer is not None and int(answer) == q["answer"]:
            correct += 1
    score = int((correct / total) * 100)
    passed = score >= PASS_SCORE
    if passed:
        metrics["passes"] += 1
    else:
        metrics["fails"] += 1
    return render_template_string(RESULT_HTML,
        name=name, email=email,
        score=score, correct=correct,
        total=total, passed=passed,
        pass_score=PASS_SCORE)

@app.route("/health")
def health():
    metrics["requests"] += 1
    return jsonify({
        "status": "ok",
        "uptime_seconds": round(time.time() - start_time),
        "service": "quiz-app",
        "version": "1.0.0"
    })

@app.route("/metrics")
def get_metrics():
    metrics["requests"] += 1
    uptime = round(time.time() - start_time)
    return jsonify({
        "total_requests": metrics["requests"],
        "total_passes": metrics["passes"],
        "total_fails": metrics["fails"],
        "uptime_seconds": uptime,
        "pass_rate_percent": round((metrics["passes"] / max(metrics["passes"] + metrics["fails"], 1)) * 100, 1)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
