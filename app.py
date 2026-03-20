"""
medisign.app — Gradio web interface for real-time medical sign language detection.

        with gr.Blocks(title="MediSign — Medical Sign Language Detector") as demo:
            # Login / Home area
            with gr.Column():
                login_col = gr.Column(visible=True)
                with login_col:
                    gr.Markdown("# 🏥 Welcome to MediSign")
                    gr.Markdown(
                        "Upload or record medical sign videos and get instant predictions with audio feedback."
                    )
                    username = gr.Textbox(label="Username", placeholder="admin")
                    password = gr.Textbox(label="Password", type="password")
                    login_msg = gr.Markdown(" ")
                    login_btn = gr.Button("Sign In", variant="primary")

                main_col = gr.Column(visible=False)
                with main_col:
                    # Home / hero section
                    gr.Markdown(
                        "## MediSign — Medical Sign Language Detection"
                        "\n\n"
                        "Real-time detection using BiLSTM+Attention. Use the tabs below to upload videos, record from webcam, view supported terms, and audit logs."
                    )

                    logout_btn = gr.Button("Logout", variant="secondary")

                    with gr.Tabs():
                        # Tab 1: File upload
                        with gr.Tab("Upload Video"):
                            video_input = gr.Video(label="Upload Video (MP4, MOV, etc.)")

                            with gr.Row():
                                upload_button = gr.Button("Predict", variant="primary")
                                enable_audio_upload = gr.Checkbox(label="Generate Audio", value=True)

                            with gr.Row():
                                with gr.Column():
                                    pred_label = gr.Textbox(label="Predicted Sign", interactive=False, scale=2)
                                with gr.Column():
                                    confidence = gr.Slider(label="Confidence", minimum=0.0, maximum=1.0, interactive=False, scale=1)

                            audio_output_upload = gr.Audio(label="Predicted Audio (click to play)", type="filepath")

                            upload_button.click(fn=self.infer_video, inputs=[video_input, enable_audio_upload], outputs=[pred_label, confidence, audio_output_upload])

                        # Tab 2: Webcam
                        with gr.Tab("Live Webcam"):
                            gr.Markdown("Record a video from your webcam and click **Predict** to analyze it.")
                            webcam_input = gr.Video(label="Webcam Recording", sources=["webcam"])

                            with gr.Row():
                                webcam_button = gr.Button("Predict from Webcam", variant="primary")
                                enable_audio_webcam = gr.Checkbox(label="Generate Audio", value=True)

                            with gr.Row():
                                with gr.Column():
                                    webcam_label = gr.Textbox(label="Predicted Sign", interactive=False, scale=2)
                                with gr.Column():
                                    webcam_conf = gr.Slider(label="Confidence", minimum=0.0, maximum=1.0, interactive=False, scale=1)

                            audio_output_webcam = gr.Audio(label="Predicted Audio (click to play)", type="filepath")

                            webcam_button.click(fn=self.infer_video, inputs=[webcam_input, enable_audio_webcam], outputs=[webcam_label, webcam_conf, audio_output_webcam])

                        # Tab 3: Info
                        with gr.Tab("Info"):
                            info_text = f"""
## Model Information
- **Model Type**: BiLSTMx2 + Self-Attention
-- **Input**: 60 frames @ 224x224 px
- **Feature Extraction**: MobileNetV2 (1280-dim per frame)
- **Classes**: {len(self.label_names)} ({', '.join(self.label_names)})
- **Model Path**: {Path('models/sequence_model_final.keras').resolve()}

## Audio Feedback
- **Engine**: Google Text-to-Speech (gTTS)
- **Language**: English
- **Output**: MP3 files saved to `logs/audio/`

## How It Works
1. Video is preprocessed to extract exactly 60 frames
2. Each frame is resized to 224x224 and normalized
3. MobileNetV2 extracts 1280-dimensional feature vectors
4. BiLSTMx2 processes the temporal sequence
5. Self-attention aggregates the sequence
6. Final Dense layer outputs class probabilities
7. Predicted label is converted to speech using gTTS

## Requirements
- Video must be a valid MP4, MOV, or similar format
- Optimal video length: 2–3 seconds
"""
                            gr.Markdown(info_text)

                        # Tab 4: Audit Log
                        with gr.Tab("Audit Log"):
                            gr.Markdown("## Prediction Audit Log")
                            gr.Markdown("Below is a summary of all predictions logged in `logs/predictions.csv`")

                            with gr.Row():
                                refresh_log_button = gr.Button("Refresh Log Summary", variant="secondary")
                                export_button = gr.Button("Export as CSV", variant="secondary")

                            log_summary = gr.Textbox(label="Log Summary Statistics", interactive=False, lines=12, max_lines=20)
                            recent_predictions = gr.Dataframe(label="Recent Predictions", interactive=False)

                            def get_log_summary_text():
                                if not self.logger:
                                    return "Logger not initialized"

                                summary = self.logger.get_log_summary()
                                text = f"""
