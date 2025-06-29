// Global variables
let stream = null;
let currentStep = 1;
let knownImageData = null;
let newImageData = null;

const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const startCameraBtn = document.getElementById('startCamera');
const captureBtn = document.getElementById('captureBtn');
const stopCameraBtn = document.getElementById('stopCamera');
const verifyBtn = document.getElementById('verifyBtn');
const knownFileInput = document.getElementById('knownFileInput');
const newFileInput = document.getElementById('newFileInput');

const cameraStatus = document.getElementById('cameraStatus');
const knownImageStatus = document.getElementById('knownImageStatus');
const newImageStatus = document.getElementById('newImageStatus');

const verificationResult = document.getElementById('verificationResult');
const resultIcon = document.getElementById('resultIcon');
const resultMessage = document.getElementById('resultMessage');
const resultDetails = document.getElementById('resultDetails');

const loadingOverlay = document.getElementById('loadingOverlay');
const loadingMessage = document.getElementById('loadingMessage');

document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    updateStepIndicator();
    updateVerifyButton();
    checkNetworkAccess();
});

function initializeEventListeners() {
    startCameraBtn.addEventListener('click', startCamera);
    captureBtn.addEventListener('click', captureImage);
    stopCameraBtn.addEventListener('click', stopCamera);
    verifyBtn.addEventListener('click', verifyFaces);
    
    knownFileInput.addEventListener('change', handleKnownFileUpload);
    newFileInput.addEventListener('change', handleNewFileUpload);
}

async function startCamera() {
    try {
        showLoading('Starting camera...');
        
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            throw new Error('Camera API not supported in this browser');
        }
        
        const isRemoteAccess = !window.location.hostname.includes('localhost') && 
                              !window.location.hostname.includes('127.0.0.1');
        
        if (isRemoteAccess) {
            showRemoteAccessWarning();
            return;
        }
        
        const constraints = {
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user'
            }
        };
        
        stream = await navigator.mediaDevices.getUserMedia(constraints);
        video.srcObject = stream;
        
        startCameraBtn.disabled = true;
        captureBtn.disabled = false;
        stopCameraBtn.disabled = false;
        
        cameraStatus.textContent = 'Camera: Active';
        cameraStatus.style.color = '#4CAF50';
        
        hideLoading();
        
        video.addEventListener('loadedmetadata', () => {
            console.log('Camera started successfully');
        });
        
    } catch (error) {
        console.error('Error starting camera:', error);
        hideLoading();
        
        let errorMessage = 'Error starting camera. ';
        
        if (error.name === 'NotAllowedError') {
            errorMessage += 'Camera permission denied. Please allow camera access in your browser settings and refresh the page.';
            showCameraPermissionHelp();
        } else if (error.name === 'NotFoundError') {
            errorMessage += 'No camera found. Please connect a camera and try again.';
        } else if (error.name === 'NotSupportedError') {
            errorMessage += 'Camera not supported in this browser. Please use Chrome, Firefox, or Safari.';
        } else if (error.name === 'NotReadableError') {
            errorMessage += 'Camera is in use by another application. Please close other camera apps and try again.';
        } else {
            errorMessage += 'Please check camera permissions and try again.';
        }
        
        showNotification(errorMessage, 'error');
        cameraStatus.textContent = 'Camera: Error';
        cameraStatus.style.color = '#f44336';
    }
}

function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    
    video.srcObject = null;
    
    startCameraBtn.disabled = false;
    captureBtn.disabled = true;
    stopCameraBtn.disabled = true;
    
    cameraStatus.textContent = 'Camera: Stopped';
    cameraStatus.style.color = '#666';
}

function captureImage(callback) {
    if (!stream) {
        showNotification('Camera not started', 'error');
        return;
    }
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL('image/jpeg', 0.8);
    if (typeof callback === 'function') {
        callback(imageData);
    }
}

function handleKnownFaceCapture(imageData) {
    knownImageData = imageData;
    displayImage('knownImageContainer', imageData);
    knownImageStatus.textContent = 'Known Face: Captured';
    knownImageStatus.style.color = '#4CAF50';
    currentStep = 2;
    updateStepIndicator();
    showNotification('Known face captured successfully!', 'success');
}

function handleNewFaceCapture(imageData) {
    newImageData = imageData;
    displayImage('newImageContainer', imageData);
    newImageStatus.textContent = 'New Face: Captured';
    newImageStatus.style.color = '#4CAF50';
    currentStep = 3;
    updateStepIndicator();
    updateVerifyButton();
    showNotification('New face captured successfully!', 'success');
}

