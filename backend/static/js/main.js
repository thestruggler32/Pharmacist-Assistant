// Image upload preview
document.addEventListener('DOMContentLoaded', function () {
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (event) {
                    let preview = document.getElementById('image-preview');
                    if (!preview) {
                        preview = document.createElement('img');
                        preview.id = 'image-preview';
                        preview.className = 'prescription-preview';
                        fileInput.parentElement.appendChild(preview);
                    }
                    preview.src = event.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Drag and drop upload
    const uploadArea = document.querySelector('.upload-area');
    if (uploadArea) {
        uploadArea.addEventListener('dragover', function (e) {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', function (e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', function (e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');

            const files = e.dataTransfer.files;
            if (files.length > 0 && fileInput) {
                fileInput.files = files;
                fileInput.dispatchEvent(new Event('change'));
            }
        });
    }
});

// Validate approval - prevent approval with uncorrected red items
function validateApproval() {
    const redRows = document.querySelectorAll('tr.red');
    if (redRows.length > 0) {
        alert('Please correct all red (low confidence) items before approving.');
        return false;
    }
    return confirm('Are you sure you want to approve this prescription? This action cannot be undone.');
}

// Inline editing helper
function enableInlineEdit(element) {
    element.contentEditable = true;
    element.focus();
    element.style.background = '#fffacd';
}

function disableInlineEdit(element) {
    element.contentEditable = false;
    element.style.background = '';
}

// Auto-save corrections
let saveTimeout;
function autoSaveCorrection(field, value, medicineIndex) {
    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(() => {
        console.log(`Auto-saving ${field} for medicine ${medicineIndex}: ${value}`);
        // AJAX save would go here in production
    }, 1000);
}

// Highlight changes
function highlightChange(element) {
    element.classList.add('changed');
    setTimeout(() => {
        element.classList.remove('changed');
    }, 2000);
}

// Search alternatives
function searchAlternatives(medicineName) {
    const resultsDiv = document.getElementById('alternatives-results');
    if (!resultsDiv) return;

    resultsDiv.innerHTML = '<div class="spinner"></div>';

    fetch(`/alternatives/${encodeURIComponent(medicineName)}`)
        .then(response => response.json())
        .then(data => {
            if (data.alternatives && data.alternatives.length > 0) {
                let html = '';
                data.alternatives.forEach(alt => {
                    html += `
                        <div class="alternative-item">
                            <strong>${alt.brand_name}</strong> - ${alt.strength}
                            <br><small>Generic: ${alt.generic_name}</small>
                        </div>
                    `;
                });
                html += '<div class="alternative-disclaimer">⚠️ Availability not guaranteed. Verify with pharmacy stock.</div>';
                resultsDiv.innerHTML = html;
            } else {
                resultsDiv.innerHTML = '<p>No alternatives found.</p>';
            }
        })
        .catch(error => {
            resultsDiv.innerHTML = '<p class="alert alert-error">Error loading alternatives.</p>';
            console.error('Error:', error);
        });
}

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.style.borderColor = '#dc3545';
            isValid = false;
        } else {
            field.style.borderColor = '#28a745';
        }
    });

    if (!isValid) {
        alert('Please fill in all required fields.');
    }

    return isValid;
}

// Confirmation dialogs
function confirmAction(message) {
    return confirm(message);
}

// Flash message auto-dismiss
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});
