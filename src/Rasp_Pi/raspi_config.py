from pathlib import Path

# ==========================================================
# Project Directories
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_DIR = PROJECT_ROOT / "models"

SOUND_DIR = PROJECT_ROOT / "sounds"

LOG_DIR = PROJECT_ROOT / "logs"

# ==========================================================
# TensorFlow Lite Model
# ==========================================================

MODEL_PATH = MODEL_DIR / "wildlife.tflite"

# ==========================================================
# Camera
# ==========================================================

CAMERA_WIDTH = 640

CAMERA_HEIGHT = 480

CAMERA_FPS = 30

# ==========================================================
# Detection
# ==========================================================

IMAGE_SIZE = (96,96)

NUM_CLASSES = 4

CONFIDENCE_THRESHOLD = 0.20

LABELS = {

    0: "elephant",

    1: "wildboar",

    2: "monkey",

    3: "background"

}


# ==========================================================
# Audio
# ==========================================================

ELEPHANT_AUDIO = SOUND_DIR / "elephant.wav"

BOAR_AUDIO = SOUND_DIR / "boar&monkey.wav"

MONKEY_AUDIO = SOUND_DIR / "boar&monkey.wav"

# ==========================================================
# Logging
# ==========================================================

LOG_FILE = LOG_DIR / "detections.csv"

SAVE_DETECTED_IMAGES = True

DETECTION_IMAGE_DIR = LOG_DIR / "detections"

DETECTION_IMAGE_DIR.mkdir(

    parents=True,

    exist_ok=True

)