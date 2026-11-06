import tensorflow as tf

from dataset import load_dataset

from model import unfreeze_model

from Training.config import *

train_ds, val_ds = load_dataset()

model = tf.keras.models.load_model(

    MODEL_PATH,

    compile=False

)

model = unfreeze_model(model)

callbacks = [

    tf.keras.callbacks.ModelCheckpoint(

        CHECKPOINT_PATH,

        monitor="val_accuracy",

        save_best_only=True,

        verbose=1

    ),

    tf.keras.callbacks.EarlyStopping(

        monitor="val_loss",

        patience=5,

        restore_best_weights=True,

        verbose=1

    ),

    tf.keras.callbacks.ReduceLROnPlateau(

        monitor="val_loss",

        factor=0.2,

        patience=2,

        verbose=1

    )

]

model.fit(

    train_ds,

    validation_data=val_ds,

    epochs=FINE_TUNE_EPOCHS,

    callbacks=callbacks,

    verbose=1

)

model.save(

    MODEL_PATH

)

print("Fine tuning complete.")