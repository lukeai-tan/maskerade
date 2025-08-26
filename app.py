import os
import cv2
import easyocr
from presidio_analyzer import AnalyzerEngine

reader = easyocr.Reader(['en'])
analyzer = AnalyzerEngine()
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def redact_image(input_path, output_path):
    img = cv2.imread(input_path)

    # Detect faces
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        roi = img[y:y+h, x:x+w]
        img[y:y+h, x:x+w] = cv2.GaussianBlur(roi, (55, 55), 30)

    # Detect text regions
    results = reader.readtext(img)

    for (bbox, text, prob) in results:
        pii_results = analyzer.analyze(text=text, language="en")
        if pii_results:
            # Blur the text bounding box
            tl, tr, br, bl = bbox
            x_coords = [tl[0], tr[0], br[0], bl[0]]
            y_coords = [tl[1], tr[1], br[1], bl[1]]
            x_min, x_max = int(min(x_coords)), int(max(x_coords))
            y_min, y_max = int(min(y_coords)), int(max(y_coords))

            roi = img[y_min:y_max, x_min:x_max]
            img[y_min:y_max, x_min:x_max] = cv2.GaussianBlur(roi, (25, 25), 30)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cv2.imwrite(output_path, img)
    print(f"Blurred image saved as {output_path}")

if __name__ == "__main__":
    input_path = "uploads/faces.jpg"
    output_path = "output/blurred_output.jpg"
    redact_image(input_path, output_path)

