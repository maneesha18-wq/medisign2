
import os
# Workaround for Avast/AVG SSL permission error
if "SSLKEYLOGFILE" in os.environ:
    del os.environ["SSLKEYLOGFILE"]

import tensorflow as tf
import numpy as np
import time

def test_tflite_model(model_path="models/medisign_model.tflite"):
    print(f"Testing TFLite model: {model_path}")
    
    if not os.path.exists(model_path):
        print("Error: Model file not found.")
        return

    try:
        # Load TFLite model and allocate tensors
        interpreter = tf.lite.Interpreter(model_path=model_path)
        interpreter.allocate_tensors()

        # Get input and output details
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        print("\nInput details:")
        print(f"  Shape: {input_details[0]['shape']}")
        print(f"  Type: {input_details[0]['dtype']}")
        
        print("\nOutput details:")
        print(f"  Shape: {output_details[0]['shape']}")
        
        # Create dummy input
        # Model expects (1, 60, 1280)
        input_shape = input_details[0]['shape']
        dummy_input = np.random.random(input_shape).astype(np.float32)
        
        # Run inference
        print("\nRunning inference...")
        interpreter.set_tensor(input_details[0]['index'], dummy_input)
        
        start_time = time.time()
        interpreter.invoke()
        end_time = time.time()
        
        output_data = interpreter.get_tensor(output_details[0]['index'])
        
        print(f"Inference time: {(end_time - start_time) * 1000:.2f} ms")
        print(f"Output shape: {output_data.shape}")
        print(f"Output sum: {np.sum(output_data):.2f} (Should be close to 1.0 for Softmax)")
        
        print("\nPASS: TFLite model verification successful.")
        
    except Exception as e:
        print(f"\nFAIL: Verification failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tflite_model()
