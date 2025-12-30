#!/usr/bin/env python3
"""
Recipe Extractor Web UI
Provides a web interface for extracting recipes from URLs, images, and PDFs
Shows real-time transcription and video frame analysis
"""

import os
import sys
import json
import tempfile
import base64
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
import threading
import time
import platform

# Add ffmpeg to PATH if on Windows
if platform.system() == 'Windows':
    ffmpeg_path = r'C:\ffmpeg\bin'
    if os.path.exists(ffmpeg_path) and ffmpeg_path not in os.environ['PATH']:
        os.environ['PATH'] = ffmpeg_path + os.pathsep + os.environ['PATH']
        print(f"Added ffmpeg to PATH: {ffmpeg_path}")

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from extract_recipe_v2 import (
    gemini_ocr_image,
    format_with_gemini,
    download_video_audio,
    transcribe_audio_whisper,
    save_as_json,
    save_as_markdown
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'recipe-extractor-secret'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max

socketio = SocketIO(app, cors_allowed_origins="*")

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf', 'mp4', 'avi', 'mov', 'mkv'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_video_frames(video_path, output_dir, fps=2):
    """Extract frames from video at specified FPS"""
    import cv2

    frames = []
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return frames

    video_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(video_fps / fps)

    frame_count = 0
    saved_count = 0

    while cap.isOpened() and saved_count < 10:  # Max 10 frames
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            frame_path = os.path.join(output_dir, f"frame_{saved_count:03d}.jpg")
            cv2.imwrite(frame_path, frame)

            # Convert to base64 for web display
            _, buffer = cv2.imencode('.jpg', frame)
            frame_b64 = base64.b64encode(buffer).decode('utf-8')

            frames.append({
                'index': saved_count,
                'timestamp': frame_count / video_fps,
                'path': frame_path,
                'base64': frame_b64
            })
            saved_count += 1

        frame_count += 1

    cap.release()
    return frames


def process_url(url, sid):
    """Process video URL with real-time updates"""
    try:
        print(f"[{sid}] Processing URL: {url}")
        socketio.emit('status', {'step': 'download', 'message': 'Downloading video...'}, room=sid)

        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"[{sid}] Temp directory: {temp_dir}")

            # Download audio
            print(f"[{sid}] Starting download...")
            audio_path = download_video_audio(url, temp_dir)
            print(f"[{sid}] Audio downloaded to: {audio_path}")
            socketio.emit('status', {'step': 'download_complete', 'message': f'Download complete: {os.path.basename(audio_path)}'}, room=sid)

            # Transcribe with progress
            socketio.emit('status', {'step': 'transcribe', 'message': 'Transcribing audio...'}, room=sid)

            transcript = transcribe_audio_whisper(audio_path, model_size="large")

            socketio.emit('transcript', {'text': transcript}, room=sid)
            socketio.emit('status', {'step': 'transcribe_complete', 'message': 'Transcription complete'}, room=sid)

            # Format recipe
            socketio.emit('status', {'step': 'format', 'message': 'Formatting recipe with AI...'}, room=sid)

            recipe_data = format_with_gemini(transcript)

            if recipe_data.get('is_recipe') == False:
                socketio.emit('error', {'message': f"Not a recipe: {recipe_data.get('reason')}"}, room=sid)
                return

            # Save outputs
            recipe_data['source'] = url
            recipe_data['extracted_at'] = datetime.now().isoformat()

            json_path = save_as_json(recipe_data, 'recipes', url)
            md_path = save_as_markdown(recipe_data, 'recipes', url)

            socketio.emit('result', {
                'recipe': recipe_data,
                'json_path': json_path,
                'md_path': md_path
            }, room=sid)

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[{sid}] ERROR: {error_details}")
        socketio.emit('error', {'message': f"{str(e)}\n\nDetails: {error_details}"}, room=sid)


def process_image(image_path, sid):
    """Process image with OCR"""
    try:
        socketio.emit('status', {'step': 'ocr', 'message': 'Extracting text from image...'}, room=sid)

        # Read and encode image for preview
        with open(image_path, 'rb') as f:
            img_data = f.read()
        img_b64 = base64.b64encode(img_data).decode('utf-8')

        socketio.emit('image_preview', {'base64': img_b64}, room=sid)

        # OCR
        raw_text, confidence = gemini_ocr_image(image_path)

        socketio.emit('ocr_result', {'text': raw_text, 'confidence': confidence}, room=sid)
        socketio.emit('status', {'step': 'ocr_complete', 'message': f'OCR complete (confidence: {confidence:.2f})'}, room=sid)

        # Format recipe
        socketio.emit('status', {'step': 'format', 'message': 'Formatting recipe...'}, room=sid)

        recipe_data = format_with_gemini(raw_text)

        if recipe_data.get('is_recipe') == False:
            socketio.emit('error', {'message': f"Not a recipe: {recipe_data.get('reason')}"}, room=sid)
            return

        # Update confidence
        recipe_data['confidence'] = (confidence + recipe_data.get('confidence', 0.5)) / 2
        recipe_data['source'] = image_path
        recipe_data['extracted_at'] = datetime.now().isoformat()

        # Save outputs
        json_path = save_as_json(recipe_data, 'recipes', image_path)
        md_path = save_as_markdown(recipe_data, 'recipes', image_path)

        socketio.emit('result', {
            'recipe': recipe_data,
            'json_path': json_path,
            'md_path': md_path
        }, room=sid)

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[{sid}] ERROR: {error_details}")
        socketio.emit('error', {'message': f"{str(e)}\n\nDetails: {error_details}"}, room=sid)


