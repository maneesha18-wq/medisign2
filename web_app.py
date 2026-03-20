#!/usr/bin/env python
"""
MediSign Professional Web Application
A production-ready platform for medical sign language recognition
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import json
from pathlib import Path
import numpy as np
import tensorflow as tf
from io import BytesIO
import logging

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import sys

sys.path.insert(0, ".")
from modules.preprocessing import preprocess_video
from modules.feature_extractor import FeatureExtractor
from modules.sequence_model import build_sequence_model, AttentionLayer
from modules.text_to_speech import TextToSpeech
from modules.prediction_logger import PredictionLogger

# Setup Flask app
app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model and components
model = None
feature_extractor = None
label_map = None
tts = None
logger_pred = None


def init_model():
    """Initialize model and components"""
    global model, feature_extractor, label_map, tts, logger_pred

    logger.info("Loading model and components...")

    # Load model
    model_path = "models/sequence_model_medical.keras"
    if Path(model_path).exists():
        model = tf.keras.models.load_model(
            model_path, custom_objects={"AttentionLayer": AttentionLayer}
        )
        logger.info("[OK] Model loaded")

    # Load label map
    label_map_path = "models/medical_terms_map.json"
    if Path(label_map_path).exists():
        with open(label_map_path, "r") as f:
            label_map = json.load(f)
        logger.info(f"[OK] Label map loaded: {label_map['num_classes']} classes")

    # Initialize feature extractor
    feature_extractor = FeatureExtractor(backbone="mobilenetv2", device="gpu")
    logger.info("[OK] Feature extractor initialized")

    # Initialize TTS
    tts = TextToSpeech(output_dir="logs/audio", language="en")
    logger.info("[OK] Text-to-speech initialized")

    # Initialize logger
    try:
        logger_pred = PredictionLogger(log_file="logs/predictions_medical.csv")
        logger.info("Prediction logger initialized")
    except:
        logger_pred = None
        logger.info("Prediction logger skipped")


# Initialize on startup
init_model()

# ==================== ROUTES ====================


@app.route("/")
def home():
    """Home page"""
    return render_template("index.html")


@app.route("/demo")
def demo():
    """Demo/test page"""
    return render_template("demo.html")


@app.route("/about")
def about():
    """About page"""
    return render_template("about.html")


@app.route("/features")
def features():
    """Features page"""
    return render_template("features.html")


@app.route("/api/info")
def api_info():
    """Get app info"""
    return jsonify(
        {
            "name": "MediSign",
            "version": "2.0",
            "description": "Medical Sign Language Recognition System",
            "classes": label_map["num_classes"] if label_map else 0,
            "medical_terms": label_map["medical_terms"] if label_map else [],
        }
    )


@app.route("/api/stats")
def api_stats():
    """Get live prediction statistics from the audit log."""
    try:
        if logger_pred is None:
            return jsonify({
                "total_predictions": 0,
                "success_count": 0,
                "error_count": 0,
                "average_confidence": 0.0,
                "label_distribution": {},
                "active_terms": label_map["num_classes"] if label_map else 0,
            })

        summary = logger_pred.get_log_summary()

        # Derive "successful matches" = predictions with confidence >= 0.6
        # (re-read CSV to count high-confidence predictions)
        high_confidence_count = 0
        top_term = None
        try:
            import csv
            with open(logger_pred.log_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                label_counts = {}
                for row in reader:
                    try:
                        conf = float(row.get("confidence", 0))
                        if conf >= 0.60:
                            high_confidence_count += 1
                        lbl = row.get("label", "")
                        if lbl:
                            label_counts[lbl] = label_counts.get(lbl, 0) + 1
                    except ValueError:
                        pass
            if label_counts:
                top_term = max(label_counts, key=label_counts.get)
        except Exception:
            pass

        return jsonify({
            "total_predictions": summary.get("total_predictions", 0),
            "success_count": summary.get("success_count", 0),
            "high_confidence_matches": high_confidence_count,
            "error_count": summary.get("error_count", 0),
            "average_confidence": round(summary.get("average_confidence", 0.0) * 100, 1),
            "label_distribution": summary.get("label_distribution", {}),
            "top_term": top_term,
            "active_terms": label_map["num_classes"] if label_map else 0,
        })
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/recognize", methods=["POST"])
def api_recognize():
    """API endpoint for video recognition"""
    try:
        # Check if model is loaded
        if model is None or feature_extractor is None or label_map is None:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Model not loaded. Please restart the app.",
                    }
                ),
                503,
            )

        if "video" not in request.files:
            return jsonify({"success": False, "error": "No video provided"}), 400

        video_file = request.files["video"]
        if video_file.filename == "":
            return jsonify({"success": False, "error": "No video selected"}), 400

        # Save temporary video
        temp_path = f"uploads/{video_file.filename}"
        os.makedirs("uploads", exist_ok=True)
        video_file.save(temp_path)

        # Preprocess
        preprocessed = preprocess_video(
            temp_path, num_frames=60, target_size=(224, 224)
        )
        if preprocessed is None or preprocessed.shape != (60, 224, 224, 3):
            return (
                jsonify({"success": False, "error": "Video preprocessing failed"}),
                400,
            )

        # Extract features
        features = feature_extractor.extract(preprocessed)
        if features is None or features.shape[0] != 60:
            logger.error(
                f"Feature extraction failed: got {features.shape if features is not None else 'None'}"
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Feature extraction failed. Try a different video.",
                    }
                ),
                400,
            )

        # Get prediction
        features_expanded = np.expand_dims(features, axis=0)
        prediction = model.predict(features_expanded, verbose=0)
        pred_class = np.argmax(prediction[0])
        confidence = float(prediction[0][pred_class])

        # Get label
        predicted_label = label_map["idx_to_label"][str(pred_class)]

        # Get all probabilities
        all_probs = {
            label_map["idx_to_label"][str(i)]: float(prediction[0][i])
            for i in range(len(prediction[0]))
        }

        if logger_pred is not None:
            try:
                logger_pred.log_prediction(
                    label=predicted_label, 
                    confidence=confidence,
                    video_source=request.form.get("source", "upload"),
                    video_path=video_file.filename
                )
            except Exception as log_err:
                logger.warning(f"Failed to log prediction: {log_err}")

        # Generate TTS audio
        audio_url = None
        translated_text = None
        if tts is not None:
            try:
                # Convert label to readable text (replace underscores with spaces)
                readable_text = predicted_label.replace('_', ' ')
                target_lang = request.form.get("language", "en")
                logger.info(f"Target language for TTS: {target_lang}")
                
                # Modified call to get translated text back
                audio_path, tts_error, translated_text = tts.convert_and_save(readable_text, label=predicted_label, target_language=target_lang)
                
                if audio_path and not tts_error:
                    audio_filename = os.path.basename(audio_path)
                    audio_url = f"/audio/{audio_filename}"
                    logger.info(f"Generated TTS audio: {audio_url} (Text: {translated_text})")
                else:
                    logger.warning(f"TTS error: {tts_error}")
            except Exception as audio_err:
                logger.warning(f"Failed to generate TTS: {audio_err}")

        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return jsonify(
            {
                "success": True,
                "prediction": predicted_label,
                "confidence": confidence,
                "all_predictions": all_probs,
                "audio_url": audio_url,
                "translation": translated_text,
                "language": request.form.get("language", "en")
            }
        )

    except Exception as e:
        logger.error(f"Recognition error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/audio/<filename>")
def serve_audio(filename):
    """Serve generated audio files"""
    try:
        audio_path = os.path.join("logs/audio", filename)
        if os.path.exists(audio_path):
            return send_file(audio_path, mimetype="audio/mpeg")
        return jsonify({"error": "Audio file not found"}), 404
    except Exception as e:
        logger.error(f"Audio serving error: {e}")
        return jsonify({"error": str(e)}), 500




# ==================== MAIN ====================

if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("🚀 MediSign Professional Web Platform")
    logger.info("=" * 70)
    logger.info(f"Starting Flask app on http://0.0.0.0:5000")
    logger.info("Visit: http://localhost:5000")
    logger.info("=" * 70)

    app.run(host="0.0.0.0", port=5000, debug=False)
