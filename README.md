# Wildlife Intrusion Detection System

An end-to-end edge AI system for detecting wildlife intrusions (Elephant, Wild Boar, Monkey, Background) and triggering audio deterrents, designed to deploy on Raspberry Pi with TensorFlow Lite.

---

## 📌 Project Overview

* **Edge Architecture:** MobileNetV3-Small backbone optimized and quantized to TensorFlow Lite (`wildlife.tflite`) for real-time edge inference.
* **Target Classes:**
  * `elephant`
  * `wildboar`
  * `monkey`
  * `background`
* **Autonomous Deterrence:** Automatically plays specific deterrence frequencies/sounds (`sounds/elephant.wav`, `sounds/boar&monkey.wav`) upon detecting target animals, with cooldown mechanisms and event logging.

---

## 📁 Repository Structure

```
├── models/                     # Trained model checkpoints
│   ├── best_model.keras        # Best checkpoint saved during training
│   ├── wildlife.keras          # Full Keras model
│   └── wildlife.tflite         # Quantized TFLite model for Raspberry Pi
├── sounds/                     # Audio deterrent files
│   ├── elephant.wav            # Deterrence sound for elephants
│   └── boar&monkey.wav         # Deterrence sound for boars & monkeys
├── src/
│   ├── Dataset_Build/          # Dataset preprocessing, split, and verification
│   │   ├── dataset_builder_config.py
│   │   ├── preprocess.py
│   │   ├── split.py
│   │   └── verify.py
│   ├── Rasp_Pi/                # Edge runtime deployed on Raspberry Pi
│   │   ├── raspi_config.py     # Configuration (thresholds, paths, pins)
│   │   ├── camera.py           # Video capture handling
│   │   ├── detector.py         # TFLite inference engine
│   │   ├── audio.py            # Audio playback management
│   │   ├── logger.py           # CSV detection logger & frame snapshot
│   │   ├── gpio_setup.py       # GPIO peripheral control
│   │   └── main.py             # Main runtime loop
│   └── Training/               # Model definition, training & export pipeline
│       ├── config.py           # Training hyperparameters & image dimensions
│       ├── model.py            # MobileNetV3-Small architecture & augmentation
│       ├── dataset.py          # Data pipeline loader
│       ├── train.py            # Training script
│       ├── finetune.py         # Fine-tuning backbone layers
│       ├── evaluate.py         # Model evaluation metrics
│       ├── export_tflite.py    # TFLite conversion & quantization
│       └── webcam_test.py      # Real-time webcam validation script
├── requirements.txt            # Python dependencies
└── .gitignore                  # Git ignore rules for datasets, logs, and venvs
```

---

## 🚀 Getting Started

### 1. Prerequisites & Installation

Clone the repository and install dependencies in a virtual environment:

```bash
git clone https://github.com/ksjztzx22r-coder/tensor-flow.git
cd tensor-flow

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

---

### 2. Testing via Webcam

To test the trained model on your local machine using a webcam:

```bash
python -m src.Training.webcam_test
```

---

### 3. Deploying to Raspberry Pi

1. Transfer the project files (`src/Rasp_Pi`, `models/wildlife.tflite`, and `sounds/`) to your Raspberry Pi.
2. Install `tflite-runtime` and `opencv-python`:
   ```bash
   pip install tflite-runtime opencv-python pygame
   ```
3. Run the main detection loop:
   ```bash
   python -m src.Rasp_Pi.main
   ```

---

## 🛠 Model Training Pipeline

If you wish to retrain or fine-tune the model:

1. **Preprocess and split dataset:**
   ```bash
   python -m src.Dataset_Build.preprocess
   python -m src.Dataset_Build.split
   python -m src.Dataset_Build.verify
   ```

2. **Train model:**
   ```bash
   python -m src.Training.train
   ```

3. **Fine-tune backbone layers:**
   ```bash
   python -m src.Training.finetune
   ```

4. **Export to TensorFlow Lite:**
   ```bash
   python -m src.Training.export_tflite
   ```
