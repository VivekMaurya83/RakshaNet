import cv2
import numpy as np
from pathlib import Path

def preprocess_image(file_path: Path, target_size=(224, 224)) -> np.ndarray:
    """
    Reads, validates, resizes, converts to RGB, and normalizes a banknote image.
    
    Args:
        file_path: Path to the image file.
        target_size: Dimensions (width, height) to resize the image to.
        
    Returns:
        A normalized float32 numpy array.
    """
    # 1. Read image (OpenCV default is BGR)
    img = cv2.imread(str(file_path))
    
    # 2. Validate image loading
    if img is None:
        raise ValueError("Could not read image. The file may be corrupted or of an unsupported format.")
        
    # 3. Convert from BGR to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # 4. Resize image
    resized = cv2.resize(img_rgb, target_size)
    
    # 5. Normalize image (convert pixels to float32 range [0, 1])
    normalized = resized.astype(np.float32) / 255.0
    
    return normalized
