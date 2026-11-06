from pathlib import Path

# ============================================================
# Project Directories
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_DIR = PROJECT_ROOT / "dataset"

MODEL_DIR = PROJECT_ROOT / "models"

LOG_DIR = PROJECT_ROOT / "logs"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# Model Output
# ============================================================

MODEL_PATH = MODEL_DIR / "wildlife.keras"

TFLITE_PATH = MODEL_DIR / "wildlife.tflite"

# ============================================================
# Dataset
# ============================================================

IMG_HEIGHT = 96
IMG_WIDTH = 96
CHANNELS = 3

IMAGE_SIZE = (IMG_HEIGHT, IMG_WIDTH)

NUM_CLASSES = 4

CLASS_NAMES = [

    "elephant",

    "wildboar",

    "monkey",

    "background"

]

# ============================================================
# Training
# ============================================================

BATCH_SIZE = 32

EPOCHS = 40

VALIDATION_SPLIT = 0.20

SEED = 42

LEARNING_RATE = 1e-4

FINE_TUNE_LR = 1e-5

FINE_TUNE_EPOCHS = 15

# ============================================================
# Callbacks
# ============================================================

CHECKPOINT_NAME = "best_model.keras"

CHECKPOINT_PATH = MODEL_DIR / CHECKPOINT_NAME

EARLY_STOPPING_PATIENCE = 6

LR_PATIENCE = 3

LR_FACTOR = 0.25

# ============================================================
# TensorBoard
# ============================================================

TENSORBOARD_DIR = LOG_DIR / "tensorboard"

# ============================================================
# TensorFlow Lite
# ============================================================

ENABLE_QUANTIZATION = True

# ============================================================
# Detection Labels
# ============================================================

LABELS = {

    0: "elephant",

    1: "wildboar",

    2: "monkey",

    3: "background"

}