#import section
import os
import numpy as np
import h5py
import matplotlib.pyplot as plt
import tensorflow as tf
import keras
from keras import layers
from tensorflow.python.keras.layers import Flatten
from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras.losses import SparseCategoricalCrossentropy
from sklearn.metrics import accuracy_score
from sys import getsizeof

#helper functions
def get_file_size(file_path):
    size = os.path.getsize(file_path)
    return size
def convert_bytes(size, unit=None):
    if unit == "KB":
        return print('File size: ' + str(round(size / 1024, 3)) + ' Kilobytes')
    elif unit == "MB":
        return print('File size: ' + str(round(size / (1024 * 1024), 3)) + ' Megabytes')
    else:
        return print('File size: ' + str(size) + ' bytes')
    
#dataset call
@misc{imagescv_indian_elephant_2026,
  title        = {Indian elephant Image Classification Dataset},
  author       = {{images.cv}},
  year         = {2026},
  howpublished = {\url{https://images.cv/dataset/indian_elephant-image-classification-dataset}},
  note         = {Labeled image dataset for computer vision research.}
}

# Load the dataset (PyTorch ImageFolder)
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

transform = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
])

train_ds = datasets.ImageFolder('./indian_elephant/data/train', transform=transform)
val_ds   = datasets.ImageFolder('./indian_elephant/data/val',   transform=transform)

train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)
val_loader   = DataLoader(val_ds,   batch_size=32)

print(f'Classes: {train_ds.classes}')
print(f'Train:   {len(train_ds)} images')
print(f'Val:     {len(val_ds)} images')