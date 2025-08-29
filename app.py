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

UPLOAD_FOLDER = "uploads/"
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


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
    image.save(filepath)

    # Dummy table data
    table_data = [
        {"name": "Item 1", "value": 100},
        {"name": "Item 2", "value": 200},
        {"name": "Item 3", "value": 300},
    ]

    return render_template(
        "display.html",
        view="display",
        image_url=url_for("uploaded_file", filename=filename),
        table_data=table_data,
    )


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
