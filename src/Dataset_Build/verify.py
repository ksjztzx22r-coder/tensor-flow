from pathlib import Path
import cv2

try:
    from src.Dataset_Build.dataset_builder_config import *
except ModuleNotFoundError:
    from Dataset_Build.dataset_builder_config import *

SUPPORTED_EXTENSIONS = [

    ".jpg",

    ".jpeg",

    ".png"

]


def verify_class(class_name):

    folder = DATASET_DIR / class_name

    print()

    print("=" * 60)

    print(f"Class : {class_name}")

    print("=" * 60)

    if not folder.exists():

        print("Folder not found.")

        return

    images = [

        file

        for file in folder.iterdir()

        if file.suffix.lower() in SUPPORTED_EXTENSIONS

    ]

    print("Images :", len(images))

    corrupted = 0

    wrong_size = 0

    valid = 0

    for image_path in images:

        image = cv2.imread(str(image_path))

        if image is None:

            corrupted += 1

            continue

        h, w = image.shape[:2]

        if (

            w != IMAGE_WIDTH

            or

            h != IMAGE_HEIGHT

        ):

            wrong_size += 1

        else:

            valid += 1

    print("Valid Images :", valid)

    print("Wrong Size :", wrong_size)

    print("Corrupted :", corrupted)


def verify_split(folder_name, folder):

    print()

    print("=" * 60)

    print(folder_name)

    print("=" * 60)

    total = 0

    for cls in CLASSES:

        class_folder = folder / cls

        if not class_folder.exists():

            print(f"{cls}: Missing")

            continue

        count = len(

            [

                file

                for file in class_folder.iterdir()

                if file.suffix.lower() in SUPPORTED_EXTENSIONS

            ]

        )

        total += count

        print(f"{cls}: {count}")

    print()

    print("Total :", total)


def verify_dataset():

    print()

    print("=" * 60)

    print("VERIFYING DATASET")

    print("=" * 60)

    for cls in CLASSES:

        verify_class(cls)

    verify_split(

        "TRAIN DATASET",

        TRAIN_DIR

    )

    verify_split(

        "VALIDATION DATASET",

        VALID_DIR

    )

    verify_split(

        "TEST DATASET",

        TEST_DIR

    )

    print()

    print("=" * 60)

    print("Verification Complete")

    print("=" * 60)


if __name__ == "__main__":

    verify_dataset()