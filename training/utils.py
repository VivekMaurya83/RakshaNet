import cv2
import numpy as np
from pathlib import Path

def preprocess_single_image(image_path: Path, target_size=(224, 224)) -> np.ndarray:
    """
    Loads, resizes, and normalizes a single image for model inference.
    
    Args:
        image_path: Path to the image file.
        target_size: Dimensions (width, height) to resize to.
        
    Returns:
        A normalized float32 numpy array.
    """
    # 1. Read image
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Could not load image file: {image_path}")
        
    # 2. Convert BGR to RGB (which the model expects)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # 3. Resize image
    resized = cv2.resize(img_rgb, target_size)
    
    # 4. Normalize pixel values to [0, 1]
    normalized = resized.astype(np.float32) / 255.0
    
    return normalized
