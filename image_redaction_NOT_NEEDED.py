"""import cv2
from ocr_utils import detect_text
from pii_utils import analyze_pii
from face_utils import blur_faces
from image_processing import redact, save_image


def redact_image(
    input_path: str, output_path: str, min_confidence: float = 0.4
) -> None:

    img: cv2.typing.MatLike = cv2.imread(input_path)  # type: ignore

    # Blurs faces
    img = blur_faces(img)

    # OCR + merge boxes
    merged_results = detect_text(img, min_confidence=min_confidence)

    for bbox, text, prob in merged_results:
        if prob < min_confidence:
            continue
        if analyze_pii(text):
            img = black_censor_box(img, bbox)

    save_image(img, output_path)
    print(f"Redacted image saved as {output_path}")


# def some_test_function(input_path: str, output_path: str) -> None:
#     input_path = "uploads/creditcard.jpg"  # Edit as needed
#     output_path = "output/blurred_output.jpg"
#     redact_image(input_path, output_path, min_confidence=0.5)
"""