Total Predictions: {summary.get('total_predictions', 0)}
  ✓ Successful: {summary.get('success_count', 0)}
  ❌ Errors: {summary.get('error_count', 0)}

Average Confidence: {summary.get('average_confidence', 0):.4f}

Label Distribution:
"""
                                for label, count in sorted(summary.get("label_distribution", {}).items(), key=lambda x: x[1], reverse=True):
                                    text += f"  - {label}: {count}\n"

                                return text

                            def get_recent_predictions_df():
                                if not self.logger:
                                    return []

                            refresh_log_button.click(fn=get_log_summary_text, inputs=None, outputs=log_summary).then(fn=get_recent_predictions_df, inputs=None, outputs=recent_predictions)

                            export_button.click(fn=lambda: f"Export ready. Download from: {self.logger.log_file if self.logger else 'N/A'}", outputs=log_summary)

                # Login validation function
                def check_login(username, password):
                    expected_user = os.environ.get("MEDISIGN_USER", "admin")
                    expected_pass = os.environ.get("MEDISIGN_PASS", "password")
                    if username == expected_user and password == expected_pass:
                        return gr.update(visible=False), gr.update(visible=True), gr.update(value="")
                    else:
                        return gr.update(visible=True), gr.update(visible=False), gr.update(value="**Invalid credentials.**")

                def do_logout():
                    return gr.update(visible=True), gr.update(visible=False), gr.update(value="")

                login_btn.click(fn=check_login, inputs=[username, password], outputs=[login_col, main_col, login_msg])
                logout_btn.click(fn=do_logout, outputs=[login_col, main_col, login_msg])
        except Exception as e:
            print(f"Inference error: {e}")
            import traceback

            traceback.print_exc()

            # Log error
            if self.logger:
                video_source = (
                    "webcam" if video_path and "tmp" in video_path else "upload"
                )
                self.logger.log_error(
                    label="unknown",
                    video_source=video_source,
                    video_path=video_path,
                    error_message=str(e),
                )

            return f"Error: {str(e)}", 0.0, None

    def build_interface(self) -> gr.Blocks:
        """Build the Gradio web interface with TTS."""
        with gr.Blocks(title="MediSign — Medical Sign Language Detector") as demo:
            gr.Markdown("# MediSign: Medical Sign Language Detection + Audio Feedback")
            gr.Markdown(
                "Upload a video or record live to detect medical signs. "
                "The model analyzes 60 frames using BiLSTM+Attention and provides audio feedback."
            )

            with gr.Tabs():
                # Tab 1: File upload
                with gr.Tab("Upload Video"):
                    video_input = gr.Video(
                        label="Upload Video (MP4, MOV, etc.)",
                    )

                    with gr.Row():
                        upload_button = gr.Button("Predict", variant="primary")
                        enable_audio_upload = gr.Checkbox(
                            label="Generate Audio", value=True
                        )

                    with gr.Row():
                        with gr.Column():
                            pred_label = gr.Textbox(
                                label="Predicted Sign",
                                interactive=False,
                                scale=2,
                            )
                        with gr.Column():
                            confidence = gr.Slider(
                                label="Confidence",
                                minimum=0.0,
                                maximum=1.0,
                                interactive=False,
                                scale=1,
                            )

                    # Audio output
                    audio_output_upload = gr.Audio(
                        label="Predicted Audio (click to play)",
                        type="filepath",
                    )

                    upload_button.click(
                        fn=self.infer_video,
                        inputs=[video_input, enable_audio_upload],
                        outputs=[pred_label, confidence, audio_output_upload],
                    )

                # Tab 2: Webcam
                with gr.Tab("Live Webcam"):
                    gr.Markdown(
                        "Record a video from your webcam and click **Predict** to analyze it. "
                        "The model will detect the medical sign language gesture and speak the result."
                    )
                    webcam_input = gr.Video(
                        label="Webcam Recording",
                        sources=["webcam"],
                    )

                    with gr.Row():
                        webcam_button = gr.Button(
                            "Predict from Webcam", variant="primary"
                        )
                        enable_audio_webcam = gr.Checkbox(
                            label="Generate Audio", value=True
                        )

                    with gr.Row():
                        with gr.Column():
                            webcam_label = gr.Textbox(
                                label="Predicted Sign",
                                interactive=False,
                                scale=2,
                            )
                        with gr.Column():
                            webcam_conf = gr.Slider(
                                label="Confidence",
                                minimum=0.0,
                                maximum=1.0,
                                interactive=False,
                                scale=1,
                            )

                    # Audio output
                    audio_output_webcam = gr.Audio(
                        label="Predicted Audio (click to play)",
                        type="filepath",
                    )

                    webcam_button.click(
                        fn=self.infer_video,
                        inputs=[webcam_input, enable_audio_webcam],
                        outputs=[webcam_label, webcam_conf, audio_output_webcam],
                    )

                # Tab 3: Info
                with gr.Tab("Info"):
                    info_text = f"""
