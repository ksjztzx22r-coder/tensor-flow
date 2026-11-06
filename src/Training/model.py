import tensorflow as tf

from Training.config import *

# ============================================================
# Data Augmentation
# ============================================================

data_augmentation = tf.keras.Sequential(

    [

        tf.keras.layers.RandomFlip("horizontal"),

        tf.keras.layers.RandomRotation(0.15),

        tf.keras.layers.RandomZoom(0.15),

        tf.keras.layers.RandomContrast(0.10),

        tf.keras.layers.RandomBrightness(0.10)

    ],

    name="data_augmentation"

)

# ============================================================
# Build Model
# ============================================================

def build_model():

    base_model = tf.keras.applications.MobileNetV3Small(

        input_shape=(IMG_HEIGHT, IMG_WIDTH, CHANNELS),

        include_top=False,

        weights="imagenet",

        pooling=None,

        name="mobilenet_base"

    )

    base_model.trainable = False

    inputs = tf.keras.Input(

        shape=(IMG_HEIGHT, IMG_WIDTH, CHANNELS),

        name="input_image"

    )

    x = data_augmentation(inputs, training=True)

    x = tf.keras.applications.mobilenet_v3.preprocess_input(x)

    x = base_model(

        x,

        training=False

    )

    x = tf.keras.layers.GlobalAveragePooling2D()(x)

    x = tf.keras.layers.BatchNormalization()(x)

    x = tf.keras.layers.Dropout(0.30)(x)

    x = tf.keras.layers.Dense(

        256,

        activation="relu"

    )(x)

    x = tf.keras.layers.Dropout(0.20)(x)

    outputs = tf.keras.layers.Dense(

        NUM_CLASSES,

        activation="softmax",

        name="predictions"

    )(x)

    model = tf.keras.Model(

        inputs,

        outputs,

        name="WildlifeDetector"

    )

    model.compile(

        optimizer=tf.keras.optimizers.Adam(

            learning_rate=LEARNING_RATE

        ),

        loss="sparse_categorical_crossentropy",

        metrics=[
    "accuracy"
]

    )

    return model

# ============================================================
# Fine Tune
# ============================================================

def unfreeze_model(model):

    base_model = model.get_layer("mobilenet_base")

    base_model.trainable = True

    freeze_until = int(

        len(base_model.layers) * 0.80

    )

    for layer in base_model.layers[:freeze_until]:

        layer.trainable = False

    for layer in base_model.layers[freeze_until:]:

        layer.trainable = True

    model.compile(

        optimizer=tf.keras.optimizers.Adam(

            learning_rate=FINE_TUNE_LR

        ),

        loss="sparse_categorical_crossentropy",

        metrics=[
    "accuracy"
]

    )

    return model