import time
import cv2

from camera import get_frame, close_camera
from detector import classify
from audio import play_audio, audio_busy
from logger import log_detection
from Rasp_Pi.raspi_config import *

# ==========================================================
# Detection Control
# ==========================================================

LAST_LABEL = "background"

LAST_TRIGGER = 0

TRIGGER_COOLDOWN = 8

# ==========================================================
# Main Loop
# ==========================================================

def main():

    global LAST_LABEL
    global LAST_TRIGGER

    print("=" * 60)
    print("Wildlife Detection System Started")
    print("Press 'Q' to Exit")
    print("=" * 60)

    while True:

        frame = get_frame()

        if frame is None:
            continue

        result = classify(frame)

        label = result["label"]

        confidence = result["confidence"]

        current_time = time.time()

        if (

            label != "background"

            and confidence >= CONFIDENCE_THRESHOLD

        ):

            if (

                label != LAST_LABEL

                or current_time - LAST_TRIGGER > TRIGGER_COOLDOWN

            ):

                if not audio_busy():
                    play_audio(label)

                log_detection(

                    label,

                    confidence,

                    frame

                )

                LAST_LABEL = label

                LAST_TRIGGER = current_time

        text = f"{label} : {confidence:.2f}"

        color = (0, 255, 0)

        if label == "background":

            color = (0, 255, 255)

        cv2.putText(

            frame,

            text,

            (15, 35),

            cv2.FONT_HERSHEY_SIMPLEX,

            1,

            color,

            2

        )

        cv2.imshow(

            "Wildlife Detector",

            frame

        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):

            break

    close_camera()

    cv2.destroyAllWindows()

    print("System Stopped.")

# ==========================================================
# Entry Point
# ==========================================================

if __name__ == "__main__":

    main()