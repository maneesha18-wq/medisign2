"""
MediSign Medical Edition - Updated Gradio App
Supports real medical sign language recognition
"""

import os

os.environ["SSLKEYLOGFILE"] = ""
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import sys
import json
from pathlib import Path
from typing import Tuple, Optional

import gradio as gr
import numpy as np
import tensorflow as tf

sys.path.insert(0, ".")
from modules.preprocessing import preprocess_video
from modules.feature_extractor import FeatureExtractor
from modules.sequence_model import build_sequence_model, AttentionLayer
from modules.text_to_speech import TextToSpeech
from modules.prediction_logger import PredictionLogger


class MedicalSignLanguageApp:
    """Gradio app for medical sign language recognition"""

    def __init__(
        self,
        model_path: str = "models/sequence_model_medical.keras",
        label_map_path: str = "models/medical_terms_map.json",
        device: str = "gpu",
        enable_tts: bool = True,
    ):
        """Initialize medical sign language app"""

        self.device = device
        self.model = None
        self.label_map = None
        self.feature_extractor = None
        self.tts = None
        self.logger = None

        # Load model
        if Path(model_path).exists():
            print(f"Loading model: {model_path}")
            self.model = tf.keras.models.load_model(
                model_path, custom_objects={"AttentionLayer": AttentionLayer}
            )
            print("Model loaded successfully")
        else:
            print(f"WARNING: Model not found at {model_path}")

        # Load label mapping
        if Path(label_map_path).exists():
            with open(label_map_path, "r") as f:
                self.label_map = json.load(f)
            print(f"Loaded {self.label_map['num_classes']} medical terms")
        else:
            print(f"WARNING: Label map not found at {label_map_path}")

        # Initialize feature extractor
        self.feature_extractor = FeatureExtractor(backbone="mobilenetv2", device=device)
        print("Feature extractor initialized")

        # Initialize TTS
        if enable_tts:
            self.tts = TextToSpeech(output_dir="logs/audio", language="en")
            print("TTS enabled")

        # Initialize logger
        self.logger = PredictionLogger(log_file="logs/predictions_medical.csv")
        print("Prediction logger initialized")

    def infer_video(
        self, video_path: Optional[str], enable_audio: bool = True
    ) -> Tuple[str, float, Optional[str]]:
        """Run inference on medical sign language video"""

        if self.model is None:
            return "Model not loaded", 0.0, None

        if video_path is None or not Path(video_path).exists():
            return "No video provided or file not found", 0.0, None

        try:
            # Preprocess
            print(f"Preprocessing video: {video_path}")
            preprocessed = preprocess_video(
                video_path, num_frames=60, target_size=(224, 224)
            )

            if preprocessed is None or preprocessed.shape != (60, 224, 224, 3):
                return (
                    f"Preprocessing failed: {preprocessed.shape if preprocessed is not None else 'None'}",
                    0.0,
                    None,
                )

            # Extract features
            print("Extracting features")
            features = self.feature_extractor.extract(preprocessed)

            if features.shape != (60, 1280):
                return f"Feature extraction failed: {features.shape}", 0.0, None

            # Inference
            print("Running inference")
            features_batch = np.expand_dims(features, axis=0)
            logits = self.model.predict(features_batch, verbose=0)

            pred_idx = np.argmax(logits[0])
            confidence = float(logits[0, pred_idx])

            # Get medical term
            if self.label_map:
                idx_to_label = self.label_map["idx_to_label"]
                medical_term = idx_to_label[str(pred_idx)]
            else:
                medical_term = f"class_{pred_idx}"

            print(f"Predicted: {medical_term} (confidence: {confidence:.4f})")

            # Generate audio
            audio_file = None
            if enable_audio and self.tts:
                audio_file, error = self.tts.convert_and_save(
                    text=medical_term, label=medical_term
                )
                if error:
                    print(f"TTS warning: {error}")

            # Log prediction
            if self.logger:
                video_source = "webcam" if "tmp" in video_path else "upload"
                self.logger.log_prediction(
                    label=medical_term,
                    confidence=confidence,
                    audio_file=audio_file,
                    video_source=video_source,
                    video_path=video_path,
                    status="success",
                )

            return f"**{medical_term}**", confidence, audio_file

        except Exception as e:
            print(f"Inference error: {e}")
            if self.logger:
                self.logger.log_error(
                    label="unknown",
                    video_source="upload",
                    video_path=video_path,
                    error_message=str(e),
                )
            return f"Error: {str(e)}", 0.0, None

    def get_medical_terms_info(self) -> str:
        """Get information about supported medical terms"""
        if not self.label_map:
            return "Medical terms information not available"

        terms = self.label_map["medical_terms"]
        info = "**Supported Medical Terms:**\n\n"
        for i, term in enumerate(terms, 1):
            info += f"{i}. {term.replace('_', ' ').title()}\n"

        return info

    def get_audit_log(self) -> Tuple[str, str]:
        """Get audit log summary"""
        if not self.logger:
            return "Logger not available", ""

        summary = self.logger.get_log_summary()

        summary_text = f"""
**Prediction Summary:**
- Total predictions: {summary['total_predictions']}
- Successful: {summary['success_count']}
- Errors: {summary['error_count']}
- Average confidence: {summary['average_confidence']:.3f}

**Most common medical terms:**
"""

        label_dist = summary.get("label_distribution", {})
        for term, count in sorted(label_dist.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]:
            summary_text += f"\n- {term}: {count}"

        return summary_text, json.dumps(summary, indent=2)


