import cv2
from pathlib import Path

try:
    from src.Dataset_Build.dataset_builder_config import *
except ModuleNotFoundError:
    from Dataset_Build.dataset_builder_config import *

SUPPORTED_EXTENSIONS = [
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff"
]


def preprocess_image(input_path, output_path):

    image = cv2.imread(str(input_path))

    if image is None:
        print(f"Failed: {input_path}")
        return False

    image = cv2.resize(
        image,
        IMAGE_SIZE,
        interpolation=cv2.INTER_AREA
    )

    cv2.imwrite(
        str(output_path),
        image
    )

    return True


def preprocess_class(class_name):

    source_dir = RAW_DATASET_DIR / class_name

    output_dir = DATASET_DIR / class_name

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    if not source_dir.exists():

        print(f"{class_name} folder missing.")

        return

    image_number = 0

    for image_file in sorted(source_dir.iterdir()):

        if image_file.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        if image_number >= MAX_IMAGES_PER_CLASS:
            break

        output_file = output_dir / f"{image_number:05d}.jpg"

        success = preprocess_image(
            image_file,
            output_file
        )

        if success:
            image_number += 1

    print(f"{class_name}: {image_number} images processed.")


def preprocess_dataset():

    print("=" * 60)
    print("PREPROCESSING DATASET")
    print("=" * 60)

    for cls in CLASSES:

        preprocess_class(cls)

    print()
    print("Finished preprocessing.")


if __name__ == "__main__":

    preprocess_dataset()