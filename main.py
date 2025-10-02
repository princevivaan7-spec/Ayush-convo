from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run():
    token = request.form.get("token")
    return f"Token received: {token}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
