import random
import shutil

from pathlib import Path

try:
    from src.Dataset_Build.dataset_builder_config import *
except ModuleNotFoundError:
    from Dataset_Build.dataset_builder_config import *

random.seed(RANDOM_SEED)

SUPPORTED_EXTENSIONS = [

    ".jpg",

    ".jpeg",

    ".png"

]


def clear_directory(folder):

    if not folder.exists():

        return

    for file in folder.iterdir():

        if file.is_file():

            file.unlink()


def split_class(class_name):

    # Prefer DATASET_DIR / class_name (where user uploads large curated datasets), fallback to RAW_DATASET_DIR
    dataset_class_dir = DATASET_DIR / class_name
    if dataset_class_dir.exists() and any(dataset_class_dir.iterdir()):
        source = dataset_class_dir
    else:
        source = RAW_DATASET_DIR / class_name

    train_folder = TRAIN_DIR / class_name

    valid_folder = VALID_DIR / class_name

    test_folder = TEST_DIR / class_name

    clear_directory(train_folder)

    clear_directory(valid_folder)

    clear_directory(test_folder)

    images = []

    for file in source.iterdir():

        if file.suffix.lower() in SUPPORTED_EXTENSIONS:

            images.append(file)

    random.shuffle(images)

    total = len(images)

    train_end = int(total * TRAIN_SPLIT)

    valid_end = train_end + int(total * VALID_SPLIT)

    train_images = images[:train_end]

    valid_images = images[train_end:valid_end]

    test_images = images[valid_end:]

    for image in train_images:

        shutil.copy2(

            image,

            train_folder / image.name

        )

    for image in valid_images:

        shutil.copy2(

            image,

            valid_folder / image.name

        )

    for image in test_images:

        shutil.copy2(

            image,

            test_folder / image.name

        )

    print()

    print(class_name)

    print("---------------------------")

    print("Train :", len(train_images))

    print("Validation :", len(valid_images))

    print("Test :", len(test_images))


def split_dataset():

    print()

    print("=" * 60)

    print("Splitting Dataset")

    print("=" * 60)

    for class_name in CLASSES:

        split_class(class_name)

    print()

    print("=" * 60)

    print("Dataset Split Complete")

    print("=" * 60)


if __name__ == "__main__":

    split_dataset()