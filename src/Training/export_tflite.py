import tensorflow as tf
from pathlib import Path
from Training.config import *

# ==========================================================
# Load Keras Model
# ==========================================================

print("=" * 60)
print("Loading trained model...")
print(MODEL_PATH)

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Model not found:\n{MODEL_PATH}")

model = tf.keras.models.load_model(MODEL_PATH)

print("Model loaded successfully.")

# ==========================================================
# Convert to TensorFlow Lite
# ==========================================================

print()
print("=" * 60)
print("Converting to TensorFlow Lite...")

converter = tf.lite.TFLiteConverter.from_keras_model(model)

converter.optimizations = [tf.lite.Optimize.DEFAULT]

tflite_model = converter.convert()

# ==========================================================
# Save
# ==========================================================

TFLITE_PATH.parent.mkdir(parents=True, exist_ok=True)

with open(TFLITE_PATH, "wb") as f:
    f.write(tflite_model)

print("TensorFlow Lite model saved.")

# ==========================================================
# Verify
# ==========================================================

print()
print("=" * 60)
print("Verifying TensorFlow Lite model...")

interpreter = tf.lite.Interpreter(model_path=str(TFLITE_PATH))
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print()
print("Input Tensor")
print(input_details)

print()
print("Output Tensor")
print(output_details)

print()
print("=" * 60)
print("TensorFlow Lite conversion successful.")
print("Saved to:")
print(TFLITE_PATH)
print("=" * 60)