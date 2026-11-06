import tensorflow as tf

from Training.dataset import load_dataset
from Training.model import build_model
from Training.config import *

# ============================================================
# Load Dataset
# ============================================================

train_ds, val_ds = load_dataset()

# ============================================================
# Build Model
# ============================================================

model = build_model()

model.summary()

# ============================================================
# Callbacks
# ============================================================

checkpoint = tf.keras.callbacks.ModelCheckpoint(

    filepath=CHECKPOINT_PATH,

    monitor="val_accuracy",

    verbose=1,

    save_best_only=True,

    save_weights_only=False

)

early_stop = tf.keras.callbacks.EarlyStopping(

    monitor="val_loss",

    patience=EARLY_STOPPING_PATIENCE,

    restore_best_weights=True,

    verbose=1

)

reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(

    monitor="val_loss",

    factor=LR_FACTOR,

    patience=LR_PATIENCE,

    verbose=1,

    min_lr=1e-6

)

tensorboard = tf.keras.callbacks.TensorBoard(

    log_dir=str(TENSORBOARD_DIR),

    histogram_freq=1,

    write_graph=True,

    write_images=False

)

csv_logger = tf.keras.callbacks.CSVLogger(

    LOG_DIR / "training_log.csv",

    append=True

)

callbacks = [

    checkpoint,

    early_stop,

    reduce_lr,

    tensorboard,

    csv_logger

]

# ============================================================
# Train
# ============================================================

history = model.fit(

    train_ds,

    validation_data=val_ds,

    epochs=EPOCHS,

    callbacks=callbacks,

    verbose=1

)

# ============================================================
# Save Final Model
# ============================================================

model.save(

    MODEL_PATH,

    include_optimizer=True

)

print()

print("=" * 60)

print("Training Completed")

print("Final Model Saved To:")

print(MODEL_PATH)

print("=" * 60)

# ============================================================
# Final Evaluation
# ============================================================

loss, accuracy = model.evaluate(
    val_ds,
    verbose=1
)

print()

print("=" * 60)

print(f"Validation Loss      : {loss:.4f}")

print(f"Validation Accuracy  : {accuracy*100:.2f}%")

print("=" * 60)

# ============================================================
# Save Training History
# ============================================================

history_file = LOG_DIR / "history.txt"

with open(history_file, "w") as file:

    for key in history.history.keys():

        file.write(f"{key}\n")

        for value in history.history[key]:

            file.write(f"{value}\n")

        file.write("\n")

print()

print("Training history saved.")

print("Done.")