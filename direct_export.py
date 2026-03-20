"""
Stage 13: Direct TFLite Export Script
Simplified export with error handling and timeout support
"""

import os
import sys
import time
import subprocess
import platform


def setup_environment():
    """Set up environment variables to minimize TensorFlow issues"""
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"  # Suppress TF warnings
    os.environ["HDF5_PLUGIN_PATH"] = ""  # Disable h5py plugins
    os.environ["TF_FORCE_GPU_ALLOW_GROWTH"] = "true"


def run_export_with_timeout(timeout_sec=120):
    """Run export in subprocess with timeout"""
    script = """
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['HDF5_PLUGIN_PATH'] = ''

import sys
sys.path.insert(0, '.')

from modules.tflite_exporter import TFLiteExporter
import numpy as np

print("")
print("=" * 60)
print("STAGE 13: TFLite Model Export & Quantization")
print("=" * 60)
print("")

try:
    # Initialize exporter
    print("[1/6] Initializing TFLiteExporter...")
    exporter = TFLiteExporter(
        model_path="models/sequence_model_final.keras"
    )
    print("[OK] Exporter initialized")
    
    # Load model
    print("")
    print("[2/6] Loading Keras model...")
    model = exporter.load_model()
    print(f"[OK] Model loaded: {model.input_shape} -> {model.output_shape}")
    
    # Export all formats
    print("")
    print("[3/6] Exporting to Float32...")
    fp32_path = exporter.export_tflite_float32()
    print(f"[OK] Exported: {fp32_path}")
    
    print("")
    print("[4/6] Exporting to Float16 (quantized)...")
    fp16_path = exporter.export_tflite_fp16()
    print(f"[OK] Exported: {fp16_path}")
    
    print("")
    print("[5/6] Exporting to Int8 (quantized)...")
    int8_path = exporter.export_tflite_int8()
    print(f"[OK] Exported: {int8_path}")
    
    # Benchmark
    print("")
    print("[6/6] Benchmarking exported models...")
    test_batch = np.random.randn(10, 60, 1280).astype(np.float32)
    
    results = {}
    for model_path in [fp32_path, fp16_path, int8_path]:
        model_name = os.path.basename(model_path)
        print(f"  Benchmarking {model_name}...", end="", flush=True)
        result = exporter.benchmark_tflite(model_path, test_batch)
        results[model_name] = result
        print(" [OK]")
    
    # Print results
    print("")
    print("=" * 60)
    print("EXPORT SUMMARY")
    print("=" * 60)
    
    # File sizes
    print("")
    print("Model Sizes:")
    for name, result in results.items():
        size_mb = exporter.get_model_size_mb(f"models/tflite/{name}")
        print(f"  * {name}: {size_mb:.2f} MB")
    
    # Performance
    print("")
    print("Inference Performance:")
    for name, result in results.items():
        print(f"  * {name}:")
        print(f"      Mean latency: {result['mean_latency_ms']:.2f} ms")
        print(f"      Throughput: {result['throughput_samples_sec']:.0f} samples/sec")
    
    # Compression ratios
    print("")
    print("Compression Analysis:")
    original_size = 18.77  # MB
    for name in results.keys():
        size_mb = exporter.get_model_size_mb(f"models/tflite/{name}")
        compression = (1 - size_mb / original_size) * 100
        print(f"  * {name}: {compression:.1f}% reduction from original")
    
    print("")
    print("=" * 60)
    print("[OK] STAGE 13 COMPLETE - All models exported successfully!")
    print("=" * 60)
    print("")
    
except Exception as e:
    print(f"")
    print(f"[ERROR] Export failed: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""

    try:
        # Run in subprocess with timeout
        process = subprocess.Popen(
            [sys.executable, "-c", script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd(),
        )

        try:
            stdout, stderr = process.communicate(timeout=timeout_sec)
            print(stdout)
            if stderr:
                print("STDERR:", stderr, file=sys.stderr)
            return process.returncode == 0
        except subprocess.TimeoutExpired:
            process.kill()
            print("\n[TIMEOUT] Export timed out after {} seconds".format(timeout_sec))
            print("   This may be due to TensorFlow initialization issues on Windows.")
            print("   Try running: python direct_export.py")
            return False

    except Exception as e:
        print(f"\n[ERROR] Failed to run export: {e}")
        return False


def verify_exports():
    """Check if .tflite files were successfully created"""
    tflite_dir = "models/tflite"
    files = []

    if os.path.exists(tflite_dir):
        files = [f for f in os.listdir(tflite_dir) if f.endswith(".tflite")]

    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)
    print(f"\nTFLite Directory: {os.path.abspath(tflite_dir)}")
    print(f"Files found: {len(files)}")

    if files:
        print("\nExported models:")
        for f in sorted(files):
            path = os.path.join(tflite_dir, f)
            size_mb = os.path.getsize(path) / (1024 * 1024)
            print(f"  [OK] {f} ({size_mb:.2f} MB)")
        return True
    else:
        print("\n[WARNING] No .tflite files found in models/tflite/")
        print("  The export process may have encountered issues.")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("MediSign Stage 13: TFLite Export")
    print("=" * 60 + "\n")

    setup_environment()

    success = run_export_with_timeout(timeout_sec=120)
    verify_exports()

    if not success:
        print("\n[WARNING] Export process encountered issues.")
        print("   Please check the error messages above.")
        sys.exit(1)
