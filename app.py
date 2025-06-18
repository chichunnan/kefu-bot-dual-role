
from flask import Flask, render_template, request
import json, csv
from datetime import datetime

app = Flask(__name__)
with open("corpus.json", "r", encoding="utf-8") as f:
    CORPUS = json.load(f)

def classify_scene(text):
    for entry in CORPUS:
        for kw in entry["keywords"]:
            if kw in text:
                return entry["scene"], entry["reply"]
    return "無對應情境", "請您再確認描述內容，謝謝。"

@app.route("/", methods=["GET", "POST"])
def index():
    customer_text = ""
    agent_reply = ""
    scene = ""
    suggestion = ""
    score = ""
    saved = False

    if request.method == "POST":
        customer_text = request.form.get("customer_input", "")
        agent_reply = request.form.get("agent_reply", "")
        scene, suggestion = classify_scene(customer_text)

        score = "✅ 合格"
        if any(bad in agent_reply for bad in ["幹", "爛", "白癡"]):
            score = "❌ 不合格（用詞不當）"
        elif len(agent_reply.strip()) < 6:
            score = "⚠️ 回覆太短"
        elif suggestion not in agent_reply:
            score = "⚠️ 回覆未完整對應建議話術"

        with open("static/log.csv", "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                customer_text, agent_reply, scene, suggestion, score
            ])
        saved = True

    return render_template("index.html", customer_text=customer_text, agent_reply=agent_reply,
                           scene=scene, suggestion=suggestion, score=score, saved=saved)

@app.route("/download")
def download():
    return app.send_static_file("log.csv")

if __name__ == "__main__":
    app.run(debug=True)
