import cv2
import sys
from pathlib import Path

def find_template_image() -> Path:
    # Look for the first genuine banknote image in the dataset to act as our domain reference
    base_dir = Path(__file__).resolve().parent.parent
    real_dir = base_dir / "datasets" / "raw" / "currency500_real_fake" / "real"
    for p in real_dir.rglob("*"):
        if p.is_file() and p.suffix.lower() in [".jpg", ".jpeg", ".png"]:
            return p
    return None

def test_orb_validator(test_image_path_str: str):
    template_path = find_template_image()
    if not template_path:
        print("Error: Reference banknote template image not found in dataset.")
        sys.exit(1)
        
    print(f"📖 Loading reference template banknote: {template_path.name}")
    
    # 1. Read images in grayscale
    img_template = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
    img_test = cv2.imread(test_image_path_str, cv2.IMREAD_GRAYSCALE)
    
    if img_test is None:
        print(f"Error: Could not read test image at {test_image_path_str}")
        sys.exit(1)
        
    # 2. Initialize ORB feature detector
    orb = cv2.ORB_create(nfeatures=1000)
    
    # 3. Detect keypoints and compute descriptors
    kp_temp, des_temp = orb.detectAndCompute(img_template, None)
    kp_test, des_test = orb.detectAndCompute(img_test, None)
    
    if des_test is None or des_temp is None:
        print("❌ Reject: No visual features detected in the image.")
        return False
        
    # 4. Use Brute-Force Matcher with Hamming distance
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des_temp, des_test)
    
    # Filter matches based on quality (distance)
    good_matches = [m for m in matches if m.distance < 45]
    match_count = len(good_matches)
    
    print(f"🔍 Total good keypoint matches found: {match_count}")
    
    # Define validation threshold (12 matches is standard for positive domain match)
    threshold = 12
    if match_count >= threshold:
        print("✅ Accept: Image contains an Indian currency note/banknote.")
        return True
    else:
        print("❌ Reject: Image does not appear to contain a valid banknote.")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_orb.py <path_to_test_image>")
        sys.exit(1)
        
    test_orb_validator(sys.argv[1])
