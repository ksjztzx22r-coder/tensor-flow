import tensorflow as tf

try:
    from src.Training.dataset import load_dataset
    from src.Training.model import build_model
    from src.Training.config import *
except ModuleNotFoundError:
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

import time

class ResilientModelCheckpoint(tf.keras.callbacks.ModelCheckpoint):
    """Handles transient Windows file locks (Errno 22 / Antivirus indexing) gracefully."""
    def _save_model(self, epoch, batch, logs):
        for attempt in range(5):
            try:
                super()._save_model(epoch, batch, logs)
                return
            except (OSError, PermissionError) as e:
                time.sleep(0.5)
                if attempt == 4:
                    print(f"\n[WARNING] Checkpoint file temporarily locked by Windows: {e}. Skipping epoch save.")

checkpoint = ResilientModelCheckpoint(

    filepath=str(CHECKPOINT_PATH),

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
# Balanced Class Weights
# ============================================================

train_dir = DATASET_DIR / "train"
class_names = sorted([d.name for d in train_dir.iterdir() if d.is_dir()])
class_counts = {}
total_train = 0
for i, c_name in enumerate(class_names):
    count = len(list((train_dir / c_name).glob("*.*")))
    class_counts[i] = count
    total_train += count

class_weights = {}
for i, count in class_counts.items():
    class_weights[i] = total_train / (len(class_names) * max(count, 1))

print(f"[TRAIN] Class counts: {{class_names[i]: class_counts[i] for i in class_counts}}")
print(f"[TRAIN] Balanced class weights: {{class_names[i]: round(class_weights[i], 3) for i in class_weights}}")

# ============================================================
# Train
# ============================================================

history = model.fit(

    train_ds,

    validation_data=val_ds,

    epochs=EPOCHS,

    callbacks=callbacks,

    class_weight=class_weights,

    verbose=1

)

# ============================================================
# Save Final Model
# ============================================================

model.save(

    str(MODEL_PATH),

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