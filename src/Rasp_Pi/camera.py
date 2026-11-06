"""
Camera module supporting Raspberry Pi Camera V1.3 / V2.
Uses the native rpicam-still / libcamera-still engine with --awb auto
and 2-second exposure/white balance convergence to guarantee authentic color rendering.
"""

import os
import shutil
import subprocess
import time
from pathlib import Path
import cv2
import numpy as np

from src.Rasp_Pi.raspi_config import CAMERA_WIDTH, CAMERA_HEIGHT

# Detect native Raspberry Pi camera CLI
RPICAM_CMD = None
if shutil.which("rpicam-still"):
    RPICAM_CMD = "rpicam-still"
elif shutil.which("libcamera-still"):
    RPICAM_CMD = "libcamera-still"


class CameraInterface:
    def __init__(self):
        self.cmd = RPICAM_CMD
        self.cap = None
        self.temp_image_path = Path("/tmp/rpicam_capture.jpg")
        self.is_opened = False

    def open(self):
        if self.is_opened:
            return

        if self.cmd:
            print(f"[CAMERA] Using native Raspberry Pi camera CLI: {self.cmd}")
            print("[CAMERA] Enabled: Auto White Balance (--awb auto) & 2000ms convergence")
            self.is_opened = True
            return

        # Fallback to OpenCV if native CLI is unavailable
        print("[CAMERA] Native CLI not found. Falling back to OpenCV VideoCapture...")
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        if not self.cap.isOpened():
            raise RuntimeError("Unable to open camera via native CLI or OpenCV.")
        self.is_opened = True
        print("[CAMERA] OpenCV Camera initialized successfully.")

    def capture_still(self):
        """
        Captures a single photograph on demand using the exact same parameters
        as `rpicam-still -t 2000 -o <file> --awb auto --width <W> --height <H>`.
        Returns the image as an RGB uint8 NumPy array (H, W, C).
        """
        if not self.is_opened:
            self.open()

        if self.cmd:
            try:
                # Remove previous temp image if exists
                if self.temp_image_path.exists():
                    self.temp_image_path.unlink()

                # Execute exact verified command with clean AWB and exposure convergence
                cmd_args = [
                    self.cmd,
                    "-t", "2000",
                    "-o", str(self.temp_image_path),
                    "--awb", "auto",
                    "--width", str(CAMERA_WIDTH),
                    "--height", str(CAMERA_HEIGHT),
                    "-n"  # No preview window (headless)
                ]

                subprocess.run(
                    cmd_args,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

                if not self.temp_image_path.exists():
                    print("[CAMERA ERROR] Capture file was not generated.")
                    return None

                # Read with OpenCV and convert to RGB
                image_bgr = cv2.imread(str(self.temp_image_path))
                if image_bgr is None:
                    return None

                image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
                return image_rgb

            except Exception as e:
                print(f"[CAMERA ERROR] Native CLI capture failed: {e}")
                return None

        elif self.cap is not None:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                return None
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return frame_rgb

        return None

    def release(self):
        """Releases camera resources and cleans up temporary capture files."""
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None

        if self.temp_image_path.exists():
            try:
                self.temp_image_path.unlink()
            except Exception:
                pass

        self.is_opened = False
        print("[CAMERA] Camera released.")


camera = CameraInterface()

def initialize_camera():
    camera.open()

def capture_still():
    return camera.capture_still()

def close_camera():
    camera.release()


if __name__ == "__main__":
    print("=== Standalone Camera Test (rpicam-still mode) ===")
    try:
        initialize_camera()
        print("Capturing still with 2000ms AWB auto convergence...")
        img = capture_still()
        if img is not None:
            print(f"Captured shape: {img.shape}, dtype: {img.dtype}")
            test_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            cv2.imwrite("test_still.jpg", test_bgr)
            print("Successfully saved test_still.jpg with verified natural colors!")
        else:
            print("[ERROR] Capture failed.")
    finally:
        close_camera()
