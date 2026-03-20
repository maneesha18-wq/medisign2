#!/usr/bin/env python
from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import os
import json
from pathlib import Path
import numpy as np
import tensorflow as tf
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Absolute path to the React build directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")

app = Flask(__name__, static_folder=os.path.join(FRONTEND_DIST, "assets"))
CORS(app)

# --- (Model Initialization) ---
model = None
label_map = None

def init_model():
    global model, label_map
    model_path = os.path.join(BASE_DIR, "models", "sequence_model_medical.keras")
    map_path = os.path.join(BASE_DIR, "models", "medical_terms_map.json")
    
    if os.path.exists(model_path):
        from modules.sequence_model import AttentionLayer
        model = tf.keras.models.load_model(model_path, custom_objects={"AttentionLayer": AttentionLayer})
        logger.info("Model loaded")
    
    if os.path.exists(map_path):
        with open(map_path, "r") as f:
            label_map = json.load(f)
        logger.info("Label map loaded")

init_model()

# --- (API Routes) ---
@app.route("/api/info")
def api_info():
    return jsonify({"name": "MediSign", "status": "online"})

# --- (Frontend Serving) ---
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists(os.path.join(FRONTEND_DIST, path)):
        return send_from_directory(FRONTEND_DIST, path)
    else:
        # Serve index.html for all other routes (React Router)
        return send_from_directory(FRONTEND_DIST, "index.html")

if __name__ == "__main__":
    logger.info(f"Serving frontend from: {FRONTEND_DIST}")
    app.run(host="0.0.0.0", port=5000, debug=False)
