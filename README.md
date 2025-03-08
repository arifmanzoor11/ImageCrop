# Image Cropper Webapp
# Image Cropper Webapp

## Overview
The **Image Cropper Webapp** is a simple and efficient Flask-based web application that allows users to upload images, resize them using two different modes (Stretch or Cover), and download the processed images in various formats.

## Features
- Upload multiple images at once.
- Resize images with two options:
  - **Stretch**: Forces the image to fit the target dimensions.
  - **Cover**: Maintains aspect ratio while covering the entire target area.
- Supports multiple image formats (PNG, JPEG, etc.).
- Automatically clears old processed images before each new upload.
- Download individual processed images.
- Download all processed images as a ZIP file.

## Installation

### Prerequisites
Ensure you have Python installed on your system. You can check by running:
```sh
python --version
```

### Setup Steps
1. Clone this repository:
   ```sh
   git clone https://github.com/your-repo/image-cropper-webapp.git
   cd image-cropper-webapp
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the application:
   ```sh
   python app.py
   ```
4. Open your web browser and visit:
   ```
   http://127.0.0.1:5000
   ```

## Usage
1. Upload images via the web interface.
2. Select the width, height, format, and resize mode.
3. Click **Submit** to process images.
4. Download individual images or all processed images as a ZIP file.

## Folder Structure
```
image-cropper-webapp/
│── app.py              # Main Flask application
│── templates/
│   ├── upload.html     # Upload page template
│   ├── download.html   # Download page template
│── static/             # Static assets (CSS, JS)
│── uploads/            # Stores uploaded images
│── processed/          # Stores processed images
│── requirements.txt    # Required dependencies
│── README.md           # Project documentation
```

## Dependencies
The app requires the following Python libraries:
```sh
Flask
Pillow
zipfile
```
Install them using:
```sh
pip install Flask Pillow
```

## License
This project is licensed under the MIT License.

## Contributing
Feel free to submit issues and pull requests if you have any improvements or bug fixes!

## Author
Arif M.