from pathlib import Path

# ==========================================================
# Project Directories
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATASET_DIR = PROJECT_ROOT / "Dataset_raw"

DATASET_DIR = PROJECT_ROOT / "dataset"

TRAIN_DIR = DATASET_DIR / "train"

VALID_DIR = DATASET_DIR / "validation"

TEST_DIR = DATASET_DIR / "test"

# ==========================================================
# Image Processing
# ==========================================================

IMAGE_WIDTH = 96

IMAGE_HEIGHT = 96

IMAGE_SIZE = (IMAGE_WIDTH, IMAGE_HEIGHT)

IMAGE_FORMAT = ".jpg"

# ==========================================================
# Dataset Split
# ==========================================================

TRAIN_SPLIT = 0.70

VALID_SPLIT = 0.20

TEST_SPLIT = 0.10

RANDOM_SEED = 42

# ==========================================================
# Classes
# ==========================================================

CLASSES = [

    "elephant",

    "wildboar",

    "monkey",

    "background"

]

# ==========================================================
# Limits
# ==========================================================

MAX_IMAGES_PER_CLASS = 5000

# ==========================================================
# Create Directories
# ==========================================================

for folder in [

    RAW_DATASET_DIR,

    DATASET_DIR,

    TRAIN_DIR,

    VALID_DIR,

    TEST_DIR

]:

    folder.mkdir(

        parents=True,

        exist_ok=True

    )

for cls in CLASSES:

    (TRAIN_DIR / cls).mkdir(

        parents=True,

        exist_ok=True

    )

    (VALID_DIR / cls).mkdir(

        parents=True,

        exist_ok=True

    )

    (TEST_DIR / cls).mkdir(

        parents=True,

        exist_ok=True

    )