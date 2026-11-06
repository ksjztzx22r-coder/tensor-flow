import tensorflow as tf

from Training.config import *

model = tf.keras.models.load_model(

    MODEL_PATH,

    compile=False

)

converter = tf.lite.TFLiteConverter.from_keras_model(

    model

)

if ENABLE_QUANTIZATION:

    converter.optimizations = [

        tf.lite.Optimize.DEFAULT

    ]

tflite_model = converter.convert()

with open(

    TFLITE_PATH,

    "wb"

) as f:

    f.write(

        tflite_model

    )

print()

print("TensorFlow Lite model saved to")

print(TFLITE_PATH)