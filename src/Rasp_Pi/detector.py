"""
TensorFlow Lite inference engine for wildlife intrusion detection.
Accepts RGB image arrays, matches training MobileNetV3 input shape and float32 scaling.
"""

from pathlib import Path
import cv2
import numpy as np

try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    import tensorflow as tf
    tflite = tf.lite

from src.Rasp_Pi.raspi_config import MODEL_PATH, LABELS, CONFIDENCE_THRESHOLD


class WildlifeDetector:
    def __init__(self):
        if not Path(MODEL_PATH).exists():
            raise FileNotFoundError(f"TFLite model not found: {MODEL_PATH}")

        self.interpreter = tflite.Interpreter(model_path=str(MODEL_PATH))
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        self.input_height = self.input_details[0]["shape"][1]
        self.input_width = self.input_details[0]["shape"][2]
        self.input_dtype = self.input_details[0]["dtype"]

        print(f"[DETECTOR] Loaded model: {MODEL_PATH}")
        print(f"[DETECTOR] Expected input: {self.input_width}x{self.input_height}, dtype: {self.input_dtype}")

    def preprocess(self, image_rgb):
        """
        Takes RGB image array (H, W, 3), resizes to model input shape,
        and casts to float32 in range [0, 255].
        Note: tf.keras.applications.mobilenet_v3.preprocess_input is built
        into the model graph, so feeding [0, 255] float32 is strictly correct.
        """
        image_resized = cv2.resize(
            image_rgb,
            (self.input_width, self.input_height),
            interpolation=cv2.INTER_AREA
        )
        image_float = image_resized.astype(np.float32)
        image_batch = np.expand_dims(image_float, axis=0)
        return image_batch

    def infer(self, image_rgb):
        input_data = self.preprocess(image_rgb)

        self.interpreter.set_tensor(
            self.input_details[0]["index"],
            input_data.astype(self.input_dtype)
        )
        self.interpreter.invoke()

        output = self.interpreter.get_tensor(
            self.output_details[0]["index"]
        )[0]

        class_id = int(np.argmax(output))
        confidence = float(output[class_id])
        label = LABELS.get(class_id, "unknown")

        return {
            "class_id": class_id,
            "label": label,
            "confidence": confidence,
            "scores": output
        }

    def detect(self, image_rgb):
        result = self.infer(image_rgb)
        
        # Check against validated confidence threshold
        if result["confidence"] < CONFIDENCE_THRESHOLD:
            return {
                "class_id": result["class_id"],
                "label": "uncertain",
                "raw_label": result["label"],
                "confidence": result["confidence"],
                "scores": result["scores"]
            }

        return result


detector = None

def initialize_detector():
    global detector
    if detector is None:
        detector = WildlifeDetector()

def classify(image_rgb):
    initialize_detector()
    return detector.detect(image_rgb)


if __name__ == "__main__":
    print("=== Standalone Detector Test ===")
    initialize_detector()
    dummy_rgb = np.zeros((480, 640, 3), dtype=np.uint8)
    res = classify(dummy_rgb)
    print(f"Result on blank frame: {res}")
