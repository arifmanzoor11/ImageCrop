class ProcessingStatus {
    constructor() {
        this.statusElement = document.getElementById('processingStatus');
        this.progressBar = document.getElementById('processingProgress');
        this.currentFileName = document.getElementById('currentFileName');
    }

    show() {
        this.statusElement.style.display = 'block';
    }

    hide() {
        this.statusElement.style.display = 'none';
    }

    updateProgress(percent, filename) {
        this.progressBar.style.width = percent + '%';
        this.progressBar.textContent = percent + '%';
        this.currentFileName.textContent = filename || '-';
    }

    reset() {
        this.updateProgress(0);
        this.hide();
    }
}