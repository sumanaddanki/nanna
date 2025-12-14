"""
Extract Nanna's voice segments from the mixed audio
"""
import wave
import struct
import os

def extract_segments(input_path, output_path, segments):
    """Extract specific time segments and combine them"""

    with wave.open(input_path, 'rb') as inp:
        params = inp.getparams()
        rate = inp.getframerate()

        all_frames = []

        for start_sec, end_sec in segments:
            start_frame = int(start_sec * rate)
            end_frame = int(end_sec * rate)
            num_frames = end_frame - start_frame

            inp.setpos(start_frame)
            frames = inp.readframes(num_frames)
            all_frames.append(frames)

            print(f"  Extracted: {start_sec}s - {end_sec}s ({end_sec - start_sec}s)")

        # Combine all frames
        combined = b''.join(all_frames)

        # Write output
        with wave.open(output_path, 'wb') as out:
            out.setparams(params)
            out.writeframes(combined)

        # Calculate total duration
        total_duration = len(combined) / (rate * params.sampwidth)
        print(f"\n✓ Saved: {output_path}")
        print(f"  Total duration: {total_duration:.1f} seconds")

def main():
    input_wav = "/Users/sumanaddanke/git/nanna/webapp/nanna_voice.wav"
    output_wav = "/Users/sumanaddanke/git/nanna/webapp/nanna_voice_only.wav"

    # Nanna's segments (from user input)
    # Skipping 38-46 segment since user says they nod/say 'ha' there
    nanna_segments = [
        (2, 3),      # 02-03
        (8, 11),     # 08-11
        (16, 17),    # 16-16 (assuming 1 second)
        (21, 25),    # 21-25
        (28, 30),    # 28-30
        (31, 37),    # 31-37
        (38, 46),    # 38-46 (has some 'ha' from user but mostly Nanna)
        (52, 56),    # 52-56
    ]

    print(f"Input: {input_wav}")
    print(f"Output: {output_wav}")
    print(f"\nExtracting Nanna's segments:\n")

    extract_segments(input_wav, output_wav, nanna_segments)

    print(f"\n✅ Done! Nanna's voice extracted.")
    print(f"   File ready for ElevenLabs voice cloning.")

if __name__ == "__main__":
    main()