function handleKnownFileUpload(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            knownImageData = e.target.result;
            displayImage('knownImageContainer', knownImageData);
            knownImageStatus.textContent = 'Known Face: Uploaded';
            knownImageStatus.style.color = '#4CAF50';
            
            currentStep = 2;
            updateStepIndicator();
            showNotification('Known face uploaded successfully!', 'success');
        };
        reader.readAsDataURL(file);
    }
}

function handleNewFileUpload(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            newImageData = e.target.result;
            displayImage('newImageContainer', newImageData);
            newImageStatus.textContent = 'New Face: Uploaded';
            newImageStatus.style.color = '#4CAF50';
            
            currentStep = 3;
            updateStepIndicator();
            updateVerifyButton();
            showNotification('New face uploaded successfully!', 'success');
        };
        reader.readAsDataURL(file);
    }
}

function displayImage(containerId, imageData) {
    const container = document.getElementById(containerId);
    container.innerHTML = `<img src="${imageData}" alt="Captured face">`;
}

async function verifyFaces() {
    if (!knownImageData || !newImageData) {
        showNotification('Please capture both images first', 'error');
        return;
    }
    
    showLoading('Verifying faces...');
    
    try {
        const response = await fetch('/verify/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                known_image: knownImageData,
                new_image: newImageData
            })
        });
        
        const result = await response.json();
        
        hideLoading();
        
        if (result.success) {
            showVerificationResult(result.verified, result.message, result.embedding_saved);
        } else {
            showNotification(result.error || 'Verification failed', 'error');
        }
        
    } catch (error) {
        console.error('Verification error:', error);
        hideLoading();
        showNotification('Network error during verification', 'error');
    }
}

function showVerificationResult(verified, message, embeddingSaved) {
    verificationResult.style.display = 'block';
    
    if (verified) {
        resultIcon.className = 'fas fa-check-circle success';
        resultMessage.textContent = 'Verification Successful!';
        resultMessage.style.color = '#4CAF50';
        
        let details = message;
        if (embeddingSaved) {
            details += ' Face embedding has been saved.';
        }
        resultDetails.textContent = details;
        
        showNotification('Faces match! Verification successful.', 'success');
    } else {
        resultIcon.className = 'fas fa-times-circle error';
        resultMessage.textContent = 'Verification Failed';
        resultMessage.style.color = '#f44336';
        resultDetails.textContent = message;
        
        showNotification('Faces do not match. Please try again.', 'error');
    }
}

function updateStepIndicator() {
    const steps = document.querySelectorAll('.step');
    steps.forEach((step, index) => {
        if (index + 1 <= currentStep) {
            step.classList.add('active');
        } else {
            step.classList.remove('active');
        }
    });
}

function updateVerifyButton() {
    verifyBtn.disabled = !(knownImageData && newImageData);
}

function showLoading(message = 'Processing...') {
    loadingMessage.textContent = message;
    loadingOverlay.style.display = 'flex';
}

function hideLoading() {
    loadingOverlay.style.display = 'none';
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1001;
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: 500;
        animation: slideIn 0.3s ease-out;
    `;
    
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

window.captureKnownFace = function() {
    if (currentStep === 1) {
        captureImage(handleKnownFaceCapture);
    } else {
        showNotification('Please complete the current step first', 'error');
    }
};

window.captureNewFace = function() {
    if (currentStep === 2) {
        captureImage(handleNewFaceCapture);
    } else {
        showNotification('Please capture the known face first', 'error');
    }
};

window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    showNotification('An unexpected error occurred', 'error');
});

window.addEventListener('beforeunload', function() {
    stopCamera();
});

// Show camera permission help
function showCameraPermissionHelp() {
    const helpDiv = document.createElement('div');
    helpDiv.className = 'camera-help';
    helpDiv.innerHTML = `
        <div class="help-content">
            <h3>🔒 Camera Permission Required</h3>
            <p>To use the camera, you need to allow camera access in your browser.</p>
            <div class="browser-instructions">
                <h4>How to enable camera access:</h4>
                <div class="browser-section">
                    <strong>Chrome/Edge:</strong>
                    <ul>
                        <li>Click the camera icon in the address bar</li>
                        <li>Select "Allow" for camera access</li>
                        <li>Refresh the page</li>
                    </ul>
                </div>
                <div class="browser-section">
                    <strong>Firefox:</strong>
                    <ul>
                        <li>Click the camera icon in the address bar</li>
                        <li>Select "Allow" for camera access</li>
                        <li>Refresh the page</li>
                    </ul>
                </div>
                <div class="browser-section">
                    <strong>Safari:</strong>
                    <ul>
                        <li>Go to Safari > Preferences > Websites > Camera</li>
                        <li>Allow camera access for this website</li>
                        <li>Refresh the page</li>
                    </ul>
                </div>
            </div>
            <div class="help-actions">
                <button onclick="this.parentElement.parentElement.parentElement.remove()" class="btn btn-primary">
                    Got it, I'll fix permissions
                </button>
                <button onclick="tryAlternativeMethod()" class="btn btn-outline">
                    Try Alternative Method
                </button>
            </div>
        </div>
    `;
    
    // Add styles
    helpDiv.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1002;
        padding: 20px;
    `;
    
    document.body.appendChild(helpDiv);
}

