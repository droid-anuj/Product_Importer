/**
 * CSV Upload Module
 */

let currentUploadTaskId = null;
let progressCheckInterval = null;

document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadForm = document.getElementById('upload-form');

    if (dropZone) {
        dropZone.addEventListener('click', () => fileInput?.click());

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('border-blue-500', 'bg-blue-50');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('border-blue-500', 'bg-blue-50');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('border-blue-500', 'bg-blue-50');

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileSelect(files[0]);
            }
        });
    }

    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });
    }

    if (uploadForm) {
        uploadForm.addEventListener('submit', (e) => {
            e.preventDefault();
            submitUpload();
        });
    }
});

function handleFileSelect(file) {
    if (!file.name.endsWith('.csv')) {
        alert('⚠️  Please select a CSV file');
        return;
    }

    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');
    const uploadBtn = document.getElementById('upload-btn');

    if (fileInfo && fileName && fileSize && uploadBtn) {
        fileName.textContent = file.name;
        fileSize.textContent = `Size: ${(file.size / 1024).toFixed(2)} KB`;
        fileInfo.classList.remove('hidden');
        uploadBtn.disabled = false;

        // Store file for upload
        document.getElementById('file-input').files = new DataTransfer().items.add(file).files;
    }
}

async function submitUpload() {
    const fileInput = document.getElementById('file-input');
    const file = fileInput?.files?.[0];

    if (!file) {
        alert('⚠️  Please select a file');
        return;
    }

    try {
        const uploadBtn = document.getElementById('upload-btn');
        if (uploadBtn) uploadBtn.disabled = true;

        // Upload file
        const response = await API.upload.csv(file);
        currentUploadTaskId = response.task_id;

        // Show progress section
        const progressSection = document.getElementById('progress-section');
        if (progressSection) {
            progressSection.classList.remove('hidden');
        }

        // Start polling for progress
        pollProgress();
    } catch (error) {
        console.error('Upload error:', error);
        alert(`❌ Upload error: ${error.message}`);
        const uploadBtn = document.getElementById('upload-btn');
        if (uploadBtn) uploadBtn.disabled = false;
    }
}

async function pollProgress() {
    if (!currentUploadTaskId) return;

    if (progressCheckInterval) clearInterval(progressCheckInterval);

    progressCheckInterval = setInterval(async () => {
        try {
            const progress = await API.upload.progress(currentUploadTaskId);

            updateProgressUI(progress);

            if (progress.status === 'completed' || progress.status === 'failed') {
                clearInterval(progressCheckInterval);

                if (progress.status === 'completed') {
                    showCompletionModal(progress);
                } else {
                    showErrorModal(progress.error || 'Unknown error');
                }

                // Reset form after showing modal
                setTimeout(() => {
                    document.getElementById('upload-form').reset();
                    document.getElementById('file-info').classList.add('hidden');
                    document.getElementById('progress-section').classList.add('hidden');

                    const uploadBtn = document.getElementById('upload-btn');
                    if (uploadBtn) uploadBtn.disabled = true;

                    currentUploadTaskId = null;

                    // Reload products
                    loadProducts();
                }, 500);
            }
        } catch (error) {
            console.error('Progress check error:', error);
        }
    }, 1000);
}

function showCompletionModal(progress) {
    const modal = document.getElementById('completion-modal');
    if (!modal) return;

    // Update modal content
    document.getElementById('modal-created').textContent = progress.created_products || 0;
    document.getElementById('modal-updated').textContent = progress.updated_products || 0;
    document.getElementById('modal-failed').textContent = progress.failed_products || 0;

    // Show modal
    modal.classList.remove('hidden');
    modal.classList.add('flex');

    // Close modal on button click
    const closeBtn = document.getElementById('close-completion-modal');
    const okBtn = document.getElementById('completion-ok-btn');

    const closeModal = () => {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    };

    if (closeBtn) closeBtn.onclick = closeModal;
    if (okBtn) okBtn.onclick = closeModal;
}

function showErrorModal(errorMessage) {
    const modal = document.getElementById('error-modal');
    if (!modal) return;

    document.getElementById('error-message-text').textContent = errorMessage;

    modal.classList.remove('hidden');
    modal.classList.add('flex');

    const closeBtn = document.getElementById('close-error-modal');
    const okBtn = document.getElementById('error-ok-btn');

    const closeModal = () => {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    };

    if (closeBtn) closeBtn.onclick = closeModal;
    if (okBtn) okBtn.onclick = closeModal;
}

function updateProgressUI(progress) {
    const progressBar = document.getElementById('progress-bar');
    const progressPercent = document.getElementById('progress-percent');
    const totalRows = document.getElementById('total-rows');
    const processedRows = document.getElementById('processed-rows');
    const createdCount = document.getElementById('created-count');
    const updatedCount = document.getElementById('updated-count');
    const statusText = document.getElementById('status-text');

    if (progressBar && progress.total_rows > 0) {
        const percent = Math.round((progress.processed_rows / progress.total_rows) * 100);
        progressBar.style.width = percent + '%';

        if (progressPercent) {
            progressPercent.textContent = percent + '%';
        }
    }

    if (totalRows) totalRows.textContent = progress.total_rows || 0;
    if (processedRows) processedRows.textContent = progress.processed_rows || 0;
    if (createdCount) createdCount.textContent = progress.created_products || 0;
    if (updatedCount) updatedCount.textContent = progress.updated_products || 0;

    if (statusText) {
        const statusMap = {
            pending: '⏳ Waiting to start...',
            processing: '⚙️  Processing CSV...',
            completed: '✓ Upload completed!',
            failed: '❌ Upload failed',
        };
        statusText.textContent = statusMap[progress.status] || progress.status || 'Processing...';
    }
}
