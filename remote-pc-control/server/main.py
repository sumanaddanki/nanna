#!/usr/bin/env python3
"""
Remote PC Control Server
- Captures screen via HDMI capture / camera
- Uses Gemini Vision to understand screen
- Sends commands to Pico W for mouse/keyboard control
- Provides web interface for remote access
"""

import os
import cv2
import socket
import json
import base64
import threading
from io import BytesIO
from PIL import Image
from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# ============ CONFIGURATION ============
PICO_IP = os.getenv("PICO_IP", "192.168.1.100")
PICO_PORT = int(os.getenv("PICO_PORT", 8888))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CAPTURE_DEVICE = int(os.getenv("CAPTURE_DEVICE", 0))  # 0 = default camera/capture
WEB_PORT = int(os.getenv("WEB_PORT", 9999))
# =======================================

app = Flask(__name__,
            template_folder='../web/templates',
            static_folder='../web/static')
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    vision_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    vision_model = None
    print("WARNING: No Gemini API key - AI features disabled")

# Video capture
cap = None
latest_frame = None
frame_lock = threading.Lock()


def init_capture():
    """Initialize video capture device"""
    global cap
    cap = cv2.VideoCapture(CAPTURE_DEVICE)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    return cap.isOpened()


def capture_frame():
    """Capture a single frame"""
    global latest_frame
    if cap and cap.isOpened():
        ret, frame = cap.read()
        if ret:
            with frame_lock:
                latest_frame = frame.copy()
            return frame
    return None


def frame_to_base64(frame):
    """Convert OpenCV frame to base64 JPEG"""
    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
    return base64.b64encode(buffer).decode('utf-8')


def frame_to_pil(frame):
    """Convert OpenCV frame to PIL Image"""
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def send_to_pico(command: dict) -> dict:
    """Send command to Pico W"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((PICO_IP, PICO_PORT))
        sock.send(json.dumps(command).encode('utf-8'))
        response = sock.recv(1024).decode('utf-8')
        sock.close()
        return json.loads(response)
    except Exception as e:
        return {"status": "error", "message": str(e)}


def analyze_screen(prompt: str, frame=None) -> str:
    """Use Gemini Vision to analyze the screen"""
    if not vision_model:
        return "Gemini API not configured"

    if frame is None:
        frame = capture_frame()

    if frame is None:
        return "No frame available"

    image = frame_to_pil(frame)

    response = vision_model.generate_content([
        prompt,
        image
    ])

    return response.text


def ai_click_target(target_description: str) -> dict:
    """Use AI to find and click a target on screen"""
    frame = capture_frame()
    if frame is None:
        return {"status": "error", "message": "No frame"}

    height, width = frame.shape[:2]

    prompt = f"""Look at this screen and find: "{target_description}"

    The screen resolution is {width}x{height}.

    Return ONLY a JSON object with the x,y coordinates to click:
    {{"x": <number>, "y": <number>, "found": true/false, "element": "<what you found>"}}

    If you cannot find the target, set found to false.
    """

    try:
        result = analyze_screen(prompt, frame)
        # Extract JSON from response
        import re
        json_match = re.search(r'\{[^}]+\}', result)
        if json_match:
            coords = json.loads(json_match.group())
            if coords.get("found"):
                # Calculate relative movement from center
                center_x, center_y = width // 2, height // 2
                rel_x = coords["x"] - center_x
                rel_y = coords["y"] - center_y

                # First move to center, then to target
                send_to_pico({"action": "move_to", "x": rel_x, "y": rel_y})
                send_to_pico({"action": "click"})

                return {"status": "ok", "coords": coords}

        return {"status": "error", "message": "Target not found", "ai_response": result}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def continuous_capture():
    """Background thread for continuous frame capture"""
    while True:
        capture_frame()
        socketio.sleep(0.1)  # ~10 FPS


# ============ WEB ROUTES ============

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/screenshot')
def screenshot():
    """Get current screenshot as base64"""
    frame = capture_frame()
    if frame is not None:
        return jsonify({"image": frame_to_base64(frame)})
    return jsonify({"error": "No frame available"}), 500


@app.route('/api/mouse', methods=['POST'])
def mouse_action():
    """Send mouse command"""
    data = request.json
    result = send_to_pico(data)
    return jsonify(result)


@app.route('/api/keyboard', methods=['POST'])
def keyboard_action():
    """Send keyboard command"""
    data = request.json
    result = send_to_pico(data)
    return jsonify(result)


@app.route('/api/ai/analyze', methods=['POST'])
def ai_analyze():
    """Analyze screen with AI"""
    data = request.json
    prompt = data.get("prompt", "Describe what you see on this screen")
    result = analyze_screen(prompt)
    return jsonify({"result": result})


@app.route('/api/ai/click', methods=['POST'])
def ai_click():
    """Click on element described in natural language"""
    data = request.json
    target = data.get("target", "")
    result = ai_click_target(target)
    return jsonify(result)


@app.route('/api/ai/execute', methods=['POST'])
def ai_execute():
    """Execute a complex task using AI"""
    data = request.json
    task = data.get("task", "")

    prompt = f"""You are controlling a computer. The user wants to: "{task}"

    Look at the screen and tell me the next action to take.
    Return JSON: {{"action": "click|type|scroll|key", "target": "...", "value": "..."}}

    - For click: target = what to click
    - For type: value = text to type
    - For scroll: value = up/down
    - For key: value = key name (enter, tab, etc.)
    """

    result = analyze_screen(prompt)
    return jsonify({"ai_response": result})


def generate_video():
    """Generator for video streaming"""
    while True:
        with frame_lock:
            if latest_frame is not None:
                _, buffer = cv2.imencode('.jpg', latest_frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        socketio.sleep(0.1)


@app.route('/video_feed')
def video_feed():
    """Live video stream"""
    return Response(generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# ============ WEBSOCKET EVENTS ============

@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('mouse_move')
def handle_mouse_move(data):
    send_to_pico({"action": "move", "x": data['x'], "y": data['y']})


@socketio.on('mouse_click')
def handle_mouse_click(data):
    send_to_pico({"action": "click", "button": data.get('button', 'left')})


@socketio.on('key_press')
def handle_key_press(data):
    send_to_pico({"action": "key", "key": data['key']})


# ============ MAIN ============

if __name__ == '__main__':
    print("Initializing capture device...")
    if init_capture():
        print(f"Capture device {CAPTURE_DEVICE} initialized")
    else:
        print("WARNING: Could not initialize capture device")

    # Start background capture thread
    capture_thread = threading.Thread(target=continuous_capture, daemon=True)
    capture_thread.start()

    print(f"Starting server on port {WEB_PORT}")
    print(f"Pico W expected at {PICO_IP}:{PICO_PORT}")
    print(f"Access web interface at http://localhost:{WEB_PORT}")

    socketio.run(app, host='0.0.0.0', port=WEB_PORT, debug=False)
