import sys
import json
import numpy as np
import onnxruntime as ort
from pathlib import Path
from utils import preprocess_single_image
from config import ONNX_MODEL_PATH, LABELS_PATH

def predict_image(image_path_str: str) -> dict:
    """
    Loads, preprocesses, and classifies an image using the exported ONNX model.
    
    Args:
        image_path_str: Relative or absolute path to the banknote image file.
        
    Returns:
        A dictionary with prediction label and confidence score.
    """
    image_path = Path(image_path_str)
    if not image_path.exists():
        raise FileNotFoundError(f"Banknote image file not found at: {image_path_str}")
        
    if not ONNX_MODEL_PATH.exists():
        raise FileNotFoundError(f"Exported ONNX model file not found at: {ONNX_MODEL_PATH}. Export the model first.")
        
    if not LABELS_PATH.exists():
        raise FileNotFoundError(f"Class labels registry file not found at: {LABELS_PATH}")
        
    # 1. Load class labels dict (0 -> Counterfeit / 1 -> Genuine)
    with open(LABELS_PATH, "r") as f:
        labels_map = json.load(f)
        
    # 2. Preprocess image (load, resize, convert RGB, normalize to [0, 1])
    preprocessed_img = preprocess_single_image(image_path)
    
    # 3. Add batch dimension: (1, 224, 224, 3)
    input_tensor = np.expand_dims(preprocessed_img, axis=0).astype(np.float32)
    
    # 4. Initialize ONNX runtime session and run inference
    session = ort.InferenceSession(str(ONNX_MODEL_PATH))
    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: input_tensor})
    
    # 5. Extract probabilities from soft-max logits output
    probabilities = outputs[0][0]
    predicted_idx = int(np.argmax(probabilities))
    confidence_pct = float(probabilities[predicted_idx] * 100)
    
    prediction_label = labels_map[str(predicted_idx)]
    
    result = {
        "prediction": prediction_label,
        "confidence": round(confidence_pct, 1)
    }
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python predict.py <path_to_image>")
        sys.exit(1)
        
    try:
        res = predict_image(sys.argv[1])
        print(json.dumps(res, indent=4))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=4))
        sys.exit(1)
