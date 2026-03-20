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

# Force using port 5001 to bypass any old processes stuck on 5000
PORT = 5001

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
        try:
            model = tf.keras.models.load_model(model_path, custom_objects={"AttentionLayer": AttentionLayer})
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
    
    if os.path.exists(map_path):
        with open(map_path, "r") as f:
            label_map = json.load(f)
        logger.info("Label map loaded")

init_model()

# --- (API Routes) ---
@app.route("/api/info")
def api_info():
    return jsonify({
        "name": "MediSign Professional",
        "version": "2.0",
        "status": "online",
        "features": ["Login", "Dashboard", "Webcam", "Interpreter"]
    })

# --- (Frontend Serving) ---
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    # If the path exists in dist, serve it (for assets like .js, .css, etc)
    if path != "" and os.path.exists(os.path.join(FRONTEND_DIST, path)):
        return send_from_directory(FRONTEND_DIST, path)
    
    # Otherwise, check if it's an API route (let it fail if not found)
    if path.startswith("api/"):
        return jsonify({"error": "API route not found"}), 404
        
    # For all other routes (like /login or /dashboard), serve the React index.html
    # This allows React Router to handle the navigation
    return send_from_directory(FRONTEND_DIST, "index.html")

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 STARTING MEDISIGN MODERN DASHBOARD")
    logger.info(f"Serving from: {FRONTEND_DIST}")
    logger.info(f"Access it here: http://localhost:{PORT}")
    logger.info("=" * 60)
    
    app.run(host="0.0.0.0", port=PORT, debug=False)
