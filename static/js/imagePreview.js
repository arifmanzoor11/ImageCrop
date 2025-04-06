function createImagePreview(file) {
    const reader = new FileReader();
    const preview = document.createElement('div');
    preview.className = 'preview-item';
    
    reader.onload = function(e) {
        preview.innerHTML = `
            <img src="${e.target.result}" class="preview-image" alt="${file.name}">
            <span class="filename">${file.name}</span>
        `;
    };
    
    reader.readAsDataURL(file);
    return preview;
}

function updateImagePreviews(files) {
    const previewContainer = document.getElementById('imagePreviewContainer');
    previewContainer.innerHTML = '';
    
    Array.from(files).forEach(file => {
        const preview = createImagePreview(file);
        previewContainer.appendChild(preview);
    });
    
    initializeSlider();
}

function initializeSlider() {
    const container = document.getElementById('imagePreviewContainer');
    const items = container.querySelectorAll('.preview-item');
    
    if (items.length > 6) { // Show slider if more than 6 images
        new Slick(container, {
            dots: true,
            infinite: false,
            speed: 300,
            slidesToShow: 3,
            slidesToScroll: 3,
            rows: 2,
            responsive: [
                {
                    breakpoint: 768,
                    settings: {
                        slidesToShow: 2,
                        slidesToScroll: 2,
                        rows: 2
                    }
                }
            ]
        });
    }
}