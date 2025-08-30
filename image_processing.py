import cv2
import numpy as np
from numpy.typing import NDArray
from custom_types import CensorRegion


def preprocess_text(image):
    """
    Preprocess the image for text recognition using EasyOCR.

    Args:
    - image_path (str): Path to the input image.
    - target_size (tuple): Target size for resizing the image (width, height).

    Returns:
    - preprocessed_image (numpy array): The preprocessed image ready for EasyOCR text recognition.
    """

    if image is None:
        raise ValueError(f"Image at path {image_path} could not be loaded.")

    # Convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Histogram Equalization for better contrast
    gray_image = cv2.equalizeHist(gray_image)

    # Optional: Denoise the image using GaussianBlur (light application to reduce noise)
    gray_image = cv2.GaussianBlur(gray_image, (3, 3), 0)

    # CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray_image = clahe.apply(gray_image)

    # Optional: Smoothing with bilateral filter to reduce noise while preserving edges
    gray_image = cv2.bilateralFilter(gray_image, 9, 75, 75)

    # Returning the preprocessed image which is ready for OCR
    return gray_image


def preprocess_faces(image):
    # We apply it directly on each channel (R, G, B) for better color preservation
    image_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    image_yuv[:, :, 0] = cv2.equalizeHist(
        image_yuv[:, :, 0]
    )  # Only apply to the Y (luminance) channel
    image = cv2.cvtColor(image_yuv, cv2.COLOR_YUV2BGR)

    # Optional: CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    image_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    image_yuv[:, :, 0] = clahe.apply(image_yuv[:, :, 0])  # Apply CLAHE to Y channel
    image = cv2.cvtColor(image_yuv, cv2.COLOR_YUV2BGR)

    return image


def redact(
    img: cv2.typing.MatLike,
    censored_regions: list[CensorRegion],
) -> tuple[bool, NDArray[np.uint8]]:

    # Check if img is valid
    if img is None or img.size == 0:
        print("Error: Invalid image passed to redact function.")
        return False, None

    for region in censored_regions:
        if not region.is_censored:
            continue

        try:
            x1, y1, x2, y2 = region.bbox

            # Ensure coordinates are within bounds
            x1, x2 = sorted([max(0, x1), min(img.shape[1], x2)])
            y1, y2 = sorted([max(0, y1), min(img.shape[0], y2)])

            # Draw a black box (0 for all color channels)
            img[y1:y2, x1:x2] = 0

        except Exception as e:
            print(f"Skipping region due to error: {region} -> {e}")
            continue

    # Check the shape after redaction
    print(f"Redacted image shape: {img.shape}")  # Log shape after redaction

    # Try to encode the redacted image
    success, encoded_image = cv2.imencode(ext=".webp", img=img)

    # Check if the encoding was successful
    if not success:
        print("Error: Image encoding failed.")
        return False, None

    # Check the size of the encoded image to ensure it's not empty
    if encoded_image.size == 0:
        print("Error: Encoded image is empty.")
        return False, None

    print(f"Encoded image size: {encoded_image.size}")  # Log the encoded image size

    # Return encoded image
    return True, encoded_image
