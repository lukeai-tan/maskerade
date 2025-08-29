import cv2
import face_recognition
import numpy as np
from typing import Any

def blur_faces(
    img: np.ndarray[Any, Any],
    blur_strength: tuple[int, int] = (55, 55)
) -> np.ndarray[Any, Any]:
    rgb_img: np.ndarray[Any, Any] = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    face_locations: list[tuple[int, int, int, int]] = face_recognition.face_locations(rgb_img)  # type: ignore
    for top, right, bottom, left in face_locations:
        roi: np.ndarray[Any, Any] = img[top:bottom, left:right]
        img[top:bottom, left:right] = cv2.GaussianBlur(roi, blur_strength, 0)
    return img
