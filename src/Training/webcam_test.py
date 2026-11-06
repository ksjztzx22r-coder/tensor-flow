
import cv2
import tensorflow as tf
import numpy as np
from pathlib import Path

print("Loading Wildlife Recognition Model...", flush=True)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "wildlife.keras"

IMAGE_SIZE = (96, 96)
CLASS_NAMES = ["background", "elephant", "monkey", "wildboar"]
CONFIDENCE_THRESHOLD = 0.60

model = tf.keras.models.load_model(MODEL_PATH)
print("Model loaded successfully!", flush=True)

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ERROR: Could not access webcam.")
    raise SystemExit

print("Webcam connected! Press Q to exit.", flush=True)

try:
    while True:
        ret, frame = camera.read()

        if not ret:
            print("Could not read camera frame.")
            break

        image = cv2.resize(frame, IMAGE_SIZE)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # Note: MobileNetV3 preprocess_input is baked into the model architecture expecting [0, 255] float32.
        # Do not divide by 255.0 here to avoid double normalization.
        image = image.astype(np.float32)
        image = np.expand_dims(image, axis=0)

        predictions = model.predict(image, verbose=0)[0]

        predicted_index = np.argmax(predictions)
        confidence = float(predictions[predicted_index])
        predicted_class = CLASS_NAMES[predicted_index]

        display_text = f"{predicted_class}: {confidence * 100:.2f}%"

        print(
            " | ".join(
            f"{CLASS_NAMES[i]}: {predictions[i] * 100:.2f}%"
            for i in range(len(CLASS_NAMES))
            ),
        flush=True
        )

        cv2.putText(
            frame, display_text, (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8,
            (0, 255, 0), 2
        )

        cv2.imshow("Wildlife Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    camera.release()
    cv2.destroyAllWindows()
    print("Webcam recognition stopped.")
