import os
import zipfile
import logging
from datetime import datetime
from flask import Flask, request, render_template, send_file
from PIL import Image

# Configure logging with timestamp and log levels
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console handler
        logging.FileHandler('app.log')  # File handler
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def clear_processed_folder():
    """Removes all files from the processed folder to prevent duplication."""
    for filename in os.listdir(PROCESSED_FOLDER):
        file_path = os.path.join(PROCESSED_FOLDER, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            logger.error(f"Error deleting {file_path}: {e}")

def resize_image(image, target_width, target_height, mode):
    """Resizes the image based on the selected mode."""
    if mode == "Stretch":
        return image.resize((target_width, target_height), Image.LANCZOS)
    
    # Cover mode: Maintain aspect ratio, crop excess
    img_ratio = image.width / image.height
    target_ratio = target_width / target_height

    if img_ratio > target_ratio:
        new_height = target_height
        new_width = int(target_height * img_ratio)
    else:
        new_width = target_width
        new_height = int(target_width / img_ratio)

    image = image.resize((new_width, new_height), Image.LANCZOS)

    # Center cropping
    left = (new_width - target_width) / 2
    top = (new_height - target_height) / 2
    right = (new_width + target_width) / 2
    bottom = (new_height + target_height) / 2

    return image.crop((left, top, right, bottom))


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    """Handles file uploads, processes images, and renders the result page."""
    if request.method == 'POST':
        try:
            # Log request details
            logger.info('====== New Image Processing Request ======')
            logger.info(f'Request received at: {datetime.now()}')
            
            files = request.files.getlist('file')
            total_files = len(files)
            logger.info(f'Number of files: {total_files}')
            
            clear_processed_folder()
            width = int(request.form.get('width', 100))
            height = int(request.form.get('height', 100))
            format = request.form.get('format', 'PNG').upper()
            mode = request.form.get('mode', 'Cover')
            
            processed_files = []

            for index, file in enumerate(files, 1):
                if file:
                    filename = file.filename
                    logger.info(f'Processing file: {filename}')
                    try:
                        image = Image.open(file)
                        processed_img = resize_image(image, width, height, mode)

                        if format == "JPEG" and processed_img.mode == "RGBA":
                            processed_img = processed_img.convert("RGB")

                        original_name, _ = os.path.splitext(file.filename)
                        filename = f"{original_name}.{format.lower()}"

                        filepath = os.path.join(PROCESSED_FOLDER, filename)
                        processed_img.save(filepath, format=format)
                        processed_files.append(filename)
                        logger.info(f'Successfully processed: {filename}')
                        
                    except Exception as e:
                        logger.error(f'Error processing {filename}: {str(e)}')
                        raise

            logger.info('====== Request Processing Completed ======\n')
            return render_template('download.html', files=processed_files)

        except Exception as e:
            logger.error(f'Fatal error: {str(e)}')
            return f'Error: {str(e)}', 500

    return render_template('upload.html')

@app.route('/download/<filename>')
def download_file(filename):
    """Allows individual processed files to be downloaded."""
    return send_file(os.path.join(PROCESSED_FOLDER, filename), as_attachment=True)

@app.route('/download_all', methods=['GET', 'POST'])
def download_all():
    if request.method == 'POST':
        try:
            # Create a timestamp for unique zip name
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            zip_filename = f'processed_images_{timestamp}.zip'
            zip_path = os.path.join(app.config['UPLOAD_FOLDER'], zip_filename)

            # Create ZIP file
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for filename in os.listdir(app.config['UPLOAD_FOLDER']):
                    if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        zipf.write(file_path, filename)

            # Send file and delete after sending
            return send_file(
                zip_path,
                as_attachment=True,
                download_name=zip_filename
            )
        except Exception as e:
            return f"Error creating zip file: {str(e)}", 500
    
    # GET request - show download page
    images = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            images.append(filename)
    return render_template('download.html', images=images)

@app.route('/download_zip')
def download_zip():
    """Creates and provides a ZIP file of all processed images."""
    zip_filename = os.path.join(PROCESSED_FOLDER, "processed_images.zip")

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zipf:
        for filename in os.listdir(PROCESSED_FOLDER):
            if filename != "processed_images.zip":  # Exclude previous ZIP files
                file_path = os.path.join(PROCESSED_FOLDER, filename)
                zipf.write(file_path, filename)

    return send_file(zip_filename, as_attachment=True)

# Add error handlers
@app.errorhandler(404)
def not_found_error(error):
    logger.error(f'Page not found: {request.url}')
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f'Server Error: {str(error)}')
    return render_template('500.html'), 500

if __name__ == '__main__':
    logger.info('Starting Image Cropper Application...')
    app.run(debug=True, port=3002)