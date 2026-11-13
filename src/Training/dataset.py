import tensorflow as tf

try:
    from src.Training.config import *
except ModuleNotFoundError:
    from Training.config import *

AUTOTUNE = tf.data.AUTOTUNE


def load_dataset():
    train_dir = DATASET_DIR / "train"
    val_dir = DATASET_DIR / "validation"

    train_ds = tf.keras.utils.image_dataset_from_directory(
    train_dir,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="int",
    shuffle=True
)

    val_ds = tf.keras.utils.image_dataset_from_directory(
    val_dir,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="int",
    shuffle=False
)


    train_ds = train_ds.cache()

    train_ds = train_ds.shuffle(1000)

    train_ds = train_ds.prefetch(AUTOTUNE)

    val_ds = val_ds.cache()

    val_ds = val_ds.prefetch(AUTOTUNE)

    return train_ds, val_ds


def get_class_names():

    dataset = tf.keras.utils.image_dataset_from_directory(
    DATASET_DIR / "train",

        batch_size=BATCH_SIZE,

        image_size=IMAGE_SIZE

    )

    return dataset.class_names


def dataset_size():

    dataset = tf.keras.utils.image_dataset_from_directory(
    DATASET_DIR / "train",

        batch_size=BATCH_SIZE,

        image_size=IMAGE_SIZE

    )

    count = 0

    for images, labels in dataset:

        count += images.shape[0]

    return count


def verify_dataset():

    print("=" * 60)

    print("Dataset Path")

    print(DATASET_DIR)

    print()

    print("Exists:", DATASET_DIR.exists())

    print()

    print("Classes:")

    print(get_class_names())

    print()

    print("Images:")

    print(dataset_size())

    print("=" * 60)


if __name__ == "__main__":

    verify_dataset()