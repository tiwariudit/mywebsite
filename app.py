from flask import Flask, render_template, request, jsonify
import razorpay
import hmac
import hashlib
import os

app = Flask(__name__)


RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
# Razorpay credentials above

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

@app.route("/")
def home():
    return render_template("index.html", key_id=RAZORPAY_KEY_ID)

@app.route("/create_order", methods=["POST"])
def create_order():
    data = request.get_json()
    amount = int(data["amount"]) * 100   # Convert to paise

    order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    return jsonify(order)

@app.route("/verify", methods=["POST"])
def verify_payment():
    data = request.get_json()

    order_id = data["razorpay_order_id"]
    payment_id = data["razorpay_payment_id"]
    signature = data["razorpay_signature"]

    generated = hmac.new(
        bytes(RAZORPAY_KEY_SECRET, 'utf-8'),
        bytes(order_id + "|" + payment_id, 'utf-8'),
        hashlib.sha256
    ).hexdigest()

    if generated == signature:
        return jsonify({"status": "success", "message": "Payment verified"})
    else:
        return jsonify({"status": "failed", "message": "Invalid signature"}), 400

if __name__ == "__main__":
    app.run(port=5000, debug=True)
