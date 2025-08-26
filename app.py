import os
import cv2
import easyocr
import numpy as np
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
import face_recognition

# Initialize OCR
reader = easyocr.Reader(['en'])

# Initialize Presidio analyzer
analyzer = AnalyzerEngine()

# Custom recognizer for full credit card numbers
cc_pattern = Pattern(
    name="credit_card_full",
    regex=r"\b(?:\d[ -]*?){13,16}\b",  # 13-16 digits with optional spaces/dashes
    score=0.9
)
cc_recognizer = PatternRecognizer(supported_entity="CREDIT_CARD", patterns=[cc_pattern])
analyzer.registry.add_recognizer(cc_recognizer)

# TODO: add more custom recognizers (driver's license, passport, etc.)

def merge_boxes(results, x_threshold=10, y_threshold=10):
    """
    Merge OCR boxes that are close horizontally and vertically.
    Returns list of tuples: (merged_text, merged_bbox)
    """
    merged = []
    used = set()

    for i, (bbox1, text1, prob1) in enumerate(results):
        if i in used:
            continue
        x1s = [p[0] for p in bbox1]
        y1s = [p[1] for p in bbox1]
        x_min = min(x1s)
        x_max = max(x1s)
        y_min = min(y1s)
        y_max = max(y1s)
        merged_text = text1

        for j, (bbox2, text2, prob2) in enumerate(results):
            if j <= i or j in used:
                continue
            x2s = [p[0] for p in bbox2]
            y2s = [p[1] for p in bbox2]
            x2_min, x2_max = min(x2s), max(x2s)
            y2_min, y2_max = min(y2s), max(y2s)

            # if boxes are close horizontally and vertically, merge
            if abs(x_min - x2_min) < x_threshold and abs(y_min - y2_min) < y_threshold:
                x_min = min(x_min, x2_min)
                x_max = max(x_max, x2_max)
                y_min = min(y_min, y2_min)
                y_max = max(y_max, y2_max)
                merged_text += " " + text2
                used.add(j)

        merged_bbox = [(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)]
        merged.append((merged_bbox, merged_text))

    return merged

def redact_image(input_path, output_path):
    img = cv2.imread(input_path)

    # Detect faces using face_recognition
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_img)
    for top, right, bottom, left in face_locations:
        roi = img[top:bottom, left:right]
        img[top:bottom, left:right] = cv2.GaussianBlur(roi, (55, 55), 30)

    # OCR text detection
    results = reader.readtext(img)

    # Merge nearby OCR boxes
    merged_results = merge_boxes(results)

    # PII detection + blur
    for bbox, text in merged_results:
        pii_results = analyzer.analyze(text=text, language="en")
        if pii_results:
            tl, tr, br, bl = bbox
            x_coords = [tl[0], tr[0], br[0], bl[0]]
            y_coords = [tl[1], tr[1], br[1], bl[1]]
            x_min, x_max = int(min(x_coords)), int(max(x_coords))
            y_min, y_max = int(min(y_coords)), int(max(y_coords))

            roi = img[y_min:y_max, x_min:x_max]
            img[y_min:y_max, x_min:x_max] = cv2.GaussianBlur(roi, (25, 25), 30)

    # Save output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, img)
    print(f"Blurred image saved as {output_path}")

if __name__ == "__main__":
    input_path = "uploads/faces.jpg" # edit this
    output_path = "output/blurred_output.jpg"
    redact_image(input_path, output_path)

