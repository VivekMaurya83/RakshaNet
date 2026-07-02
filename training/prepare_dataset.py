import os
import shutil
import random
import cv2
from pathlib import Path
from sklearn.model_selection import train_test_split
from config import RAW_DATA_DIR, PROCESSED_DATA_DIR, IMAGE_SIZE, RANDOM_SEED, VAL_SPLIT, TEST_SPLIT

# Set seeds for deterministic splits
random.seed(RANDOM_SEED)

def get_image_files(directory: Path) -> list:
    """Recursively lists all valid image files in a directory."""
    valid_exts = {".jpg", ".jpeg", ".png", ".webp"}
    image_files = []
    if not directory.exists():
        return []
    for p in directory.rglob("*"):
        if p.is_file() and p.suffix.lower() in valid_exts:
            image_files.append(p)
    return image_files

def process_and_save_image(src_path: Path, dest_path: Path) -> bool:
    """Loads, converts to RGB, resizes, and saves the image to target path."""
    try:
        # 1. Read image
        img = cv2.imread(str(src_path))
        if img is None:
            return False
            
        # 2. Convert to RGB internally (although we save in BGR, we verify conversion safety)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # 3. Resize to model requirements (224x224)
        resized = cv2.resize(img_rgb, IMAGE_SIZE)
        
        # 4. Save to target path
        # cv2.imwrite expects BGR, so we convert back to BGR for saving
        img_bgr = cv2.cvtColor(resized, cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(dest_path), img_bgr)
        return True
    except Exception as e:
        print(f"⚠️ Warning: Failed to process image {src_path.name} due to: {e}")
        return False

def prepare_data():
    print("📂 Discovering raw banknote images...")
    real_dir = RAW_DATA_DIR / "real"
    fake_dir = RAW_DATA_DIR / "counterfiet"
    
    real_files = get_image_files(real_dir)
    fake_files = get_image_files(fake_dir)
    
    print(f"✓ Found {len(real_files)} real banknote images.")
    print(f"✓ Found {len(fake_files)} counterfeit banknote images.")
    
    if len(real_files) == 0 or len(fake_files) == 0:
        raise ValueError("Error: Could not find raw dataset files. Ensure datasets directory matches.")
        
    # Split real files: Train / Val / Test
    real_train_val, real_test = train_test_split(real_files, test_size=TEST_SPLIT, random_state=RANDOM_SEED)
    real_train, real_val = train_test_split(real_train_val, test_size=VAL_SPLIT / (1.0 - TEST_SPLIT), random_state=RANDOM_SEED)
    
    # Split counterfeit files: Train / Val / Test
    fake_train_val, fake_test = train_test_split(fake_files, test_size=TEST_SPLIT, random_state=RANDOM_SEED)
    fake_train, fake_val = train_test_split(fake_train_val, test_size=VAL_SPLIT / (1.0 - TEST_SPLIT), random_state=RANDOM_SEED)
    
    splits = {
        "train": (real_train, fake_train),
        "validate": (real_val, fake_val),
        "test": (real_test, fake_test)
    }
    
    # Reset processed directories to avoid stale records
    print("🧹 Cleaning processed datasets folders...")
    if PROCESSED_DATA_DIR.exists():
        shutil.rmtree(PROCESSED_DATA_DIR)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save splits
    for split_name, (reals, fakes) in splits.items():
        print(f"🚀 Splitting '{split_name}' set: {len(reals)} real | {len(fakes)} counterfeit...")
        
        real_dest = PROCESSED_DATA_DIR / split_name / "real"
        fake_dest = PROCESSED_DATA_DIR / split_name / "counterfeit"
        
        real_dest.mkdir(parents=True, exist_ok=True)
        fake_dest.mkdir(parents=True, exist_ok=True)
        
        # Save reals
        for idx, file_path in enumerate(reals):
            process_and_save_image(file_path, real_dest / f"real_{idx}{file_path.suffix}")
            
        # Save counterfeits
        for idx, file_path in enumerate(fakes):
            process_and_save_image(file_path, fake_dest / f"fake_{idx}{file_path.suffix}")
            
    print("✓ Dataset splits completed successfully!")

if __name__ == "__main__":
    prepare_data()
