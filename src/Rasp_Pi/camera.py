"""
Camera module supporting Raspberry Pi Camera V1.3 / V2 via Picamera2,
with automatic fallback to OpenCV VideoCapture for local testing.
Optimized for on-demand still image capture.
"""

import time
import cv2
import numpy as np

from src.Rasp_Pi.raspi_config import CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_BACKEND

# Check Picamera2 availability
PICAMERA2_AVAILABLE = False
try:
    from picamera2 import Picamera2
    PICAMERA2_AVAILABLE = True
except (ImportError, ValueError, Exception) as e:
    print(f"[CAMERA NOTE] Picamera2 not usable ({e}). Will use OpenCV fallback.")
    PICAMERA2_AVAILABLE = False


class CameraInterface:
    def __init__(self):
        self.backend = CAMERA_BACKEND
        self.picam2 = None
        self.cap = None
        self.is_opened = False

    def open(self):
        if self.is_opened:
            return

        if self.backend == "picamera2" and PICAMERA2_AVAILABLE:
            try:
                print("[CAMERA] Initializing Picamera2 with automatic white balance & exposure...")
                self.picam2 = Picamera2()

                config = self.picam2.create_still_configuration(
                    main={"size": (CAMERA_WIDTH, CAMERA_HEIGHT), "format": "RGB888"}
                )
                self.picam2.configure(config)

                # Set standard Auto White Balance (AeEnable & AwbEnable)
                try:
                    self.picam2.set_controls({
                        "AwbEnable": True,
                        "AeEnable": True,
                        "AwbMode": 0  # 0 is Auto AWB
                    })
                except Exception:
                    pass

                self.picam2.start()
                # Crucial: Allow 2 seconds for Auto Exposure & White Balance to converge on natural room lighting
                print("[CAMERA] Waiting 2s for sensor Auto Exposure & White Balance to converge...")
                time.sleep(2.0)
                self.is_opened = True
                print("[CAMERA] Picamera2 ready with natural color tuning.")
                return
            except Exception as e:
                print(f"[CAMERA WARNING] Picamera2 init failed ({e}). Falling back to OpenCV.")
                self.backend = "opencv"

        # Fallback to OpenCV VideoCapture
        print("[CAMERA] Initializing OpenCV VideoCapture...")
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        if not self.cap.isOpened():
            raise RuntimeError("Unable to open camera via Picamera2 or OpenCV.")
        self.is_opened = True
        print("[CAMERA] OpenCV Camera initialized successfully.")

    def capture_still(self):
        """
        Captures a single photograph on demand.
        Returns the image as an RGB uint8 NumPy array (H, W, C).
        """
        if not self.is_opened:
            self.open()

        if self.backend == "picamera2" and self.picam2 is not None:
            # Picamera2 capture_array() returns RGB format directly
            frame = self.picam2.capture_array()
            return frame

        elif self.cap is not None:
            # OpenCV returns BGR, convert to RGB
            ret, frame = self.cap.read()
            if not ret or frame is None:
                return None
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return frame_rgb

        return None

    def release(self):
        """Releases camera hardware resources."""
        if self.picam2 is not None:
            try:
                self.picam2.stop()
                self.picam2.close()
            except Exception:
                pass
            self.picam2 = None

        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None

        self.is_opened = False
        print("[CAMERA] Camera closed and released.")


camera = CameraInterface()

def initialize_camera():
    camera.open()

def capture_still():
    return camera.capture_still()

def close_camera():
    camera.release()


if __name__ == "__main__":
    print("=== Standalone Camera Test ===")
    try:
        initialize_camera()
        print("Capturing test still image...")
        img = capture_still()
        if img is not None:
            print(f"Captured image shape: {img.shape}, dtype: {img.dtype}")
            # Save test image (convert back to BGR for cv2.imwrite)
            test_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            cv2.imwrite("test_still.jpg", test_bgr)
            print("Successfully saved test_still.jpg")
        else:
            print("[ERROR] Failed to capture image.")
    finally:
        close_camera()
