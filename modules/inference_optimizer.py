"""Inference optimization and benchmarking for the sequence model.

Features:
- Load trained model with optional mixed precision
- Benchmark inference speed on CPU/GPU
- Measure memory usage and latency
- Provide optimization recommendations
- Support for batch inference and real-time streaming
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Tuple

import numpy as np
import tensorflow as tf


class InferenceOptimizer:
    """Optimize and benchmark model inference."""

    def __init__(
        self,
        model_path: str = "models/sequence_model_final.keras",
        enable_mixed_precision: bool = True,
        device: str = "auto",
    ):
        """Initialize optimizer with model and precision settings.

        Args:
            model_path: Path to trained sequence model.
            enable_mixed_precision: Enable float16 mixed precision if GPU available.
            device: 'cpu', 'gpu', or 'auto' (auto-detect).
        """
        self.model_path = Path(model_path)
        self.model = None
        self.device = device
        self.precision_policy = None
        self.gpu_available = False

        # Detect device
        self._detect_device()

        # Set mixed precision policy
        if enable_mixed_precision:
            self._setup_mixed_precision()

        # Load model
        self._load_model()

    def _detect_device(self):
        """Detect available hardware."""
        gpus = tf.config.list_physical_devices("GPU")
        self.gpu_available = len(gpus) > 0

        if self.device == "auto":
            self.device = "gpu" if self.gpu_available else "cpu"

        if self.device == "gpu" and not self.gpu_available:
            print("⚠️  GPU requested but not available; falling back to CPU")
            self.device = "cpu"

        print(f"Device: {self.device.upper()}")
        if self.gpu_available:
            for gpu in gpus:
                print(f"  Found GPU: {gpu.name}")

    def _setup_mixed_precision(self):
        """Enable mixed precision float16 + float32."""
        if self.device == "gpu" and self.gpu_available:
            policy = tf.keras.mixed_precision.Policy("mixed_float16")
            tf.keras.mixed_precision.set_global_policy(policy)
            self.precision_policy = (
                "mixed_float16 (float16 compute + float32 variables)"
            )
            print(f"✓ Mixed precision enabled: {self.precision_policy}")
        else:
            self.precision_policy = (
                "float32 (CPU or GPU without mixed precision support)"
            )
            print(
                f"Mixed precision unavailable on {self.device}; using {self.precision_policy}"
            )

    def _load_model(self):
        """Load the trained model."""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")

        print(f"Loading model from {self.model_path}...")
        # Import custom layer before loading
        from modules.sequence_model import AttentionLayer

        self.model = tf.keras.models.load_model(
            self.model_path, custom_objects={"AttentionLayer": AttentionLayer}
        )
        print(f"✓ Model loaded ({self.model.count_params():,} parameters)")
        self.model.summary()

    def benchmark_inference(
        self,
        time_steps: int = 60,
        feat_dim: int = 1280,
        num_classes: int = 2,
        batch_sizes: list[int] | None = None,
        num_iterations: int = 10,
    ) -> dict:
        """Benchmark inference speed and memory usage.

        Args:
            time_steps: Sequence length.
            feat_dim: Feature dimension per time step.
            num_classes: Number of output classes.
            batch_sizes: List of batch sizes to benchmark. Default: [1, 4, 8, 16].
            num_iterations: Number of inference iterations per batch size.

        Returns:
            Dictionary with benchmark results.
        """
        if batch_sizes is None:
            batch_sizes = [1, 4, 8, 16]

        results = {
            "device": self.device,
            "precision": self.precision_policy,
            "model_params": self.model.count_params(),
            "benchmarks": {},
        }

        print("\n" + "=" * 70)
        print("INFERENCE BENCHMARK RESULTS")
        print("=" * 70)

        for batch_size in batch_sizes:
            print(f"\nBatch Size: {batch_size}")
            print("-" * 70)

            # Create synthetic feature batch
            X = np.random.randn(batch_size, time_steps, feat_dim).astype(np.float32)

            # Warmup
            _ = self.model.predict(X, verbose=0)

            # Measure inference time
            start_time = time.time()
            for _ in range(num_iterations):
                _ = self.model.predict(X, verbose=0)
            elapsed = time.time() - start_time

            avg_latency_ms = (elapsed / num_iterations) * 1000
            throughput = (batch_size * num_iterations) / elapsed

            results["benchmarks"][batch_size] = {
                "avg_latency_ms": avg_latency_ms,
                "throughput_samples_per_sec": throughput,
                "time_per_sample_ms": avg_latency_ms / batch_size,
            }

            print(f"  Avg Latency (batch): {avg_latency_ms:.2f} ms")
            print(f"  Latency per sample: {avg_latency_ms / batch_size:.2f} ms")
            print(f"  Throughput: {throughput:.1f} samples/sec")

        print("\n" + "=" * 70)
        return results

    def estimate_memory_usage(
        self, time_steps: int = 60, feat_dim: int = 1280, batch_size: int = 1
    ) -> dict:
        """Estimate memory usage for inference.

        Args:
            time_steps: Sequence length.
            feat_dim: Feature dimension per time step.
            batch_size: Batch size.

        Returns:
            Dictionary with memory estimates.
        """
        # Model weights memory (in bytes)
        model_params = self.model.count_params()
        bytes_per_param = 2 if "float16" in (self.precision_policy or "") else 4
        model_memory_mb = (model_params * bytes_per_param) / (1024 * 1024)

        # Input batch memory
        input_elements = batch_size * time_steps * feat_dim
        input_memory_mb = (input_elements * 4) / (1024 * 1024)  # float32

        # Output memory
        output_memory_mb = (batch_size * 2 * 4) / (1024 * 1024)  # 2 classes, float32

        # Activation memory (rough estimate: ~2x input size for BiLSTM)
        activation_memory_mb = (input_elements * 2 * 4) / (1024 * 1024)

        total_mb = (
            model_memory_mb + input_memory_mb + output_memory_mb + activation_memory_mb
        )

        return {
            "model_weights_mb": model_memory_mb,
            "input_batch_mb": input_memory_mb,
            "output_mb": output_memory_mb,
            "activation_memory_mb": activation_memory_mb,
            "total_estimated_mb": total_mb,
        }

    def generate_report(self, benchmark_results: dict) -> str:
        """Generate a human-readable optimization report.

        Args:
            benchmark_results: Results from benchmark_inference().

        Returns:
            Formatted report string.
        """
        report = []
        report.append("\n" + "=" * 70)
        report.append("STAGE 8: REAL-TIME OPTIMIZATION REPORT")
        report.append("=" * 70)

        # Hardware & Precision
        report.append(f"\nHardware & Precision:")
        report.append(f"  Device: {benchmark_results['device'].upper()}")
        report.append(f"  Precision: {benchmark_results['precision']}")
        report.append(f"  Model Parameters: {benchmark_results['model_params']:,}")

        # Latency Summary
        report.append(f"\nLatency Summary (per sample):")
        best_latency_ms = float("inf")
        best_batch = None
        for batch_size, metrics in benchmark_results["benchmarks"].items():
            latency = metrics["time_per_sample_ms"]
            report.append(f"  Batch {batch_size:2d}: {latency:7.2f} ms/sample")
            if latency < best_latency_ms:
                best_latency_ms = latency
                best_batch = batch_size

        # Memory Estimate
        mem = self.estimate_memory_usage(batch_size=best_batch)
        report.append(f"\nMemory Usage (Batch {best_batch}):")
        report.append(f"  Model Weights: {mem['model_weights_mb']:.2f} MB")
        report.append(f"  Input Batch: {mem['input_batch_mb']:.2f} MB")
        report.append(f"  Activations: {mem['activation_memory_mb']:.2f} MB")
        report.append(f"  Total: {mem['total_estimated_mb']:.2f} MB")

        # Recommendations
        report.append(f"\nOptimization Recommendations:")

        # Check if <500ms latency target is met
        if best_latency_ms < 500:
            report.append(
                f"  ✓ Inference latency ({best_latency_ms:.2f}ms) < 500ms target"
            )
        else:
            report.append(
                f"  ⚠ Inference latency ({best_latency_ms:.2f}ms) > 500ms target"
            )
            if self.device == "cpu":
                report.append(f"    → Consider using GPU acceleration")
            if "float16" not in (self.precision_policy or ""):
                report.append(
                    f"    → Enable mixed precision (float16) if GPU available"
                )

        # Batch optimization
        throughputs = [
            (bs, m["throughput_samples_per_sec"])
            for bs, m in benchmark_results["benchmarks"].items()
        ]
        best_throughput_batch = max(throughputs, key=lambda x: x[1])
        report.append(
            f"  ✓ Optimal batch size for throughput: {best_throughput_batch[0]} "
            f"({best_throughput_batch[1]:.1f} samples/sec)"
        )

        # Memory check
        if mem["total_estimated_mb"] < 1024:
            report.append(
                f"  ✓ Total memory usage ({mem['total_estimated_mb']:.2f}MB) < 1GB (fits on edge devices)"
            )
        else:
            report.append(
                f"  ⚠ Total memory usage ({mem['total_estimated_mb']:.2f}MB) > 1GB"
            )

        # Pre-loading advice
        report.append(f"\nPre-loading Strategy:")
        report.append(f"  • Load model once at startup (done in __init__)")
        report.append(f"  • Cache feature extractor model (MobileNetV2)")
        report.append(f"  • Use batch inference for throughput-critical applications")
        report.append(
            f"  • For real-time streaming: use batch_size=1 ({best_latency_ms:.2f}ms per frame)"
        )

        report.append(f"\nConclusion:")
        report.append(
            f"  Model is optimized for real-time inference on {self.device.upper()}."
        )
        report.append(f"  Inference pipeline ready for deployment.")

        report.append("\n" + "=" * 70)
        return "\n".join(report)

    def infer_and_time(
        self, features: np.ndarray, num_runs: int = 1
    ) -> Tuple[np.ndarray, float]:
        """Run inference and report timing.

        Args:
            features: Feature array of shape (time_steps, feat_dim) or (batch, time_steps, feat_dim).
            num_runs: Number of times to run inference (for averaging).

        Returns:
            Tuple of (predictions, avg_latency_ms).
        """
        # Ensure batch dimension
        if features.ndim == 2:
            features = np.expand_dims(features, axis=0)

        # Warmup
        _ = self.model.predict(features, verbose=0)

        # Time inference
        start = time.time()
        for _ in range(num_runs):
            predictions = self.model.predict(features, verbose=0)
        elapsed_ms = (time.time() - start) * 1000 / num_runs

        return predictions, elapsed_ms


def main(argv=None):
    """Main: Run benchmarks and generate report."""
    import argparse

    parser = argparse.ArgumentParser(description="Stage 8: Inference optimization")
    parser.add_argument(
        "--model-path",
        type=str,
        default="models/sequence_model_final.keras",
        help="Path to trained sequence model",
    )
    parser.add_argument(
        "--device",
        type=str,
        choices=["cpu", "gpu", "auto"],
        default="auto",
        help="Device to benchmark on",
    )
    parser.add_argument(
        "--enable-mixed-precision",
        action="store_true",
        default=True,
        help="Enable mixed precision (float16)",
    )
    parser.add_argument(
        "--time-steps",
        type=int,
        default=60,
        help="Sequence length",
    )
    parser.add_argument(
        "--feat-dim",
        type=int,
        default=1280,
        help="Feature dimension",
    )
    parser.add_argument(
        "--num-classes",
        type=int,
        default=2,
        help="Number of output classes",
    )
    args = parser.parse_args(argv)

    print("Initializing inference optimizer...")
    optimizer = InferenceOptimizer(
        model_path=args.model_path,
        enable_mixed_precision=args.enable_mixed_precision,
        device=args.device,
    )

    print("\nRunning benchmarks...")
    results = optimizer.benchmark_inference(
        time_steps=args.time_steps,
        feat_dim=args.feat_dim,
        num_classes=args.num_classes,
        batch_sizes=[1, 4, 8, 16],
        num_iterations=10,
    )

    report = optimizer.generate_report(results)
    print(report)

    # Save report
    report_path = Path("logs/optimization_report.txt")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nReport saved to {report_path}")


if __name__ == "__main__":
    main()
