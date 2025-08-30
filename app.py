from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    redirect,
    session,
    url_for,
)
import cv2
import numpy as np
import os
import base64
import secrets
from flask_session import Session
from custom_types import CensorRegion
from face_utils import detect_faces
from image_processing import preprocess_faces, preprocess_text, redact
from ocr_utils import detect_pii_text

# Set allowed extensions for file upload
ALLOWED_EXTENSIONS = {"webp", "png", "jpg", "jpeg"}

# Create Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(24)

# Configure session to store on the server (using filesystem here)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
Session(app)

# Folder for saving uploaded images
UPLOAD_FOLDER = ".uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# Function to normalize bounding box (ensuring proper coordinates)
def normalize_bbox(bbox: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = bbox
    x_min, x_max = sorted([x1, x2])
    y_min, y_max = sorted([y1, y2])
    return (x_min, y_min, x_max, y_max)


# Function to crop and encode an image region
def crop_and_encode(img: np.ndarray, bbox: tuple[int, int, int, int]) -> str:
    x1, y1, x2, y2 = bbox
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    cropped_img = img[y1:y2, x1:x2]
    if cropped_img.size == 0:
        return ""
    success, encoded_img = cv2.imencode(".webp", cropped_img)
    if not success:
        return ""
    return "data:image/webp;base64," + base64.b64encode(encoded_img).decode("utf-8")


@app.route("/", methods=["GET"])
def start():
    app.logger.info("GET / start called")
    return render_template("upload.html", view="upload")


# Route to upload the image
@app.route("/upload", methods=["POST"])
def upload_image() -> str:
    if "image" not in request.files:
        return redirect(url_for("start"))

    image = request.files["image"]
    if image.filename == "":
        return redirect(url_for("start"))

    # Save the uploaded image to disk
    filename = f"{secrets.token_hex(16)}.{image.filename.rsplit('.', 1)[1].lower()}"
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(image_path)

    # Process the image with OpenCV
    img_cv = cv2.imread(image_path)

    # Detect faces and PII in the image
    censor_requests: list[CensorRegion] = detect_faces(img_cv) + detect_pii_text(img_cv)

    # Store only the image path in the session
    session["image_path"] = image_path
    # When saving to session, store CensorRegion objects instead of dicts
    session["censor_requests"] = [
        CensorRegion(name=region.name, bbox=region.bbox, is_censored=region.is_censored)
        for region in censor_requests
    ]

    # Prepare data for the table
    table_data: list[dict[str, object]] = []
    for region in censor_requests:
        cropped_img_url: str = crop_and_encode(img_cv, region.bbox)
        table_data.append(
            {
                "name": region.name,
                "bbox": region.bbox,
                "is_censored": region.is_censored,
                "image_url": cropped_img_url,
            }
        )

    # Apply redactions to the image
    success, redacted_img = redact(img_cv, censor_requests)
    if success:
        if redacted_img is None or redacted_img.size == 0:
            return jsonify(success=False, error="Redacted image is invalid or empty.")

        # Encode the image to base64 string
        img_base64 = base64.b64encode(redacted_img).decode("utf-8")
        image_data_url = f"data:image/webp;base64,{img_base64}"

    else:
        # In case redaction failed, fallback to original image encoding (JPEG)
        _, img_encoded = cv2.imencode(".jpg", img_cv)
        img_base64 = base64.b64encode(img_encoded).decode("utf-8")
        image_data_url = f"data:image/jpeg;base64,{img_base64}"

    return render_template(
        "display.html", view="display", image_url=image_data_url, table_data=table_data
    )


# Route to update censor regions
@app.route("/update_censor_regions", methods=["POST"])
def update_censor_regions() -> "flask.wrappers.Response":
    data: list[dict[str, object]] | None = request.get_json()
    if not data:
        return jsonify(success=False, error="No data received")

    image_path = session.get("image_path")
    censor_requests: list[CensorRegion] | None = session.get("censor_requests")

    if not image_path or not censor_requests:
        return jsonify(success=False, error="Session expired or missing data")

    # Update the censor regions directly using the CensorRegion objects in the session
    for item in data:
        idx: int = int(item["idx"])
        is_censored: bool = bool(item["is_censored"])

        # Modify the CensorRegion directly (no need to convert to dict)
        censor_requests[idx].is_censored = is_censored

    session["censor_requests"] = censor_requests  # Update session with modified objects

    # Process the image with OpenCV
    img_cv = cv2.imread(image_path)

    # Apply redactions to the image
    success, redacted_img = redact(img_cv, censor_requests)
    if success:
        if redacted_img is None or redacted_img.size == 0:
            return jsonify(success=False, error="Redacted image is invalid or empty.")

        # Encode the image to base64 string
        img_base64 = base64.b64encode(redacted_img).decode("utf-8")
        image_data_url = f"data:image/webp;base64,{img_base64}"

    else:
        # In case redaction failed, fallback to original image encoding (JPEG)
        _, img_encoded = cv2.imencode(".jpg", img_cv)
        img_base64 = base64.b64encode(img_encoded).decode("utf-8")
        image_data_url = f"data:image/jpeg;base64,{img_base64}"

    return jsonify(success=True, image_url=image_data_url)


"""
# Optional: Serve uploaded files if needed
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
"""
