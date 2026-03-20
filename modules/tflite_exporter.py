"""
TFLite Export Module — Convert and optimize Keras model for mobile deployment.

Features:
- Load trained Keras model with custom layers
- Apply model quantization (int8, float16)
- Convert to TensorFlow Lite format
- Benchmark TFLite model inference
- Save optimized models for mobile deployment
"""

from __future__ import annotations

import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # Suppress TF logs

from pathlib import Path
from typing import Dict, Tuple, Optional, List
import time
import numpy as np

try:
    import tensorflow as tf

    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False


class TFLiteExporter:
    """Export and optimize models for TensorFlow Lite."""

    def __init__(self, model_path: str = "models/sequence_model_final.keras"):
        """Initialize TFLite exporter.

        Args:
            model_path: Path to trained Keras model.
        """
        self.model_path = Path(model_path)
        self.model = None
        self.output_dir = Path("models/tflite")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print(f"✓ TFLiteExporter initialized")
        print(f"  - Model path: {model_path}")
        print(f"  - Output dir: {self.output_dir}")

    def load_model(self) -> bool:
        """Load Keras model with custom layers.

        Returns:
            True if model loaded successfully, False otherwise.
        """
        if not TF_AVAILABLE:
            print("❌ TensorFlow not available")
            return False

        if not self.model_path.exists():
            print(f"❌ Model not found: {self.model_path}")
            return False

        try:
            print(f"\nLoading model: {self.model_path}")
            from modules.sequence_model import AttentionLayer

            self.model = tf.keras.models.load_model(
                self.model_path, custom_objects={"AttentionLayer": AttentionLayer}
            )
            print(f"✓ Model loaded successfully")
            print(f"  - Input shape: {self.model.input_shape}")
            print(f"  - Output shape: {self.model.output_shape}")
            print(f"  - Parameters: {self.model.count_params():,}")
            return True

        except Exception as e:
            print(f"❌ Model loading failed: {e}")
            import traceback

            traceback.print_exc()
            return False

    def get_model_size_mb(self, file_path: Path) -> float:
        """Get file size in MB.

        Args:
            file_path: Path to file.

        Returns:
            File size in MB.
        """
        return file_path.stat().st_size / (1024 * 1024)

    def export_tflite_float32(self) -> Optional[Path]:
        """Export model as TFLite float32.

        Returns:
            Path to exported model or None.
        """
        if self.model is None:
            print("⚠ Model not loaded")
            return None

        try:
            print(f"\n{'=' * 80}")
            print("Converting to TFLite (Float32)")
            print(f"{'=' * 80}")

            converter = tf.lite.TFLiteConverter.from_keras_model(self.model)
            converter.optimizations = []  # No quantization for baseline
            converter.target_spec.supported_ops = [
                tf.lite.OpsSet.TFLITE_BUILTINS,
            ]

            tflite_model = converter.convert()
            output_path = self.output_dir / "model_float32.tflite"

            with open(output_path, "wb") as f:
                f.write(tflite_model)

            size_mb = self.get_model_size_mb(output_path)
            print(f"✓ TFLite Float32 exported")
            print(f"  - File: {output_path.name}")
            print(f"  - Size: {size_mb:.2f} MB")

            return output_path

        except Exception as e:
            print(f"❌ Float32 conversion failed: {e}")
            return None

    def export_tflite_fp16(self) -> Optional[Path]:
        """Export model as TFLite with float16 quantization.

        Returns:
            Path to exported model or None.
        """
        if self.model is None:
            print("⚠ Model not loaded")
            return None

        try:
            print(f"\n{'=' * 80}")
            print("Converting to TFLite (Float16 Quantization)")
            print(f"{'=' * 80}")

            converter = tf.lite.TFLiteConverter.from_keras_model(self.model)
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            converter.target_spec.supported_types = [tf.float16]
            converter.target_spec.supported_ops = [
                tf.lite.OpsSet.TFLITE_BUILTINS,
            ]

            tflite_model = converter.convert()
            output_path = self.output_dir / "model_fp16.tflite"

            with open(output_path, "wb") as f:
                f.write(tflite_model)

            size_mb = self.get_model_size_mb(output_path)
            print(f"✓ TFLite Float16 exported")
            print(f"  - File: {output_path.name}")
            print(f"  - Size: {size_mb:.2f} MB")

            return output_path

        except Exception as e:
            print(f"❌ Float16 conversion failed: {e}")
            return None

    def export_tflite_int8(
        self, representative_data: Optional[np.ndarray] = None
    ) -> Optional[Path]:
        """Export model as TFLite with int8 quantization.

        Args:
            representative_data: Representative dataset for quantization.

        Returns:
            Path to exported model or None.
        """
        if self.model is None:
            print("⚠ Model not loaded")
            return None

        try:
            print(f"\n{'=' * 80}")
            print("Converting to TFLite (Int8 Quantization)")
            print(f"{'=' * 80}")

            converter = tf.lite.TFLiteConverter.from_keras_model(self.model)
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            converter.target_spec.supported_ops = [
                tf.lite.OpsSet.TFLITE_BUILTINS_INT8,
            ]

            # If representative data provided, use it for calibration
            if representative_data is not None:

                def representative_dataset():
                    for i in range(min(10, len(representative_data))):
                        data = representative_data[i : i + 1].astype(np.float32)
                        yield [data]

                converter.representative_dataset = representative_dataset
                converter.target_spec.supported_ops = [
                    tf.lite.OpsSet.TFLITE_BUILTINS_INT8
                ]
                converter.inference_input_type = tf.int8
                converter.inference_output_type = tf.int8

            tflite_model = converter.convert()
            output_path = self.output_dir / "model_int8.tflite"

            with open(output_path, "wb") as f:
                f.write(tflite_model)

            size_mb = self.get_model_size_mb(output_path)
            print(f"✓ TFLite Int8 exported")
            print(f"  - File: {output_path.name}")
            print(f"  - Size: {size_mb:.2f} MB")

            return output_path

        except Exception as e:
            print(f"❌ Int8 conversion failed: {e}")
            import traceback

            traceback.print_exc()
            return None

    def benchmark_tflite(
        self, model_path: Path, test_data: np.ndarray, num_runs: int = 100
    ) -> Dict:
        """Benchmark TFLite model inference.

        Args:
            model_path: Path to TFLite model.
            test_data: Test input data (batch).
            num_runs: Number of inference runs.

        Returns:
            Dictionary with benchmark results.
        """
        if not TF_AVAILABLE:
            print("⚠ TensorFlow not available for benchmarking")
            return {}

        try:
            print(f"\nBenchmarking: {model_path.name}")

            # Load TFLite interpreter
            interpreter = tf.lite.Interpreter(model_path=str(model_path))
            interpreter.allocate_tensors()

            # Get input/output details
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()

            print(f"  - Input shape: {input_details[0]['shape']}")
            print(f"  - Output shape: {output_details[0]['shape']}")

            # Warm up
            test_batch = test_data[:1].astype(np.float32)
            interpreter.set_tensor(input_details[0]["index"], test_batch)
            interpreter.invoke()

            # Benchmark
            latencies = []
            for i in range(num_runs):
                test_batch = test_data[
                    i % len(test_data) : (i % len(test_data)) + 1
                ].astype(np.float32)

                start = time.time()
                interpreter.set_tensor(input_details[0]["index"], test_batch)
                interpreter.invoke()
                end = time.time()

                latency_ms = (end - start) * 1000
                latencies.append(latency_ms)

            latencies = np.array(latencies)

            results = {
                "model": model_path.name,
                "file_size_mb": self.get_model_size_mb(model_path),
                "num_runs": num_runs,
                "mean_latency_ms": float(np.mean(latencies)),
                "median_latency_ms": float(np.median(latencies)),
                "min_latency_ms": float(np.min(latencies)),
                "max_latency_ms": float(np.max(latencies)),
                "std_latency_ms": float(np.std(latencies)),
                "throughput_samples_per_sec": 1000.0 / float(np.mean(latencies)),
            }

            print(f"  ✓ Benchmarking complete")
            print(f"    - Mean latency: {results['mean_latency_ms']:.2f} ms")
            print(f"    - Median latency: {results['median_latency_ms']:.2f} ms")
            print(
                f"    - Throughput: {results['throughput_samples_per_sec']:.1f} samples/sec"
            )

            return results

        except Exception as e:
            print(f"❌ Benchmarking failed: {e}")
            import traceback

            traceback.print_exc()
            return {}

    def export_all(
        self, representative_data: Optional[np.ndarray] = None
    ) -> Dict[str, Path]:
        """Export model in all formats.

        Args:
            representative_data: Optional representative dataset for int8 calibration.

        Returns:
            Dictionary mapping format_name to output_path.
        """
        if self.model is None:
            if not self.load_model():
                return {}

        results = {}

        # Export formats
        fp32_path = self.export_tflite_float32()
        if fp32_path:
            results["float32"] = fp32_path

        fp16_path = self.export_tflite_fp16()
        if fp16_path:
            results["fp16"] = fp16_path

        int8_path = self.export_tflite_int8(representative_data)
        if int8_path:
            results["int8"] = int8_path

        return results

    def compare_models(self, model_paths: List[Path]) -> None:
        """Compare model sizes and characteristics.

        Args:
            model_paths: List of model paths to compare.
        """
        print(f"\n{'=' * 80}")
        print("Model Comparison")
        print(f"{'=' * 80}")

        print(f"\n{'Model':<25} {'Size (MB)':<15} {'Compression':<15}")
        print(f"{'-' * 55}")

        original_size = (
            self.get_model_size_mb(self.model_path)
            if self.model_path.exists()
            else None
        )

        for path in model_paths:
            if path and path.exists():
                size_mb = self.get_model_size_mb(path)
                compression = ""
                if original_size:
                    ratio = (1 - size_mb / original_size) * 100
                    compression = f"{ratio:.1f}%"
                print(f"{path.name:<25} {size_mb:<15.2f} {compression:<15}")


