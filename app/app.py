from flask import Flask, jsonify, request
from pymongo import MongoClient
from datetime import datetime, timezone
from bson import json_util
import os

app = Flask(__name__)

# MongoDB connection string provided through environment variables
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb://localhost:27017/"
)

client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)

db = client["flask_db"]
collection = db["data"]


@app.route("/", methods=["GET"])
def home():
    current_time = datetime.now(timezone.utc).isoformat()

    return f"Welcome to the Flask app! The current time is: {current_time}"


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/data", methods=["GET", "POST"])
def data():
    if request.method == "POST":
        payload = request.get_json(silent=True)

        if not isinstance(payload, dict):
            return jsonify({"error": "A valid JSON object is required"}), 400

        result = collection.insert_one(payload)

        return jsonify({
            "status": "Data inserted successfully",
            "inserted_id": str(result.inserted_id)
        }), 201

    documents = list(collection.find({}, {"_id": 0}))

    return json_util.dumps(documents), 200, {
        "Content-Type": "application/json"
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
