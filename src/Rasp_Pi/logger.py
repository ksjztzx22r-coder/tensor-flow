"""
Local detection logger saving timestamped event records (CSV)
and snapshot photographs.
"""

import csv
from datetime import datetime
from pathlib import Path
import cv2

from src.Rasp_Pi.raspi_config import (
    LOG_DIR,
    LOG_FILE,
    DETECTION_IMAGE_DIR,
    SAVE_DETECTED_IMAGES,
)

LOG_DIR.mkdir(parents=True, exist_ok=True)
DETECTION_IMAGE_DIR.mkdir(parents=True, exist_ok=True)

# Initialize CSV headers if new
if not LOG_FILE.exists():
    with open(LOG_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Timestamp",
            "Species",
            "Confidence",
            "Action_Taken",
            "Inference_Time_ms",
            "Image_File"
        ])


class DetectionLogger:
    def __init__(self):
        self.log_file = LOG_FILE

    def save_image(self, frame_rgb, label):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{label}_{timestamp}.jpg"
        filepath = DETECTION_IMAGE_DIR / filename
        # Convert RGB back to BGR for cv2.imwrite
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(filepath), frame_bgr)
        # Always maintain a fixed copy at logs/latest.jpg for instant verification without browsing folders
        latest_filepath = LOG_DIR / "latest.jpg"
        cv2.imwrite(str(latest_filepath), frame_bgr)
        return filepath

    def log(self, label, confidence, action="none", inference_time_ms=0.0, frame_rgb=None):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        image_name = ""

        if SAVE_DETECTED_IMAGES and frame_rgb is not None:
            try:
                image_name = self.save_image(frame_rgb, label).name
            except Exception as e:
                print(f"[LOGGER ERROR] Failed to save image: {e}")

        with open(self.log_file, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                timestamp,
                label,
                f"{confidence:.4f}",
                action,
                f"{inference_time_ms:.1f}",
                image_name
            ])

        # Write latest detection metadata for quick CLI and web dashboard access
        try:
            import json
            latest_json = LOG_DIR / "latest.json"
            with open(latest_json, "w") as jf:
                json.dump({
                    "timestamp": timestamp,
                    "species": label,
                    "confidence": f"{confidence*100:.1f}%",
                    "action": action,
                    "inference_ms": f"{inference_time_ms:.1f}ms",
                    "image": image_name
                }, jf, indent=2)
        except Exception:
            pass

        print(f"[{timestamp}] Logged: {label} ({confidence*100:.1f}%) | Action: {action} | Time: {inference_time_ms:.1f}ms")
        print(f"       -> Latest image saved to: {LOG_DIR / 'latest.jpg'}")


logger = DetectionLogger()

def log_detection(label, confidence, action="none", inference_time_ms=0.0, frame_rgb=None):
    logger.log(label, confidence, action, inference_time_ms, frame_rgb)


if __name__ == "__main__":
    print("=== Standalone Logger Test ===")
    import numpy as np
    dummy = np.zeros((480, 640, 3), dtype=np.uint8)
    log_detection("elephant", 0.95, action="deterrence_played", inference_time_ms=45.2, frame_rgb=dummy)
    print("Logger test complete.")
