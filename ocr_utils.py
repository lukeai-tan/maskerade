import easyocr

from pii_utils import analyze_pii
from custom_types import CensorRegion
from image_processing import preprocess_text

reader: easyocr.Reader = easyocr.Reader(["en"])


def detect_pii_text(img: object) -> list[CensorRegion]:
    print("OCR Running")
    ocr_results = reader.readtext(preprocess_text(img), text_threshold=0.6, low_text=0.3)  # type: ignore

    censor_regions: list[CensorRegion] = []

    for region in ocr_results:  # type: ignore

        # bbox: list of 4 points [ [x, y], ... ] representing corners in this order:
        # top-left, top-right, bottom-right, bottom-left
        bbox: list[list[int]] = region[0]  # type: ignore

        text: str = region[1]  # type: ignore
        probability: float = region[2]  # type: ignore

        # Convert bbox to (x_min, y_min, x_max, y_max)
        x_coords = [point[0] for point in bbox]
        y_coords = [point[1] for point in bbox]
        bbox_tuple = (min(x_coords), min(y_coords), max(x_coords), max(y_coords))

        pii_name: str = f"PII Text: {text.split(' ')[:min(3, len(text.split(' ')))]}"  # type: ignore
        pii_results: list[RecognizerResult] = analyze_pii(text)  # type: ignore
        should_censor = len(pii_results) > 0  # type: ignore

        if should_censor:
            censor_regions.append(CensorRegion(name=pii_name, bbox=bbox_tuple))

    print("OCR Completed")
    return censor_regions
