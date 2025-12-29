// Remote PC Control - Frontend JavaScript

const API_BASE = window.location.origin;
let videoInterval = null;
let fpsCounter = 0;
let lastFpsTime = Date.now();

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupVideoFeed();
    setupMouseControl();
    setupKeyboardControl();
    checkPicoStatus();
});

function initializeApp() {
    console.log('Remote PC Control initialized');
    updateStatus('pico-status', 'Checking...', 'disconnected');
    updateStatus('video-status', 'Starting...', 'disconnected');
}

function updateStatus(elementId, text, status) {
    const element = document.getElementById(elementId);
    const parts = text.split(':');
    element.textContent = parts[0] + ': ' + parts[1];
    element.className = `status-badge ${status}`;
}

// Video Feed
function setupVideoFeed() {
    const videoFeed = document.getElementById('video-feed');

    // Start video stream
    videoInterval = setInterval(() => {
        const timestamp = new Date().getTime();
        videoFeed.src = `${API_BASE}/video_feed?t=${timestamp}`;

        // FPS counter
        fpsCounter++;
        const now = Date.now();
        if (now - lastFpsTime >= 1000) {
            document.getElementById('fps').textContent = fpsCounter + ' fps';
            fpsCounter = 0;
            lastFpsTime = now;
        }
    }, 100); // 10 fps refresh

    videoFeed.onload = () => {
        updateStatus('video-status', 'Video: Active', 'connected');
        document.getElementById('video-res').textContent = `${videoFeed.naturalWidth}x${videoFeed.naturalHeight}`;
    };

    videoFeed.onerror = () => {
        updateStatus('video-status', 'Video: Error', 'disconnected');
    };
}

// Mouse Control
function setupMouseControl() {
    const videoContainer = document.querySelector('.video-container');
    const mouseCursor = document.getElementById('mouse-cursor');
    const mouseEnabled = document.getElementById('mouse-enabled');

    videoContainer.addEventListener('click', (e) => {
        if (!mouseEnabled.checked) return;

        const rect = videoContainer.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width * 100).toFixed(2);
        const y = ((e.clientY - rect.top) / rect.height * 100).toFixed(2);

        // Show cursor position
        mouseCursor.style.left = `${e.clientX - rect.left}px`;
        mouseCursor.style.top = `${e.clientY - rect.top}px`;
        mouseCursor.style.display = 'block';
        setTimeout(() => mouseCursor.style.display = 'none', 500);

        // Send mouse move and click
        sendMouseMove(parseFloat(x), parseFloat(y));
        setTimeout(() => sendMouseClick('left'), 50);
    });
}

function sendMouseMove(x, y) {
    fetch(`${API_BASE}/mouse_move`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ x, y })
    })
    .then(res => res.json())
    .then(data => console.log('Mouse moved:', data))
    .catch(err => console.error('Mouse move error:', err));
}

function sendMouseClick(button) {
    fetch(`${API_BASE}/mouse_click`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ button })
    })
    .then(res => res.json())
    .then(data => console.log('Mouse clicked:', data))
    .catch(err => console.error('Mouse click error:', err));
}

// Keyboard Control
function setupKeyboardControl() {
    const textInput = document.getElementById('text-input');

    textInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendText();
        }
    });
}

function sendText() {
    const textInput = document.getElementById('text-input');
    const text = textInput.value;

    if (!text) return;

    fetch(`${API_BASE}/type_text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
    })
    .then(res => res.json())
    .then(data => {
        console.log('Text sent:', data);
        textInput.value = '';
    })
    .catch(err => console.error('Type text error:', err));
}

function sendKey(key) {
    fetch(`${API_BASE}/send_key`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key })
    })
    .then(res => res.json())
    .then(data => console.log('Key sent:', data))
    .catch(err => console.error('Send key error:', err));
}

function sendShortcut(shortcut) {
    fetch(`${API_BASE}/send_shortcut`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ shortcut })
    })
    .then(res => res.json())
    .then(data => console.log('Shortcut sent:', data))
    .catch(err => console.error('Send shortcut error:', err));
}

// AI Assistant
function sendAICommand() {
    const aiCommand = document.getElementById('ai-command');
    const aiResponse = document.getElementById('ai-response');
    const command = aiCommand.value;

    if (!command) return;

    aiResponse.textContent = 'Processing...';

    fetch(`${API_BASE}/ai_command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command })
    })
    .then(res => res.json())
    .then(data => {
        aiResponse.textContent = data.response || data.error || 'Command executed';
        console.log('AI response:', data);
    })
    .catch(err => {
        aiResponse.textContent = 'Error: ' + err.message;
        console.error('AI command error:', err);
    });
}

// System Status
function checkPicoStatus() {
    fetch(`${API_BASE}/status`)
    .then(res => res.json())
    .then(data => {
        if (data.pico_connected) {
            updateStatus('pico-status', 'Pico W: Connected', 'connected');
            document.getElementById('pico-ip').textContent = data.pico_ip || '--';
        } else {
            updateStatus('pico-status', 'Pico W: Disconnected', 'disconnected');
        }
    })
    .catch(err => {
        updateStatus('pico-status', 'Pico W: Error', 'disconnected');
        console.error('Status check error:', err);
    });

    // Check status every 5 seconds
    setTimeout(checkPicoStatus, 5000);
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (videoInterval) {
        clearInterval(videoInterval);
    }
});
