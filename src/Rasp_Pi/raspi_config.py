from pathlib import Path

# ==========================================================
# Project Directories
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_DIR = PROJECT_ROOT / "models"
SOUND_DIR = PROJECT_ROOT / "sounds"
LOG_DIR = PROJECT_ROOT / "logs"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
SOUND_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================================
# TensorFlow Lite Model
# ==========================================================

MODEL_PATH = MODEL_DIR / "wildlife.tflite"

# ==========================================================
# Camera Settings (Picamera2 / OpenCV fallback)
# ==========================================================

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_BACKEND = "picamera2"  # "picamera2" for Pi Camera V1.3/V2 on Pi OS Bookworm; "opencv" for USB webcam / fallback

# ==========================================================
# Detection & Classification
# ==========================================================

IMAGE_SIZE = (96, 96)
NUM_CLASSES = 4
CONFIDENCE_THRESHOLD = 0.70

# Label order alphabetically assigned by image_dataset_from_directory:
LABELS = {
    0: "background",
    1: "elephant",
    2: "monkey",
    3: "wildboar"
}

# ==========================================================
# PIR Sensor (HC-SR501) with Hysteresis
# ==========================================================

PIR_PIN = 17                        # BCM GPIO17 (Physical Pin 11)
PIR_WARMUP_SECONDS = 15             # Stabilisation duration after power up
PIR_QUIET_SECONDS = 3.0             # Continuous silence required to return to IDLE
PIR_CONTINUOUS_MAX_SECONDS = 5.0    # Seconds of continuous detection before entering ignore mode
PIR_IGNORE_INTERVAL_SECONDS = 15.0  # Seconds to ignore/suppress PIR after continuous detection
PIR_COOLDOWN_SECONDS = 5.0          # Fallback general cooldown

# ==========================================================
# Audio Deterrence
# ==========================================================

ELEPHANT_AUDIO = SOUND_DIR / "elephant.wav"
BOAR_AUDIO = SOUND_DIR / "boar&monkey.wav"
MONKEY_AUDIO = SOUND_DIR / "boar&monkey.wav"

AUDIO_PLAYBACK_MAX_SECONDS = 10  # Prevent audio playing indefinitely to conserve power

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
