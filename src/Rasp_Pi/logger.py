import csv
from datetime import datetime
from pathlib import Path

import cv2

from Rasp_Pi.raspi_config import *

# ==========================================================
# Create Directories
# ==========================================================

LOG_DIR.mkdir(

    parents=True,

    exist_ok=True

)

DETECTION_IMAGE_DIR.mkdir(

    parents=True,

    exist_ok=True

)

# ==========================================================
# Create CSV
# ==========================================================

if not LOG_FILE.exists():

    with open(

        LOG_FILE,

        "w",

        newline=""

    ) as file:

        writer = csv.writer(file)

        writer.writerow(

            [

                "Timestamp",

                "Species",

                "Confidence",

                "Image"

            ]

        )

# ==========================================================
# Logger Class
# ==========================================================

class DetectionLogger:

    def __init__(self):

        self.log_file = LOG_FILE

    def save_image(

        self,

        frame,

        label

    ):

        timestamp = datetime.now().strftime(

            "%Y%m%d_%H%M%S"

        )

        filename = f"{label}_{timestamp}.jpg"

        filepath = DETECTION_IMAGE_DIR / filename

        cv2.imwrite(

            str(filepath),

            frame

        )

        return filepath

    def log(

        self,

        label,

        confidence,

        frame=None

    ):

        timestamp = datetime.now().strftime(

            "%Y-%m-%d %H:%M:%S"

        )

        image_name = ""

        if SAVE_DETECTED_IMAGES and frame is not None:

            image_name = self.save_image(

                frame,

                label

            ).name

        with open(

            self.log_file,

            "a",

            newline=""

        ) as file:

            writer = csv.writer(file)

            writer.writerow(

                [

                    timestamp,

                    label,

                    f"{confidence:.4f}",

                    image_name

                ]

            )

        print(

            f"[{timestamp}] "

            f"{label} "

            f"{confidence:.2f}"

        )

# ==========================================================
# Singleton
# ==========================================================

logger = DetectionLogger()

# ==========================================================
# Public API
# ==========================================================

def log_detection(

    label,

    confidence,

    frame=None

):

    logger.log(

        label,

        confidence,

        frame

    )

# ==========================================================
# Standalone Test
# ==========================================================

if __name__ == "__main__":

    import numpy as np

    dummy = np.zeros(

        (

            CAMERA_HEIGHT,

            CAMERA_WIDTH,

            3

        ),

        dtype=np.uint8

    )

    log_detection(

        "elephant",

        0.97,

        dummy

    )

    log_detection(

        "wildboar",

        0.92,

        dummy

    )

    log_detection(

        "monkey",

        0.95,

        dummy

    )

    print("Logger test complete.")