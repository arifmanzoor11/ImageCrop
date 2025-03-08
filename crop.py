import os
from flask import Flask, request, render_template, send_file
from PIL import Image
import io
import zipfile

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def clear_processed_folder():
    for filename in os.listdir(PROCESSED_FOLDER):
        file_path = os.path.join(PROCESSED_FOLDER, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

def resize_image(image, target_width, target_height, mode):
    if mode == "Stretch":
        return image.resize((target_width, target_height), Image.LANCZOS)
    else:  # Cover mode
        img_ratio = image.width / image.height
        target_ratio = target_width / target_height

        if img_ratio > target_ratio:
            new_height = target_height
            new_width = int(target_height * img_ratio)
        else:
            new_width = target_width
            new_height = int(target_width / img_ratio)

        image = image.resize((new_width, new_height), Image.LANCZOS)
        left = (new_width - target_width) / 2
        top = (new_height - target_height) / 2
        right = (new_width + target_width) / 2
        bottom = (new_height + target_height) / 2

        return image.crop((left, top, right, bottom))

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        clear_processed_folder()
        files = request.files.getlist('file')
        width = int(request.form.get('width', 100))
        height = int(request.form.get('height', 100))
        format = request.form.get('format', 'PNG').upper()
        mode = request.form.get('mode', 'Cover')
        
        processed_files = []
        
        for file in files:
            if file:
                image = Image.open(file)
                processed_img = resize_image(image, width, height, mode)
                if format == "JPEG" and processed_img.mode == "RGBA":
                    processed_img = processed_img.convert("RGB")
                filename = f"processed_{file.filename.split('.')[0]}.{format.lower()}"
                filepath = os.path.join(PROCESSED_FOLDER, filename)
                processed_img.save(filepath, format=format)
                processed_files.append(filename)
        
        return render_template('download.html', files=processed_files)
    
    return render_template('upload.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(PROCESSED_FOLDER, filename), as_attachment=True)

@app.route('/download_all')
def download_all():
    zip_filename = os.path.join(PROCESSED_FOLDER, "processed_images.zip")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zipf:
        for filename in os.listdir(PROCESSED_FOLDER):
            if filename != "processed_images.zip":  # Exclude previous ZIP files
                file_path = os.path.join(PROCESSED_FOLDER, filename)
                zipf.write(file_path, filename)

    return send_file(zip_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
