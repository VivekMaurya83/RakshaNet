import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATASETS_DIR = BASE_DIR / "datasets"
RAW_DATA_DIR = DATASETS_DIR / "raw" / "currency500_real_fake"
PROCESSED_DATA_DIR = DATASETS_DIR / "processed"

# Processed Splits Directories
TRAIN_DIR = PROCESSED_DATA_DIR / "train"
VAL_DIR = PROCESSED_DATA_DIR / "validate"
TEST_DIR = PROCESSED_DATA_DIR / "test"

# Output Model Directories
MODEL_SAVE_DIR = BASE_DIR / "models" / "counterfeit"
BEST_MODEL_PATH = MODEL_SAVE_DIR / "best_model.keras"
ONNX_MODEL_PATH = MODEL_SAVE_DIR / "model.onnx"
LABELS_PATH = MODEL_SAVE_DIR / "labels.json"
METRICS_PATH = MODEL_SAVE_DIR / "metrics.json"

# ML Configurations
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 10
LEARNING_RATE = 1e-4

# Split ratios
VAL_SPLIT = 0.15
TEST_SPLIT = 0.15
RANDOM_SEED = 42
