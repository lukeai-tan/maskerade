from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_from_directory,
)
import os
from werkzeug.utils import secure_filename
from redact_image_call import redact_image

UPLOAD_FOLDER = "uploads/"
OUTPUT_FOLDER = "outputs/"
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER

# Ensure folders exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)


@app.route("/", methods=["GET"])
def start():
    return render_template("upload.html", view="upload")


@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return redirect(url_for("start"))

    image = request.files["image"]
    if image.filename == "":
        return redirect(url_for("start"))

    filename = secure_filename(image.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    output_path = os.path.join(app.config["OUTPUT_FOLDER"], filename)
    image.save(filepath)

    redact_image(input_path=filepath, output_path=output_path, min_confidence=0.5)

    # Dummy table data
    table_data = [
        {"name": "Item 1", "value": 100},
        {"name": "Item 2", "value": 200},
        {"name": "Item 3", "value": 300},
    ]

    return render_template(
        "display.html",
        view="display",
        image_url=url_for("output_file", filename=filename),
        table_data=table_data,
    )


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/outputs/<filename>")
def output_file(filename):
    return send_from_directory(app.config["OUTPUT_FOLDER"], filename)