def process_video_file(video_path, sid):
    """Process uploaded video file with frame extraction"""
    try:
        socketio.emit('status', {'step': 'extract_audio', 'message': 'Extracting audio from video...'}, room=sid)

        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract audio
            import subprocess
            audio_path = os.path.join(temp_dir, 'audio.mp3')

            cmd = ['ffmpeg', '-i', video_path, '-vn', '-acodec', 'mp3', '-y', audio_path]
            subprocess.run(cmd, check=True, capture_output=True)

            socketio.emit('status', {'step': 'extract_audio_complete', 'message': 'Audio extracted'}, room=sid)

            # Extract frames (2 fps)
            socketio.emit('status', {'step': 'extract_frames', 'message': 'Extracting video frames...'}, room=sid)

            frames = extract_video_frames(video_path, temp_dir, fps=2)

            socketio.emit('frames', {'frames': frames}, room=sid)
            socketio.emit('status', {'step': 'extract_frames_complete', 'message': f'Extracted {len(frames)} frames'}, room=sid)

            # Transcribe
            socketio.emit('status', {'step': 'transcribe', 'message': 'Transcribing audio...'}, room=sid)

            transcript = transcribe_audio_whisper(audio_path, model_size="large")

            socketio.emit('transcript', {'text': transcript}, room=sid)
            socketio.emit('status', {'step': 'transcribe_complete', 'message': 'Transcription complete'}, room=sid)

            # Format recipe
            socketio.emit('status', {'step': 'format', 'message': 'Formatting recipe with AI...'}, room=sid)

            recipe_data = format_with_gemini(transcript)

            if recipe_data.get('is_recipe') == False:
                socketio.emit('error', {'message': f"Not a recipe: {recipe_data.get('reason')}"}, room=sid)
                return

            # Save outputs
            recipe_data['source'] = video_path
            recipe_data['extracted_at'] = datetime.now().isoformat()
            recipe_data['frames_analyzed'] = len(frames)

            json_path = save_as_json(recipe_data, 'recipes', video_path)
            md_path = save_as_markdown(recipe_data, 'recipes', video_path)

            socketio.emit('result', {
                'recipe': recipe_data,
                'json_path': json_path,
                'md_path': md_path
            }, room=sid)

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[{sid}] ERROR: {error_details}")
        socketio.emit('error', {'message': f"{str(e)}\n\nDetails: {error_details}"}, room=sid)


@app.route('/')
def index():
    return render_template('recipe_extractor.html')


@app.route('/recipes/<path:filename>')
def download_recipe(filename):
    return send_from_directory('recipes', filename)


@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')


@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')


@socketio.on('extract_url')
def handle_extract_url(data):
    url = data.get('url')
    if not url:
        emit('error', {'message': 'No URL provided'})
        return

    # Process in background thread
    thread = threading.Thread(target=process_url, args=(url, request.sid))
    thread.start()


@socketio.on('extract_file')
def handle_extract_file(data):
    file_data = data.get('file')
    filename = data.get('filename')

    if not file_data or not filename:
        emit('error', {'message': 'No file provided'})
        return

    # Decode base64 file
    try:
        file_bytes = base64.b64decode(file_data.split(',')[1])

        # Save to uploads
        safe_filename = secure_filename(filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)

        with open(file_path, 'wb') as f:
            f.write(file_bytes)

        # Determine file type
        ext = safe_filename.rsplit('.', 1)[1].lower()

        if ext in {'png', 'jpg', 'jpeg', 'gif', 'webp'}:
            # Image
            thread = threading.Thread(target=process_image, args=(file_path, request.sid))
            thread.start()
        elif ext in {'mp4', 'avi', 'mov', 'mkv'}:
            # Video
            thread = threading.Thread(target=process_video_file, args=(file_path, request.sid))
            thread.start()
        elif ext == 'pdf':
            emit('error', {'message': 'PDF support coming soon!'})
        else:
            emit('error', {'message': f'Unsupported file type: {ext}'})

    except Exception as e:
        emit('error', {'message': str(e)})


if __name__ == '__main__':
    print("Starting Recipe Extractor Web UI...")
    print("Open browser to: http://localhost:5555")
    socketio.run(app, host='0.0.0.0', port=5555, debug=True, allow_unsafe_werkzeug=True)
