/**
 * StegoLLM Web UI JavaScript
 * Handles interactions and dynamic updates for the StegoLLM web interface.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Update status indicator based on compression status
    updateStatusIndicator();
    
    // Periodically update statistics
    setInterval(updateStatistics, 5000);
    
    // Initialize tooltips
    initializeTooltips();
});

/**
 * Updates the status indicator light and text based on the current compression status
 */
function updateStatusIndicator() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            const statusLight = document.getElementById('status-light');
            const statusText = document.getElementById('status-text');
            
            if (statusLight && statusText) {
                if (data.compression_enabled) {
                    statusLight.className = 'status-light status-active';
                    statusText.textContent = 'Compression Active';
                } else {
                    statusLight.className = 'status-light status-inactive';
                    statusText.textContent = 'Compression Inactive';
                }
            }
        })
        .catch(error => console.error('Error updating status:', error));
}

/**
 * Periodically updates statistics on the dashboard
 */
function updateStatistics() {
    // Only update statistics if we're on the dashboard page
    const compressionChart = document.getElementById('compression-chart');
    if (!compressionChart) return;
    
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            // Update metrics
            updateElementText('requests-count', data.metrics.requests);
            updateElementText('original-size', `${data.metrics.original_size} chars`);
            updateElementText('compressed-size', `${data.metrics.compressed_size} chars`);
            
            const savedChars = data.metrics.original_size - data.metrics.compressed_size;
            updateElementText('saved-chars', `${savedChars} chars`);
            
            let ratio = 0;
            if (data.metrics.original_size > 0) {
                ratio = (savedChars / data.metrics.original_size) * 100;
            }
            updateElementText('compression-ratio', `${ratio.toFixed(2)}%`);
            
            // Update chart if it exists
            if (compressionChart && window.compressionChartObj) {
                window.compressionChartObj.data.datasets[0].data = [
                    data.metrics.original_size,
                    data.metrics.compressed_size,
                    savedChars
                ];
                window.compressionChartObj.update();
            }
        })
        .catch(error => console.error('Error updating statistics:', error));
}

/**
 * Updates the text content of an element if it exists
 */
function updateElementText(id, text) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = text;
    }
}

/**
 * Initializes tooltip elements
 */
function initializeTooltips() {
    // Add tooltip functionality if needed
    const tooltips = document.querySelectorAll('[data-tooltip]');
    
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseenter', function() {
            const tooltipText = this.getAttribute('data-tooltip');
            const tooltipEl = document.createElement('div');
            tooltipEl.className = 'tooltip';
            tooltipEl.textContent = tooltipText;
            
            document.body.appendChild(tooltipEl);
            
            const rect = this.getBoundingClientRect();
            tooltipEl.style.top = `${rect.bottom + window.scrollY + 5}px`;
            tooltipEl.style.left = `${rect.left + window.scrollX}px`;
        });
        
        tooltip.addEventListener('mouseleave', function() {
            const tooltips = document.querySelectorAll('.tooltip');
            tooltips.forEach(t => t.remove());
        });
    });
}

/**
 * Shows an alert message to the user
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    // Add close button
    const closeButton = document.createElement('button');
    closeButton.className = 'close-alert';
    closeButton.innerHTML = '&times;';
    closeButton.addEventListener('click', function() {
        alertDiv.remove();
    });
    
    alertDiv.appendChild(closeButton);
    alertContainer.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

/**
 * Handles form submission with AJAX
 */
function submitForm(formId, url, successCallback) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const formData = new FormData(form);
        const jsonData = {};
        
        formData.forEach((value, key) => {
            // Handle checkboxes
            if (form.elements[key].type === 'checkbox') {
                jsonData[key] = form.elements[key].checked;
            } else {
                jsonData[key] = value;
            }
        });
        
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(jsonData),
        })
        .then(response => response.json())
        .then(data => {
            if (successCallback) {
                successCallback(data);
            } else {
                showAlert('Settings saved successfully', 'success');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Error saving settings', 'danger');
        });
    });
}