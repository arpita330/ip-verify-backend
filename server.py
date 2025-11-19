from flask import Flask, request, jsonify
import time, os, json

app = Flask(__name__)

DATA_FILE = "verify_data.json"
SECRET_KEY = "4729"  # CHANGE THIS!

# Load data storage
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

# Save storage
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


@app.route("/report_ip", methods=["POST"])
def report_ip():
    try:
        req = request.get_json(force=True)
    except:
        return jsonify({"success": False, "message": "Invalid JSON"}), 400

    token = req.get("token")
    ip = req.get("ip")
    user_id = req.get("user_id")  # must be sent from .bjs bot

    if not token or not ip or not user_id:
        return jsonify({
            "success": False,
            "message": "Missing fields (token, ip, user_id required)"
        }), 400

    data = load_data()

    # Unique key for rule 4:
    # SAME TOKEN + SAME USER + SAME IP → Already Verified
    key = f"{user_id}:{token}:{ip}"

    # Condition: Already verified
    if key in data:
        return jsonify({
            "success": True,
            "already": True,
            "message": "Previously verified"
        }), 200

    # Save new verification entry
    data[key] = {
        "user_id": user_id,
        "token": token,
        "ip": ip,
        "verified_at": time.time()
    }

    save_data(data)

    return jsonify({
        "success": True,
        "already": False,
        "message": "Verification completed"
    }), 200


@app.route("/")
def home():
    return "IP Verification Server Running"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)