"""
Main State Machine for Wildlife Intrusion Detection & Deterrence.
Architecture: Option A (PIR Trigger -> Still Capture -> TFLite -> Deterrence -> Cooldown).
Runs 100% offline on Raspberry Pi 3B+.
"""

import time
import sys

from src.Rasp_Pi.raspi_config import (
    PIR_COOLDOWN_SECONDS,
    CONFIDENCE_THRESHOLD,
)
from src.Rasp_Pi.gpio_setup import initialize as initialize_gpio, cleanup as cleanup_gpio
from src.Rasp_Pi.pir_sensor import (
    initialize_pir,
    wait_for_pir_motion,
    wait_for_pir_clear,
    cleanup_pir,
)
from src.Rasp_Pi.camera import initialize_camera, capture_still, close_camera
from src.Rasp_Pi.detector import initialize_detector, classify
from src.Rasp_Pi.audio import play_audio, stop_audio, audio_busy
from src.Rasp_Pi.logger import log_detection


def run_system():
    print("=" * 65)
    print("  WILDLIFE INTRUSION DETECTION & ACOUSTIC DETERRENCE SYSTEM")
    print("  Mode: PIR-Triggered On-Demand Still Capture (Option A)")
    print("  Target Classes: Elephant, Wild Boar, Monkey, Background")
    print("=" * 65)

    # 1. Initialize Subsystems (Loaded once at startup)
    print("[INIT] Initializing GPIO...")
    initialize_gpio()

    print("[INIT] Loading TensorFlow Lite interpreter...")
    initialize_detector()

    print("[INIT] Initializing camera...")
    initialize_camera()

    print("[INIT] Initializing PIR motion sensor...")
    initialize_pir()

    print("=" * 65)
    print("[SYSTEM READY] Standing by for PIR motion triggers...")
    print("Press Ctrl+C to stop system safely.")
    print("=" * 65)

    try:
        while True:
            # 2. Wait for PIR LOW -> HIGH motion event
            trigger_time = wait_for_pir_motion()
            print(f"\n[MOTION] Trigger detected at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(trigger_time))}")

            # Optional brief settling delay (100ms) for camera sensor auto-exposure
            time.sleep(0.1)

            # 3. Capture one still photograph
            t_cap_start = time.time()
            frame_rgb = capture_still()
            if frame_rgb is None:
                print("[ERROR] Failed to capture photograph from camera. Continuing standby.")
                continue

            # 4. Run local TFLite classification
            t_infer_start = time.time()
            result = classify(frame_rgb)
            inference_ms = (time.time() - t_infer_start) * 1000.0

            label = result["label"]
            confidence = result["confidence"]
            action = "none"

            print(f"[PREDICTION] {label.upper()} | Confidence: {confidence*100:.2f}% | Latency: {inference_ms:.1f}ms")

            # 5. Acoustic Deterrence Decision
            if label in ["elephant", "wildboar", "monkey"] and confidence >= CONFIDENCE_THRESHOLD:
                action = f"deterrent_played_{label}"
                if not audio_busy():
                    play_audio(label)
                else:
                    print("[AUDIO] Audio channel busy; skipping overlapping trigger.")
            elif label == "background":
                action = "ignored_background"
                print("[DECISION] Non-target background image; no audio deterrent.")
            else:
                action = "uncertain_low_confidence"
                print(f"[DECISION] Confidence below threshold ({CONFIDENCE_THRESHOLD*100:.0f}%); no audio deterrent.")

            # 6. Log Event & Save Image
            log_detection(
                label=label,
                confidence=confidence,
                action=action,
                inference_time_ms=inference_ms,
                frame_rgb=frame_rgb,
            )

            # 7. Apply strict 5-second cooldown and return to idle
            print(f"[COOLDOWN] Applying {PIR_COOLDOWN_SECONDS}s cooldown...")
            time.sleep(PIR_COOLDOWN_SECONDS)

            print("[STANDBY] Re-armed. Waiting for next motion event...")

    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Keyboard interrupt received. Exiting safely...")

    finally:
        # Graceful hardware teardown
        stop_audio()
        close_camera()
        cleanup_pir()
        cleanup_gpio()
        print("[SHUTDOWN] All resources released cleanly. Goodbye.")


if __name__ == "__main__":
    run_system()
