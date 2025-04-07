from setuptools import setup, find_packages

setup(
    name="ImageCrop",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'Pillow',
        'werkzeug',
        # Add other dependencies from your requirements.txt
    ],
    python_requires='>=3.9',
    author="Your Name",
    author_email="your.email@example.com",
    description="A Flask application for image cropping",
    keywords="flask, image, crop",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ],
)