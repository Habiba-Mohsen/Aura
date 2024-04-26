import os
from fastapi import HTTPException
import cv2
import numpy as np
from numba import jit, prange
import time
import base64
from secrets import token_hex

from api.config import uploads_folder


def generate_image_id():
    timestamp = str(int(time.time()))[-4]
    randomPart = token_hex(2)
    imageID = f"{timestamp}{randomPart}"
    return imageID


def read_image(image_path: str, grayscale=False):
    if grayscale:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    else:
        original_image = cv2.imread(image_path)
        image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
    return image


def get_image(image_id):
    image_path = None

    for filename in os.listdir(uploads_folder):
        if filename.startswith(f"{image_id}."):
            image_path = os.path.join(uploads_folder, filename)
            return image_path

    if image_path is None:
        raise HTTPException(status_code=404, detail="Image not found.")


def convert_image(output_image, is_float=False):
    if is_float:
        output_image = np.clip(output_image * 255, 0, 255).astype(np.uint8)
    else:
        output_image = np.clip(output_image, 0, 255).astype(np.uint8)

    is_success, buffer = cv2.imencode(
        ".jpg", cv2.cvtColor(output_image, cv2.COLOR_RGB2BGR)
    )

    if is_success:
        base64_image = base64.b64encode(buffer).decode("utf-8")
        return base64_image
    else:
        raise ValueError("Failed to encode the image as Base64")


def get_image_dimensions(image):
    if len(image.shape) == 2:
        height, width = image.shape
        channels = 1
    elif len(image.shape) == 3:
        height, width, channels = image.shape
    else:
        raise ValueError("Unsupported image shape")

    return height, width, channels


def pad_image(image, kernel_size):
    _, _, channels = get_image_dimensions(image)

    pad = kernel_size // 2

    if channels == 1:
        padded_image = np.pad(image, ((pad, pad), (pad, pad)), mode="constant")
    else:
        padded_image = np.pad(image, ((pad, pad), (pad, pad), (0, 0)), mode="constant")

    return padded_image, pad


def compute_fft(image):
    f_transform = np.fft.fft2(image)
    f_transform_shifted = np.fft.fftshift(f_transform)
    return f_transform_shifted


def gaussian_kernel(size: int, sigma: float):
    kernel = np.fromfunction(
        lambda x, y: (1 / (2 * np.pi * sigma**2))
        * np.exp(
            -((x - (size - 1) / 2) ** 2 + (y - (size - 1) / 2) ** 2) / (2 * sigma**2)
        ),
        (size, size),
    )
    kernel = (kernel + kernel.T) / 2
    return kernel / np.sum(kernel)


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


@jit(nopython=True)
def euclidean_distance(point1, point2):
    return np.sqrt(np.sum((point1 - point2) ** 2))


@jit(nopython=True, parallel=True)
def compute_distances(feature_space, current_mean_array):
    distances = np.zeros(feature_space.shape[0])
    for i in prange(len(feature_space)):
        distance = 0
        for j in range(5):
            distance += (current_mean_array[0][j] - feature_space[i][j]) ** 2
        distances[i] = distance**0.5
    return distances

def resize_image(image_data):
    if image_data.shape[0] > 1000:
        image_data = cv2.resize(image_data, (0,0), fx=0.25, fy=0.25)
    if image_data.shape[0] > 500:
        image_data = cv2.resize(image_data, (0,0), fx=0.5, fy=0.5)
    return image_data

def gaussian_filter(image_data, filter_size=3):
    return cv2.GaussianBlur(image_data, (filter_size,filter_size), 0)