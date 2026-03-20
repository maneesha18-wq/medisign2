
import os
import sys
# Workaround for Avast/AVG SSL permission error
if "SSLKEYLOGFILE" in os.environ:
    del os.environ["SSLKEYLOGFILE"]

import tensorflow as tf
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from modules.sequence_model import AttentionLayer

def export_model(model_path="models/sequence_model_final.keras", output_path="models/medisign_model.tflite"):
    print(f"Loading model from {model_path}...")
    
    if not os.path.exists(model_path):
        print(f"Error: Model file {model_path} not found.")
        return

    try:
        # Load Keras model with custom objects
        model = tf.keras.models.load_model(model_path, custom_objects={"AttentionLayer": AttentionLayer})
        
        # Convert to TFLite
        print("Converting to TFLite...")
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        
        # Enable optimizations
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.target_spec.supported_types = [tf.float16]
        # Enable Select TF ops for LSTM support
        converter.target_spec.supported_ops = [
            tf.lite.OpsSet.TFLITE_BUILTINS,
            tf.lite.OpsSet.SELECT_TF_OPS
        ]
        converter._experimental_lower_tensor_list_ops = False
        
        tflite_model = converter.convert()
        
        # Save
        with open(output_path, "wb") as f:
            f.write(tflite_model)
            
        print(f"TFLite model saved to {output_path}")
        
        # Check sizes
        keras_size = os.path.getsize(model_path) / (1024 * 1024)
        tflite_size = os.path.getsize(output_path) / (1024 * 1024)
        
        print(f"Original Model Size: {keras_size:.2f} MB")
        print(f"TFLite Model Size:   {tflite_size:.2f} MB")
        print(f"Reduction:           {(1 - tflite_size/keras_size)*100:.1f}%")
        
    except Exception as e:
        print(f"Export failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    export_model()