def main(argv=None):
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Export Keras model to TFLite")
    parser.add_argument(
        "--model-path",
        type=str,
        default="models/sequence_model_final.keras",
        help="Path to Keras model",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="models/tflite",
        help="Output directory for TFLite models",
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Run benchmarking",
    )
    args = parser.parse_args(argv)

    if not TF_AVAILABLE:
        print("❌ TensorFlow is required for TFLite export")
        return

    exporter = TFLiteExporter(model_path=args.model_path)

    if not exporter.load_model():
        print("❌ Failed to load model")
        return

    # Export models
    results = exporter.export_all()

    if not results:
        print("❌ Export failed")
        return

    print(f"\n✓ Export complete: {len(results)} models exported")

    # Benchmark if requested
    if args.benchmark:
        print(f"\n{'=' * 80}")
        print("Running Benchmarks")
        print(f"{'=' * 80}")

        # Generate test data
        test_data = np.random.randn(10, 60, 1280).astype(np.float32)

        for model_type, model_path in results.items():
            exporter.benchmark_tflite(model_path, test_data, num_runs=50)

    # Compare models
    model_paths = list(results.values())
    exporter.compare_models(model_paths)

    print(f"\n✓ TFLite export and benchmark complete!")


if __name__ == "__main__":
    main()