## Model Information
- **Model Type**: BiLSTM×2 + Self-Attention
- **Input**: 60 frames @ 224×224 px
- **Feature Extraction**: MobileNetV2 (1280-dim per frame)
- **Classes**: {len(self.label_names)} ({', '.join(self.label_names)})
- **Model Path**: {Path('models/sequence_model_final.keras').resolve()}

## Audio Feedback
- **Engine**: Google Text-to-Speech (gTTS)
- **Language**: English
- **Output**: MP3 files saved to `logs/audio/`
- **Format**: `<label>_<timestamp>.mp3`

## How It Works
1. Video is preprocessed to extract exactly 60 frames
2. Each frame is resized to 224x224 and normalized
3. MobileNetV2 extracts 1280-dimensional feature vectors
4. BiLSTMx2 processes the temporal sequence
5. Self-attention aggregates the sequence
6. Final Dense layer outputs class probabilities
7. **NEW**: Predicted label is converted to speech using gTTS
8. Audio file is saved and played in the UI

## Requirements
- Video must be a valid MP4, MOV, or similar format
- Optimal video length: 2–3 seconds
- The more clear and frontal the hand gesture, the better the prediction accuracy
- Audio feedback requires internet connection (gTTS API)

## Audio Files
- Saved to: `logs/audio/`
- Playable directly in the interface
- Named with timestamp for auditing
"""
                    gr.Markdown(info_text)

                # Tab 4: Audit Log
                with gr.Tab("Audit Log"):
                    gr.Markdown("## Prediction Audit Log")
                    gr.Markdown(
                        "Below is a summary of all predictions logged in `logs/predictions.csv`"
                    )

                    with gr.Row():
                        refresh_log_button = gr.Button(
                            "Refresh Log Summary", variant="secondary"
                        )
                        export_button = gr.Button("Export as CSV", variant="secondary")

                    log_summary = gr.Textbox(
                        label="Log Summary Statistics",
                        interactive=False,
                        lines=12,
                        max_lines=20,
                    )

                    recent_predictions = gr.Dataframe(
                        label="Recent Predictions",
                        interactive=False,
                    )

                    def get_log_summary_text():
                        """Get formatted log summary."""
                        if not self.logger:
                            return "Logger not initialized"

                        summary = self.logger.get_log_summary()
                        text = f"""
Total Predictions: {summary.get('total_predictions', 0)}
  ✓ Successful: {summary.get('success_count', 0)}
  ❌ Errors: {summary.get('error_count', 0)}

Average Confidence: {summary.get('average_confidence', 0):.4f}

Label Distribution:
"""
                        for label, count in sorted(
                            summary.get("label_distribution", {}).items(),
                            key=lambda x: x[1],
                            reverse=True,
                        ):
                            text += f"  - {label}: {count}\n"

                        return text

                    def get_recent_predictions_df():
                        """Get recent predictions as dataframe."""
                        if not self.logger:
                            return []

                        recent = self.logger.get_recent_predictions(limit=20)
                        return recent

                    refresh_log_button.click(
                        fn=get_log_summary_text,
                        inputs=None,
                        outputs=log_summary,
                    ).then(
                        fn=get_recent_predictions_df,
                        inputs=None,
                        outputs=recent_predictions,
                    )

                    export_button.click(
                        fn=lambda: f"Export ready. Download from: {self.logger.log_file if self.logger else 'N/A'}",
                        outputs=log_summary,
                    )

        return demo


def main(argv=None):
    """Launch the Gradio app."""
    import argparse

    parser = argparse.ArgumentParser(description="MediSign Gradio app with TTS")
    parser.add_argument(
        "--model-path",
        type=str,
        default="models/sequence_model_final.keras",
        help="Path to trained sequence model",
    )
    parser.add_argument(
        "--dataset-dir",
        type=str,
        default="dataset",
        help="Dataset directory for label discovery",
    )
    parser.add_argument(
        "--device", type=str, default="cpu", help="Device: 'cpu' or 'gpu'"
    )
    parser.add_argument(
        "--enable-tts",
        action="store_true",
        default=True,
        help="Enable text-to-speech",
    )
    parser.add_argument(
        "--share",
        action="store_true",
        help="Share the app publicly via Gradio link",
    )
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=7860, help="Port to bind to")
    args = parser.parse_args(argv)

    print(f"Starting MediSign app on {args.host}:{args.port}...")
    app = MedisignApp(
        model_path=args.model_path,
        label_map_path=args.dataset_dir,
        device=args.device,
        enable_tts=args.enable_tts,
    )
    demo = app.build_interface()
    demo.launch(
        server_name=args.host,
        server_port=args.port,
        share=args.share,
        show_error=True,
    )


if __name__ == "__main__":
    main()
