from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/gateway', methods=['POST'])
def gateway():
    return jsonify({"status": "Minimal Flask app is working!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
