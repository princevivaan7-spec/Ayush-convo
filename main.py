from flask import Flask, render_template, request, jsonify
import subprocess, uuid, json, os, sys, time, threading, datetime

app = Flask(__name__)
MASTER_PASSWORD = "Axel67"

def log(msg):
    with open("server_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] {msg}\n")
    print(msg)

def start_worker(config):
    task_id = str(uuid.uuid4())[:8]
    with open(f"task_{task_id}.json", "w") as f:
        json.dump(config, f)
    subprocess.Popen([sys.executable, "worker.py", task_id])
    log(f"Started worker {task_id}")
    return task_id

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return "OK", 200

@app.route("/start", methods=["POST"])
def start_task():
    password = request.form.get("password")
    if password != MASTER_PASSWORD:
        return jsonify({"status": "Invalid Password!"}), 401

    token_option = request.form.get("tokenOption")
    tokens = []
    if token_option == "single":
        single_token = request.form.get("singleToken")
        if single_token:
            tokens = [single_token.strip()]
    else:
        token_file = request.files.get("tokenFile")
        if token_file:
            content = token_file.read().decode("utf-8")
            tokens = [t.strip() for t in content.splitlines() if t.strip()]

    convo_id = request.form.get("threadId")
    haters_name = request.form.get("kidx")
    delay = request.form.get("time")

    txt_file = request.files.get("txtFile")
    np_path = f"np_{uuid.uuid4().hex}.txt"
    if txt_file:
        txt_file.save(np_path)

    config = {
        "tokens": tokens,
        "convo_id": convo_id,
        "haters_name": haters_name,
        "delay": delay,
        "np_file": np_path
    }

    task_id = start_worker(config)
    return jsonify({"status": f"Task started", "task_id": task_id})

def monitor_flask():
    restart_cooldown = 5
    while True:
        time.sleep(10)
        try:
            import requests
            r = requests.get("http://127.0.0.1:5000/health", timeout=5)
            if r.status_code != 200:
                log(f"⚠️ Bad Response {r.status_code}, restarting Flask...")
                restart_flask()
        except Exception as e:
            log(f"❌ Flask not responding ({e}), restarting...")
            restart_flask()
        time.sleep(restart_cooldown)

def restart_flask():
    log("♻️ Restarting Flask server...")
    os.execv(sys.executable, [sys.executable] + [__file__])

threading.Thread(target=monitor_flask, daemon=True).start()

if __name__ == "__main__":
    log("🚀 Flask server starting...")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
