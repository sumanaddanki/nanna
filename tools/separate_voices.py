"""
Separate speakers from audio file
Identifies who speaks when and extracts each speaker's audio
"""
import os
import wave
import struct

def analyze_audio_energy(wav_path, chunk_ms=500):
    """Simple energy-based voice activity detection"""

    with wave.open(wav_path, 'rb') as w:
        rate = w.getframerate()
        frames = w.getnframes()
        duration = frames / rate

        chunk_frames = int(rate * chunk_ms / 1000)

        segments = []

        for i in range(0, frames, chunk_frames):
            w.setpos(i)
            chunk = w.readframes(min(chunk_frames, frames - i))

            # Calculate energy
            samples = struct.unpack(f'{len(chunk)//2}h', chunk)
            energy = sum(abs(s) for s in samples) / len(samples) if samples else 0

            start_time = i / rate
            end_time = min((i + chunk_frames) / rate, duration)

            segments.append({
                'start': start_time,
                'end': end_time,
                'energy': energy
            })

    return segments, duration

def find_speech_segments(segments, threshold_ratio=0.3):
    """Find segments where someone is speaking based on energy threshold"""

    max_energy = max(s['energy'] for s in segments)
    threshold = max_energy * threshold_ratio

    speech_segments = []
    in_speech = False
    current_start = 0

    for seg in segments:
        if seg['energy'] > threshold and not in_speech:
            in_speech = True
            current_start = seg['start']
        elif seg['energy'] <= threshold and in_speech:
            in_speech = False
            speech_segments.append({
                'start': current_start,
                'end': seg['start'],
                'duration': seg['start'] - current_start
            })

    if in_speech:
        speech_segments.append({
            'start': current_start,
            'end': segments[-1]['end'],
            'duration': segments[-1]['end'] - current_start
        })

    return speech_segments

def main():
    wav_path = "/Users/sumanaddanke/git/nanna/webapp/nanna_voice.wav"

    print(f"Analyzing: {wav_path}\n")

    segments, duration = analyze_audio_energy(wav_path, chunk_ms=300)
    speech = find_speech_segments(segments)

    print(f"Total duration: {duration:.1f} seconds")
    print(f"Found {len(speech)} speech segments:\n")

    for i, seg in enumerate(speech):
        print(f"  Segment {i+1}: {seg['start']:.1f}s - {seg['end']:.1f}s ({seg['duration']:.1f}s)")

    print("\n" + "="*50)
    print("INSTRUCTIONS:")
    print("="*50)
    print("""
Listen to the audio and identify which segments are Nanna (slower voice).
Then tell me the segment numbers, like: "Nanna is segments 1, 3, 5"

To listen:
  open /Users/sumanaddanke/git/nanna/webapp/nanna_voice.wav
""")

if __name__ == "__main__":
    main()
