import tensorflow as tf
import numpy as np

from Training.dataset import *
from Training.config import *

model = tf.keras.models.load_model(MODEL_PATH)

_, val_ds = load_dataset()

loss, accuracy = model.evaluate(

    val_ds,

    verbose=1

)

print()

print("Loss :", loss)

print("Accuracy :", accuracy)

print("Precision :", precision)

print("Recall :", recall)

print()

predictions = []

ground_truth = []

for images, labels in val_ds:

    pred = model.predict(

        images,

        verbose=0

    )

    pred = np.argmax(

        pred,

        axis=1

    )

    predictions.extend(pred)

    ground_truth.extend(labels.numpy())

predictions = np.array(predictions)

ground_truth = np.array(ground_truth)

correct = np.sum(

    predictions == ground_truth

)

total = len(predictions)

print()

print("Correct :", correct)

print("Incorrect :", total - correct)

print("Total :", total)

print("Accuracy :", correct / total)