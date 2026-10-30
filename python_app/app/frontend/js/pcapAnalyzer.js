import { showLoadingMessage, showErrorMessage, showSuccessMessage } from './modal.js';

let analysisInProgress = false;

export function isAnalysisInProgress() {
    return analysisInProgress;
}

export async function analyzePcap(file) {
    if (analysisInProgress) return;
    analysisInProgress = true;
    const fileInput = document.getElementById('pcapFile');
    const dropZone = document.getElementById('dropZone');
    const uploadStatus = document.getElementById('uploadStatus');
    fileInput.disabled = true;
    dropZone.setAttribute('aria-busy', 'true');
    dropZone.classList.remove('drag-over');
    uploadStatus.textContent = `Analyzing ${file.name}…`;
    try {
        showLoadingMessage();
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetch('/analyze-network', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error analyzing file');
        }

        const result = await response.json();
        showSuccessMessage(result);
    } catch (error) {
        console.error('Error analyzing:', error);
        showErrorMessage(error.message || 'Error occurred while analyzing the file');
    } finally {
        analysisInProgress = false;
        fileInput.disabled = false;
        dropZone.removeAttribute('aria-busy');
        uploadStatus.textContent = '';
    }
}