// Alternative method - try different camera constraints
async function tryAlternativeMethod() {
    try {
        showLoading('Trying alternative camera settings...');
       
        const basicConstraints = {
            video: true
        };
        
        stream = await navigator.mediaDevices.getUserMedia(basicConstraints);
        video.srcObject = stream;
        
        startCameraBtn.disabled = true;
        captureBtn.disabled = false;
        stopCameraBtn.disabled = false;
        
        cameraStatus.textContent = 'Camera: Active (Basic Mode)';
        cameraStatus.style.color = '#4CAF50';
        
        hideLoading();
        showNotification('Camera started with basic settings!', 'success');
        
        const helpDialog = document.querySelector('.camera-help');
        if (helpDialog) {
            helpDialog.remove();
        }
        
    } catch (error) {
        console.error('Alternative method failed:', error);
        hideLoading();
        showNotification('Alternative method also failed. Please check camera permissions manually.', 'error');
        showCameraTroubleshooting();
    }
}

// Show camera troubleshooting section
function showCameraTroubleshooting() {
    const troubleshooting = document.querySelector('.camera-troubleshooting');
    if (troubleshooting) {
        troubleshooting.style.display = 'block';
    }
}

// Show camera help (reusable function)
function showCameraHelp() {
    showCameraPermissionHelp();
}

// Enable upload mode when camera fails
function enableUploadMode() {
    // Hide camera section
    const cameraSection = document.querySelector('.camera-section');
    if (cameraSection) {
        cameraSection.style.display = 'none';
    }
    
    // Show enhanced upload instructions
    showUploadInstructions();
    
    // Update status
    cameraStatus.textContent = 'Camera: Using Upload Mode';
    cameraStatus.style.color = '#2196F3';
    
    showNotification('Upload mode enabled! You can now upload images instead of using the camera.', 'success');
}

