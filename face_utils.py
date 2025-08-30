import cv2
import face_recognition

from custom_types import CensorRegion
from image_processing import preprocess_faces


def detect_faces(img: cv2.typing.MatLike) -> list[CensorRegion]:
    """Detect faces and return a list of CensorRegion objects.

    Each CensorRegion bbox is in [top, right, bottom, left] format.
    """
    print("Facial detection running")

    face_locations = face_recognition.face_locations(preprocess_faces(img))  # type: ignore
    print(str(len(face_locations)) + " detected")

    print("Facial Detection Completed")

    # Convert to [left, top, right, bottom] format for OpenCV
    return [
        CensorRegion(
            name=f"face_{i}", bbox=(loc[3] - 8, loc[0] - 8, loc[1] + 8, loc[2] + 8)
        )  # loc is (top, right, bottom, left) # type: ignore
        for i, loc in enumerate(face_locations)  # type: ignore
    ]
