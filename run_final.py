#!/usr/bin/env python
from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import os
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")

# Using a completely unique port to avoid ANY conflicts
PORT = 9999

app = Flask(__name__, static_folder=os.path.join(FRONTEND_DIST, "assets"))
CORS(app)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists(os.path.join(FRONTEND_DIST, path)):
        return send_from_directory(FRONTEND_DIST, path)
    return send_from_directory(FRONTEND_DIST, "index.html")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 MEDISIGN MODERN DASHBOARD (LOGIN/OVERVIEW)")
    print(f"URL: http://localhost:{PORT}")
    print("=" * 60 + "\n")
    app.run(host="0.0.0.0", port=PORT, debug=False)
