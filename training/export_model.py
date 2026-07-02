import tensorflow as tf
import tf2onnx
from config import BEST_MODEL_PATH, ONNX_MODEL_PATH

def main():
    print("🔄 Loading Keras model for ONNX export...")
    if not BEST_MODEL_PATH.exists():
        raise FileNotFoundError(f"Keras model file not found at: {BEST_MODEL_PATH}")
        
    model = tf.keras.models.load_model(str(BEST_MODEL_PATH))
    print(f"✓ Loaded best model from: {BEST_MODEL_PATH}")
    
    # 1. Define the input signature
    # Shape matches (Batch, Height, Width, Channels) with standard float32 type
    spec = (tf.TensorSpec((None, 224, 224, 3), tf.float32, name="input_image"),)
    
    # 2. Export using tf2onnx from_keras API
    print("⚡ Converting Keras computational graph to ONNX model format...")
    model_proto, _ = tf2onnx.convert.from_keras(
        model,
        input_signature=spec,
        opset=13,  # Opset 13 provides broad compatibility with onnxruntime
        output_path=str(ONNX_MODEL_PATH)
    )
    print(f"🎉 Export complete! Model saved to: {ONNX_MODEL_PATH}")

if __name__ == "__main__":
    main()
