from flask import Flask, request, jsonify
import time, os, json

app = Flask(__name__)

DATA_FILE = "verify_data.json"
SECRET_KEY = "secret123"   # change this

# Load verification database
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

# Save data
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


@app.route("/")
def home():
    return "IP Verification Server Running"


# --- MAIN VERIFICATION ROUTE (POST) ---
@app.route("/report_ip", methods=["POST"])
def report_ip():
    req = request.get_json(force=True)

    token = req.get("token")
    ip = req.get("ip")
    user_id = req.get("user_id")

    if not token or not ip or not user_id:
        return jsonify({"success": False, "message": "Missing fields"}), 400

    data = load_data()

    key = f"{user_id}:{token}:{ip}"

    # Already verified
    if key in data:
        return jsonify({
            "success": True,
            "already": True
        }), 200

    # First verification
    data[key] = {
        "user_id": user_id,
        "token": token,
        "ip": ip,
        "verified_at": time.time()
    }
    save_data(data)

    return jsonify({
        "success": True,
        "already": False
    }), 200


# --- GET TEST ROUTE ---
@app.route("/test", methods=["GET"])
def test_verify():
    token = request.args.get("token")
    ip = request.args.get("ip")
    user_id = request.args.get("user_id")

    if not token or not ip or not user_id:
        return jsonify({
            "success": False,
            "message": "Use: /test?token=123&ip=1.1.1.1&user_id=999"
        }), 400

    data = load_data()
    key = f"{user_id}:{token}:{ip}"

    if key in data:
        return jsonify({
            "success": True,
            "already": True,
            "message": "Already Verified"
        }), 200

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
        "message": "Verification Successful"
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)