def create_gradio_interface(app: MedicalSignLanguageApp) -> gr.Blocks:
    """Create Gradio interface for medical sign language recognition"""

    with gr.Blocks(title="MediSign - Medical Sign Language Recognition") as interface:
        gr.Markdown(
            """
        # 🏥 MediSign - Medical Sign Language Recognition
        
        Real-time medical sign language detection using BiLSTM+Attention neural networks.
        """
        )

        with gr.Tabs():
            # Inference tab
            with gr.TabItem("🎥 Inference"):
                with gr.Row():
                    with gr.Column():
                        video_input = gr.Video(label="Upload Medical Sign Video")
                        audio_toggle = gr.Checkbox(
                            value=True, label="Enable Audio Feedback"
                        )
                        infer_btn = gr.Button("Run Inference", variant="primary")

                    with gr.Column():
                        medical_term_output = gr.Textbox(
                            label="Predicted Medical Term", interactive=False
                        )
                        confidence_output = gr.Number(
                            label="Confidence Score", interactive=False
                        )
                        audio_output = gr.Audio(label="Audio Feedback", type="filepath", autoplay=True)

                infer_btn.click(
                    fn=app.infer_video,
                    inputs=[video_input, audio_toggle],
                    outputs=[medical_term_output, confidence_output, audio_output],
                )

            # Medical Terms tab
            with gr.TabItem("📚 Medical Terms"):
                terms_info = app.get_medical_terms_info()
                gr.Markdown(terms_info)

            # Audit Log tab
            with gr.TabItem("📊 Audit Log"):
                with gr.Row():
                    summary_box = gr.Textbox(
                        label="Summary Statistics", interactive=False, lines=10
                    )
                    details_box = gr.Textbox(
                        label="Detailed JSON", interactive=False, lines=10
                    )

                refresh_btn = gr.Button("Refresh Log")

                def refresh_log():
                    summary, details = app.get_audit_log()
                    return summary, details

                refresh_btn.click(fn=refresh_log, outputs=[summary_box, details_box])

                # Load initial data
                interface.load(fn=refresh_log, outputs=[summary_box, details_box])

    return interface


def main():
    print("\n" + "=" * 70)
    print("MediSign - Medical Sign Language Recognition System")
    print("=" * 70)

    # Initialize app
    app = MedicalSignLanguageApp(
        model_path="models/sequence_model_medical.keras",
        label_map_path="models/medical_terms_map.json",
        device="gpu",
        enable_tts=True,
    )

    # Create interface
    interface = create_gradio_interface(app)

    # Launch
    print("\nLaunching Gradio interface...")
    print("Open your browser to: http://localhost:7860")
    print("=" * 70 + "\n")

    interface.launch(server_name="0.0.0.0", server_port=7860, share=False)


if __name__ == "__main__":
    main()
