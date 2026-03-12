import os
import zipfile
import logging
import time
from datetime import datetime
from flask import Flask, request, render_template, send_file
from PIL import Image
from flask import send_from_directory
from flask import after_this_request

Image.MAX_IMAGE_PIXELS = None

# ---------- CONFIG ----------
AUTO_DELETE_MINUTES = 30

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"

# ---------- LOGGING ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)

logger = logging.getLogger(__name__)

# ---------- APP ----------
app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["PROCESSED_FOLDER"] = PROCESSED_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


# ---------- AUTO CLEANUP ----------
def cleanup_old_files():

    now = time.time()
    expire = AUTO_DELETE_MINUTES * 60

    for folder in [UPLOAD_FOLDER, PROCESSED_FOLDER]:

        for f in os.scandir(folder):

            if f.is_file():

                age = now - os.path.getmtime(f.path)

                if age > expire:
                    try:
                        os.remove(f.path)
                        logger.info(f"Deleted old file: {f.path}")
                    except Exception as e:
                        logger.error(f"Delete failed: {e}")


# ---------- CLEAR PROCESSED ----------
def clear_processed_folder():

    for f in os.scandir(PROCESSED_FOLDER):

        if f.is_file():
            os.remove(f.path)


# ---------- IMAGE RESIZE ----------
def resize_image(image, target_width, target_height, mode):

    if mode == "Stretch":
        return image.resize((target_width, target_height), Image.LANCZOS)

    img_ratio = image.width / image.height
    target_ratio = target_width / target_height

    if img_ratio > target_ratio:
        new_height = target_height
        new_width = int(target_height * img_ratio)
    else:
        new_width = target_width
        new_height = int(target_width / img_ratio)

    image = image.resize((new_width, new_height), Image.LANCZOS)

    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2

    return image.crop((left, top, left + target_width, top + target_height))


# ---------- UPLOAD ----------
@app.route("/", methods=["GET", "POST"])
def upload_file():

    cleanup_old_files()

    if request.method == "POST":

        try:

            logger.info("====== New Image Request ======")

            files = request.files.getlist("file")

            width = int(request.form.get("width", 1200))
            height = int(request.form.get("height", 630))
            format = request.form.get("format", "WEBP").upper()
            mode = request.form.get("mode", "Cover")

            clear_processed_folder()

            processed_files = []

            for file in files:

                if not file:
                    continue

                filename = file.filename

                try:

                    with Image.open(file) as img:

                        img.load()

                        processed_img = resize_image(img, width, height, mode)

                        if format == "JPEG" and processed_img.mode == "RGBA":
                            processed_img = processed_img.convert("RGB")

                        name, _ = os.path.splitext(filename)

                        new_filename = f"{name}.{format.lower()}"

                        path = os.path.join(PROCESSED_FOLDER, new_filename)

                        processed_img.save(path, format=format, optimize=True)

                        processed_img.close()

                        processed_files.append(new_filename)

                        logger.info(f"Processed: {new_filename}")

                except Exception as e:
                    logger.error(f"Image failed: {filename} - {e}")

            return render_template("download.html", files=processed_files)

        except Exception as e:

            logger.error(f"Fatal error: {e}")

            return f"Error: {e}", 500

    return render_template("upload.html")


# ---------- DOWNLOAD SINGLE ----------
@app.route("/processed/<filename>")
def serve_image(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)

@app.route("/download/<filename>")
def download_file(filename):
    path = os.path.join(PROCESSED_FOLDER, filename)
    return send_file(path, as_attachment=True)

# ---------- DOWNLOAD ZIP ----------
@app.route("/download_zip")
def download_zip():

    zip_path = os.path.join(PROCESSED_FOLDER, "images.zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:

        for filename in os.listdir(PROCESSED_FOLDER):

            if filename.lower().endswith((".png",".jpg",".jpeg",".webp",".gif")):

                file_path = os.path.join(PROCESSED_FOLDER, filename)

                zipf.write(file_path, filename)

    @after_this_request
    def remove_zip(response):
        try:
            os.remove(zip_path)
        except Exception as e:
            logger.error(f"Failed to delete zip: {e}")
        return response

    return send_file(zip_path, as_attachment=True)
# ---------- ERROR PAGES ----------
@app.errorhandler(404)
def not_found(error):

    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(error):

    return render_template("500.html"), 500


# ---------- RUN ----------
if __name__ == "__main__":

    logger.info("Starting Image Processor")

    app.run(debug=True, port=3002)