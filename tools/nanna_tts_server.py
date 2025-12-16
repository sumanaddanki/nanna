#!/usr/bin/env python3
"""
Nanna TTS Server - Coqui XTTS v2 Voice Cloning
Runs locally on Mac, serves TTS API for webapp

Usage:
    python3.11 nanna_tts_server.py

API:
    POST /api/tts
    Body: {"text": "Hello ra Chinna", "voice": "nanna"}
    Returns: audio/wav
"""

import os
import io
os.environ["COQUI_TOS_AGREED"] = "1"

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from TTS.api import TTS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from webapp

# Configuration
VOICE_DIR = os.path.dirname(os.path.abspath(__file__))
VOICES = {
    "nanna": os.path.join(VOICE_DIR, "voice_tests", "nanna_reference.wav"),
    # Add more voices here as we train them
    # "ravi": os.path.join(VOICE_DIR, "voices", "ravi.wav"),
    # "lakshmi": os.path.join(VOICE_DIR, "voices", "lakshmi.wav"),
}

# Load model on startup (takes ~30 seconds)
print("Loading XTTS v2 model (this takes about 30 seconds)...")
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
print("Model loaded!")


@app.route('/api/tts', methods=['POST'])
def generate_speech():
    """Generate speech from text using voice cloning."""
    try:
        data = request.json
        text = data.get('text', '')
        voice_id = data.get('voice', 'nanna')
        language = data.get('language', 'hi')  # Hindi closest to Telugu

        if not text:
            return jsonify({"error": "No text provided"}), 400

        # Get reference voice file
        voice_file = VOICES.get(voice_id)
        if not voice_file or not os.path.exists(voice_file):
            return jsonify({"error": f"Voice '{voice_id}' not found"}), 404

        print(f"Generating: '{text[:50]}...' with voice: {voice_id}")

        # Generate speech
        wav = tts.tts(
            text=text,
            speaker_wav=voice_file,
            language=language
        )

        # Convert to bytes
        import scipy.io.wavfile as wavfile
        import numpy as np

        buffer = io.BytesIO()
        wavfile.write(buffer, 22050, np.array(wav))
        buffer.seek(0)

        return send_file(buffer, mimetype='audio/wav')

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/voices', methods=['GET'])
def list_voices():
    """List available voices."""
    available = {k: os.path.exists(v) for k, v in VOICES.items()}
    return jsonify({
        "voices": list(VOICES.keys()),
        "available": available
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "model": "xtts_v2"})


if __name__ == '__main__':
    print("\n" + "="*50)
    print("Nanna TTS Server")
    print("="*50)
    print(f"Available voices: {list(VOICES.keys())}")
    print("\nAPI endpoints:")
    print("  POST /api/tts     - Generate speech")
    print("  GET  /api/voices  - List voices")
    print("  GET  /health      - Health check")
    print("\nExample:")
    print('  curl -X POST http://localhost:5002/api/tts \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"text": "Chudu ra Chinna"}\' --output speech.wav')
    print("="*50 + "\n")

    app.run(host='0.0.0.0', port=5002, debug=False)
