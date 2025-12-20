"""
Amma Call Passthrough Server
============================
Records conversations with Amma through Twilio, transcribes in real-time,
and saves both audio and transcripts for later training.

Flow:
1. You call Twilio number
2. Twilio forwards to Amma's real phone
3. Both sides' audio streamed to this server via WebSocket
4. Whisper transcribes in real-time
5. Audio + transcripts saved for training

Setup:
1. pip install -r requirements.txt
2. Set environment variables (see .env.example)
3. Run: python app.py
4. Use ngrok to expose: ngrok http 5000
5. Configure Twilio webhook to ngrok URL
"""

import os
import json
import base64
import asyncio
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import Response
import uvicorn

# For transcription
import whisper
import numpy as np
import soundfile as sf

app = FastAPI(title="Amma Call Recorder")

# Configuration
AMMA_PHONE = os.getenv("AMMA_PHONE", "+1234567890")  # Amma's real phone number
OUTPUT_DIR = Path("recordings")
OUTPUT_DIR.mkdir(exist_ok=True)

# Load Whisper model (use 'base' for speed, 'large-v3' for quality)
print("Loading Whisper model...")
whisper_model = whisper.load_model("base")  # Change to 'large-v3' for better quality
print("Whisper model loaded!")


@app.post("/incoming-call")
async def handle_incoming_call(request: Request):
    """
    Twilio webhook for incoming calls.
    Returns TwiML to:
    1. Start media stream (for recording/transcription)
    2. Forward call to Amma's real phone
    """
    call_sid = (await request.form()).get("CallSid", "unknown")

    # Create session directory for this call
    session_dir = OUTPUT_DIR / f"call_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{call_sid[:8]}"
    session_dir.mkdir(exist_ok=True)

    # TwiML response
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Start>
        <Stream url="wss://{request.url.hostname}/media-stream">
            <Parameter name="session_dir" value="{session_dir}" />
        </Stream>
    </Start>
    <Say>Connecting you to Amma...</Say>
    <Dial callerId="{{{{From}}}}">
        <Number>{AMMA_PHONE}</Number>
    </Dial>
</Response>"""

    return Response(content=twiml, media_type="application/xml")


@app.websocket("/media-stream")
async def media_stream(websocket: WebSocket):
    """
    WebSocket endpoint for Twilio Media Streams.
    Receives real-time audio from both sides of the call.
    """
    await websocket.accept()

    session_dir = None
    audio_buffer = []
    stream_sid = None

    print("Media stream connected!")

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)

            event = data.get("event")

            if event == "start":
                # Stream started - get session info
                stream_sid = data.get("streamSid")
                start_data = data.get("start", {})
                custom_params = start_data.get("customParameters", {})
                session_dir = Path(custom_params.get("session_dir", OUTPUT_DIR / "unknown"))
                session_dir.mkdir(exist_ok=True)

                print(f"Stream started: {stream_sid}")
                print(f"Saving to: {session_dir}")

            elif event == "media":
                # Audio data received
                payload = data.get("media", {}).get("payload")
                if payload:
                    # Decode base64 audio (mulaw 8kHz)
                    audio_bytes = base64.b64decode(payload)
                    audio_buffer.append(audio_bytes)

            elif event == "stop":
                # Stream ended - process and save
                print(f"Stream ended: {stream_sid}")

                if audio_buffer and session_dir:
                    await process_and_save_audio(audio_buffer, session_dir)

                break

    except Exception as e:
        print(f"WebSocket error: {e}")

    finally:
        if audio_buffer and session_dir:
            await process_and_save_audio(audio_buffer, session_dir)


async def process_and_save_audio(audio_buffer: list, session_dir: Path):
    """
    Process audio buffer, save to WAV, and transcribe.
    """
    print(f"Processing {len(audio_buffer)} audio chunks...")

    # Combine all audio chunks
    combined_audio = b"".join(audio_buffer)

    # Convert mulaw to PCM (Twilio sends 8kHz mulaw)
    # This is simplified - in production, use audioop or similar
    try:
        import audioop
        pcm_audio = audioop.ulaw2lin(combined_audio, 2)

        # Convert to numpy array
        audio_array = np.frombuffer(pcm_audio, dtype=np.int16).astype(np.float32) / 32768.0

        # Save as WAV
        wav_path = session_dir / "recording.wav"
        sf.write(str(wav_path), audio_array, 8000)
        print(f"Saved audio: {wav_path}")

        # Transcribe with Whisper
        print("Transcribing...")
        result = whisper_model.transcribe(str(wav_path), language="te")  # Telugu

        # Save transcript
        transcript_path = session_dir / "transcript.txt"
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(result["text"])
        print(f"Saved transcript: {transcript_path}")

        # Save detailed segments (with timestamps)
        segments_path = session_dir / "segments.json"
        with open(segments_path, "w", encoding="utf-8") as f:
            json.dump(result["segments"], f, ensure_ascii=False, indent=2)
        print(f"Saved segments: {segments_path}")

        # Create metadata
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": len(audio_array) / 8000,
            "transcript_preview": result["text"][:200] + "..." if len(result["text"]) > 200 else result["text"]
        }
        metadata_path = session_dir / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"Error processing audio: {e}")
        # Save raw audio anyway
        raw_path = session_dir / "raw_audio.bin"
        with open(raw_path, "wb") as f:
            f.write(combined_audio)
        print(f"Saved raw audio: {raw_path}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "whisper_model": "loaded"}


@app.get("/recordings")
async def list_recordings():
    """List all recorded calls."""
    recordings = []
    for session_dir in OUTPUT_DIR.iterdir():
        if session_dir.is_dir():
            metadata_path = session_dir / "metadata.json"
            if metadata_path.exists():
                with open(metadata_path) as f:
                    metadata = json.load(f)
                    metadata["session_id"] = session_dir.name
                    recordings.append(metadata)
    return {"recordings": sorted(recordings, key=lambda x: x.get("timestamp", ""), reverse=True)}


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║          AMMA CALL RECORDER - PASSTHROUGH SERVER          ║
    ╠═══════════════════════════════════════════════════════════╣
    ║                                                           ║
    ║  This server records calls for training Amma's voice.     ║
    ║                                                           ║
    ║  Flow:                                                    ║
    ║  1. You call Twilio number                                ║
    ║  2. Twilio forwards to Amma's real phone                  ║
    ║  3. Both sides' audio streamed here                       ║
    ║  4. Whisper transcribes in real-time                      ║
    ║  5. Audio + transcripts saved                             ║
    ║                                                           ║
    ║  Next steps:                                              ║
    ║  - Run: ngrok http 5000                                   ║
    ║  - Configure Twilio webhook with ngrok URL                ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    uvicorn.run(app, host="0.0.0.0", port=5000)
