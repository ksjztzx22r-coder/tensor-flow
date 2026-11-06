import cv2
import numpy as np
try:
    import tflite_runtime.interpreter as tflite # type: ignore
except ImportError:
    import tensorflow as tf
    tflite = tf.lite

from Rasp_Pi.raspi_config import *

# ==========================================================
# TensorFlow Lite Detector
# ==========================================================

class WildlifeDetector:

    def __init__(self):

        from pathlib import Path

        if not Path(MODEL_PATH).exists():

            raise FileNotFoundError(

                f"TFLite model not found: {MODEL_PATH}"

        )

        self.interpreter = tflite.Interpreter(
    model_path=str(MODEL_PATH)
)

        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()

        self.output_details = self.interpreter.get_output_details()

        self.input_height = self.input_details[0]["shape"][1]

        self.input_width = self.input_details[0]["shape"][2]

        self.input_dtype = self.input_details[0]["dtype"]

    # ======================================================

    def preprocess(self, frame):

        image = cv2.resize(

            frame,

            (self.input_width, self.input_height)

        )

        image = cv2.cvtColor(

            image,

            cv2.COLOR_BGR2RGB

        )

        image = image.astype(np.float32)


        image = np.expand_dims(

            image,

            axis=0

        )

        return image

    # ======================================================

    def infer(self, frame):

        image = self.preprocess(frame)

        self.interpreter.set_tensor(

            self.input_details[0]["index"],

            image.astype(self.input_dtype)

        )

        self.interpreter.invoke()

        output = self.interpreter.get_tensor(

            self.output_details[0]["index"]

        )[0]

        class_id = int(

            np.argmax(output)

        )

        confidence = float(

            output[class_id]

        )

        label = LABELS[class_id]

        return {

            "label": label,

            "confidence": confidence,

            "scores": output

        }

    # ======================================================

    def detect(self, frame):

        result = self.infer(frame)

        if result["confidence"] >= CONFIDENCE_THRESHOLD:

            return result

        return {

            "label": "background",

            "confidence": result["confidence"],

            "scores": result["scores"]

        }


# ==========================================================
# Singleton
# ==========================================================

detector = None

def initialize_detector():

    global detector

    if detector is None:

        detector = WildlifeDetector()

# ==========================================================
# Public API
# ==========================================================

def classify(frame):

    initialize_detector()

    return detector.detect(frame)

# ==========================================================
# Standalone Test
# ==========================================================

if __name__ == "__main__":

    import cv2

    cap = cv2.VideoCapture(0)

    while True:

        ret, frame = cap.read()

        if not ret:

            continue

        result = classify(frame)

        text = f"{result['label']} : {result['confidence']:.2f}"

        cv2.putText(

            frame,

            text,

            (20,40),

            cv2.FONT_HERSHEY_SIMPLEX,

            1,

            (0,255,0),

            2

        )

        cv2.imshow(

            "Detector",

            frame

        )

        if cv2.waitKey(1) & 0xFF == ord("q"):

            break

    cap.release()

    cv2.destroyAllWindows()