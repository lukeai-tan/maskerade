import cv2
from ocr_utils import detect_text
from pii_utils import analyze_pii
from face_utils import blur_faces
from image_processing import blur_bbox, save_image

def redact_image(input_path, output_path, min_confidence=0.5):
    img = cv2.imread(input_path)
    img = blur_faces(img)  # blur all faces

    merged_results = detect_text(img, min_confidence=min_confidence)  # OCR + merge boxes

    for bbox, text, prob in merged_results:
        if analyze_pii(text):
            img = blur_bbox(img, bbox)

    save_image(img, output_path)
    print(f"Blurred image saved as {output_path}")

if __name__ == "__main__":
    input_path = "uploads/faces.jpg"  # edit as needed
    output_path = "output/blurred_output.jpg"
    redact_image(input_path, output_path, min_confidence=0.5)