// Show upload instructions
function showUploadInstructions() {
    const instructionsDiv = document.createElement('div');
    instructionsDiv.className = 'upload-instructions';
    instructionsDiv.innerHTML = `
        <div class="instructions-content">
            <h3><i class="fas fa-upload"></i> Upload Mode Active</h3>
            <p>Since camera access is not available, you can upload images from your device.</p>
            <div class="upload-steps">
                <div class="step-item">
                    <div class="step-number">1</div>
                    <div class="step-text">
                        <strong>Upload Known Face:</strong> Click "Upload" in the Known Face section and select an image
                    </div>
                </div>
                <div class="step-item">
                    <div class="step-number">2</div>
                    <div class="step-text">
                        <strong>Upload New Face:</strong> Click "Upload" in the New Face section and select an image
                    </div>
                </div>
                <div class="step-item">
                    <div class="step-number">3</div>
                    <div class="step-text">
                        <strong>Verify Faces:</strong> Click "Verify Faces" to compare the uploaded images
                    </div>
                </div>
            </div>
            <div class="upload-tips">
                <h4>Tips for better results:</h4>
                <ul>
                    <li>Use clear, well-lit photos</li>
                    <li>Ensure faces are clearly visible</li>
                    <li>Use similar angles for both images</li>
                    <li>Supported formats: JPG, PNG, GIF</li>
                </ul>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" class="btn btn-primary">
                Got it, let's start!
            </button>
        </div>
    `;
    
    // Add styles
    instructionsDiv.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1002;
        padding: 20px;
    `;
    
    document.body.appendChild(instructionsDiv);
}

// Enhanced error handling for camera
function handleCameraError(error) {
    console.error('Camera error:', error);
    
    if (error.name === 'NotAllowedError') {
        showCameraPermissionHelp();
    } else if (error.name === 'NotFoundError') {
        showNotification('No camera found. Please connect a camera or use upload mode.', 'error');
        showCameraTroubleshooting();
    } else if (error.name === 'NotSupportedError') {
        showNotification('Camera not supported in this browser. Please use upload mode.', 'error');
        showCameraTroubleshooting();
    } else {
        showNotification('Camera error occurred. Please try upload mode instead.', 'error');
        showCameraTroubleshooting();
    }
}

// Show remote access warning
function showRemoteAccessWarning() {
    hideLoading();
    
    const warningDiv = document.createElement('div');
    warningDiv.className = 'remote-access-warning';
    warningDiv.innerHTML = `
        <div class="warning-content">
            <h3><i class="fas fa-exclamation-triangle"></i> Remote Access Detected</h3>
            <p>You're accessing this application from a remote device (${window.location.hostname}).</p>
            <div class="warning-details">
                <h4>Why camera might not work:</h4>
                <ul>
                    <li>Browsers restrict camera access for security on non-localhost connections</li>
                    <li>HTTPS is required for camera access on remote connections</li>
                    <li>Some browsers block camera access entirely on non-secure connections</li>
                </ul>
            </div>
            <div class="solution-options">
                <h4>Solutions:</h4>
                <div class="solution-item">
                    <strong>Option 1: Use Upload Mode (Recommended)</strong>
                    <p>Upload images from your device instead of using the camera</p>
                    <button onclick="enableUploadMode()" class="btn btn-primary">
                        <i class="fas fa-upload"></i> Enable Upload Mode
                    </button>
                </div>
                <div class="solution-item">
                    <strong>Option 2: Access via localhost</strong>
                    <p>Access the application directly on the server machine using localhost</p>
                    <code>http://localhost:5001</code>
                </div>
                <div class="solution-item">
                    <strong>Option 3: Try camera anyway</strong>
                    <p>Some browsers might allow camera access with proper permissions</p>
                    <button onclick="tryCameraAnyway()" class="btn btn-outline">
                        <i class="fas fa-camera"></i> Try Camera
                    </button>
                </div>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" class="btn btn-secondary">
                Close
            </button>
        </div>
    `;
    
    // Add styles
    warningDiv.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1002;
        padding: 20px;
    `;
    
    document.body.appendChild(warningDiv);
}

// Try camera anyway (for remote access)
async function tryCameraAnyway() {
    try {
        showLoading('Attempting camera access...');
        
        const constraints = {
            video: true
        };
        
        stream = await navigator.mediaDevices.getUserMedia(constraints);
        video.srcObject = stream;
        
        startCameraBtn.disabled = true;
        captureBtn.disabled = false;
        stopCameraBtn.disabled = false;
        
        cameraStatus.textContent = 'Camera: Active (Remote)';
        cameraStatus.style.color = '#4CAF50';
        
        hideLoading();
        showNotification('Camera started successfully!', 'success');
        
        // Remove warning dialog
        const warningDialog = document.querySelector('.remote-access-warning');
        if (warningDialog) {
            warningDialog.remove();
        }
        
    } catch (error) {
        console.error('Camera failed on remote access:', error);
        hideLoading();
        showNotification('Camera access failed. Please use upload mode instead.', 'error');
        enableUploadMode();
    }
}

// Check network access type
function checkNetworkAccess() {
    const isRemoteAccess = !window.location.hostname.includes('localhost') && 
                          !window.location.hostname.includes('127.0.0.1');
    
    const networkStatus = document.getElementById('networkStatus');
    const networkStatusText = document.getElementById('networkStatusText');
    
    if (isRemoteAccess) {
        networkStatus.className = 'network-status remote';
        networkStatusText.textContent = `Remote Access (${window.location.hostname})`;
        networkStatus.style.display = 'flex';
        
        // Show a notification about remote access
        setTimeout(() => {
            showNotification('Remote access detected. Camera may have limited functionality.', 'info');
        }, 2000);
    } else {
        networkStatus.className = 'network-status local';
        networkStatusText.textContent = 'Local Access';
        networkStatus.style.display = 'flex';
    }
} 