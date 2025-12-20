#!/usr/bin/env python3
"""
Speaker Diarization & Separation Script
Separates audio into different speaker folders based on voice embeddings.

Usage:
    python separate_speakers.py <audio_file> [--output-dir <dir>]

Example:
    python separate_speakers.py voices/processed/arjun/sample_powerbi.wav

Output:
    voices/separated/
    ├── speaker_00/
    │   ├── segment_001.wav
    │   └── segment_002.wav
    └── speaker_01/
        └── segment_003.wav
"""

import os
import sys
import argparse
from pathlib import Path
import numpy as np

# Set ffmpeg path for pydub - use local tools/bin
TOOLS_BIN = Path(__file__).parent / "bin"
os.environ["PATH"] = str(TOOLS_BIN) + ":" + os.environ.get("PATH", "")
from pydub import AudioSegment
AudioSegment.converter = str(TOOLS_BIN / "ffmpeg")
AudioSegment.ffprobe = str(TOOLS_BIN / "ffprobe") if (TOOLS_BIN / "ffprobe").exists() else None

# Try pyannote first (best quality), fall back to resemblyzer
try:
    from pyannote.audio import Pipeline
    PYANNOTE_AVAILABLE = True
except ImportError:
    PYANNOTE_AVAILABLE = False

try:
    from resemblyzer import VoiceEncoder, preprocess_wav
    from resemblyzer.hparams import sampling_rate
    RESEMBLYZER_AVAILABLE = True
except ImportError:
    RESEMBLYZER_AVAILABLE = False

import wave
import json
from datetime import datetime


def get_audio_duration(file_path):
    """Get duration in seconds"""
    with wave.open(str(file_path), 'rb') as f:
        frames = f.getnframes()
        rate = f.getframerate()
        return frames / rate


def separate_with_pyannote(audio_file, output_dir, hf_token=None):
    """Use pyannote.audio for speaker diarization (best quality)"""
    print("Using pyannote.audio for speaker diarization...")

    # Initialize pipeline
    # Note: Requires HuggingFace token for model access
    if hf_token:
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=hf_token
        )
    else:
        print("\nWARNING: pyannote requires HuggingFace token for best model.")
        print("Get token at: https://huggingface.co/settings/tokens")
        print("Accept terms at: https://huggingface.co/pyannote/speaker-diarization-3.1")
        print("\nFalling back to resemblyzer...\n")
        return None

    # Run diarization
    diarization = pipeline(str(audio_file))

    # Load audio
    audio = AudioSegment.from_wav(str(audio_file))

    # Extract segments per speaker
    speakers = {}
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        if speaker not in speakers:
            speakers[speaker] = []

        start_ms = int(turn.start * 1000)
        end_ms = int(turn.end * 1000)
        segment = audio[start_ms:end_ms]

        speakers[speaker].append({
            'start': turn.start,
            'end': turn.end,
            'audio': segment
        })

    return speakers


def separate_with_resemblyzer(audio_file, output_dir, segment_length=3.0, min_speakers=1, max_speakers=5,
                               similarity_threshold=0.75):
    """
    Use resemblyzer for voice embedding + clustering

    Improvements for pitch/volume robustness:
    1. Use longer segments (more context)
    2. Higher similarity threshold before splitting
    3. Allow min_speakers=1 (single speaker detection)
    4. Use cosine similarity check before clustering
    """
    print("Using resemblyzer for speaker separation...")
    print(f"Segment length: {segment_length}s")
    print(f"Similarity threshold: {similarity_threshold}")

    # Load encoder
    encoder = VoiceEncoder()

    # Load and preprocess audio
    print(f"Loading {audio_file}...")
    wav = preprocess_wav(str(audio_file))

    duration = len(wav) / sampling_rate
    print(f"Audio duration: {duration:.1f} seconds")

    # Split into segments - use longer segments for better voice identification
    segment_samples = int(segment_length * sampling_rate)
    segments = []

    for i in range(0, len(wav), segment_samples):
        segment = wav[i:i + segment_samples]
        if len(segment) >= sampling_rate * 1.5:  # At least 1.5 seconds for reliable embedding
            segments.append({
                'start': i / sampling_rate,
                'end': min((i + segment_samples) / sampling_rate, duration),
                'audio': segment
            })

    print(f"Created {len(segments)} segments")

    # Get embeddings for each segment
    print("Computing voice embeddings...")
    embeddings = []
    for seg in segments:
        try:
            embed = encoder.embed_utterance(seg['audio'])
            embeddings.append(embed)
        except Exception as e:
            embeddings.append(None)

    # Filter out failed embeddings
    valid_indices = [i for i, e in enumerate(embeddings) if e is not None]
    valid_embeddings = np.array([embeddings[i] for i in valid_indices])
    valid_segments = [segments[i] for i in valid_indices]

    print(f"Valid embeddings: {len(valid_embeddings)}")

    if len(valid_embeddings) < 2:
        print("Not enough valid segments for clustering")
        return None

    # IMPROVEMENT 1: Check average similarity first
    # If all embeddings are very similar, it's likely one speaker
    from sklearn.metrics.pairwise import cosine_similarity

    similarity_matrix = cosine_similarity(valid_embeddings)
    # Get average similarity (excluding self-similarity on diagonal)
    np.fill_diagonal(similarity_matrix, 0)
    avg_similarity = similarity_matrix.sum() / (len(valid_embeddings) * (len(valid_embeddings) - 1))

    print(f"\nAverage embedding similarity: {avg_similarity:.3f}")

    if avg_similarity > similarity_threshold:
        print(f"High similarity ({avg_similarity:.3f} > {similarity_threshold}) - likely SINGLE SPEAKER")
        print("All segments assigned to speaker_00")
        return {"speaker_00": valid_segments}

    # IMPROVEMENT 2: Cluster with better parameters
    from sklearn.cluster import AgglomerativeClustering, SpectralClustering
    from sklearn.metrics import silhouette_score

    # Try different numbers of speakers and pick best
    best_score = -1
    best_labels = None
    best_n = 1

    for n_speakers in range(min_speakers, min(max_speakers + 1, len(valid_embeddings))):
        if n_speakers == 1:
            # Single speaker case
            labels = np.zeros(len(valid_embeddings), dtype=int)
            # Can't compute silhouette for single cluster, use similarity as proxy
            score = avg_similarity
            print(f"  1 speaker: avg similarity = {score:.3f}")
        else:
            try:
                # Use cosine distance for voice embeddings (more robust than euclidean)
                clusterer = AgglomerativeClustering(
                    n_clusters=n_speakers,
                    metric='cosine',
                    linkage='average'
                )
                labels = clusterer.fit_predict(valid_embeddings)

                if len(set(labels)) > 1:
                    score = silhouette_score(valid_embeddings, labels, metric='cosine')
                    print(f"  {n_speakers} speakers: silhouette score = {score:.3f}")
                else:
                    continue
            except Exception as e:
                print(f"  {n_speakers} speakers: error - {e}")
                continue

        # IMPROVEMENT 3: Prefer fewer speakers unless clustering is much better
        # Add penalty for more speakers (Occam's razor)
        adjusted_score = score - (n_speakers - 1) * 0.05

        if adjusted_score > best_score:
            best_score = adjusted_score
            best_labels = labels
            best_n = n_speakers

    print(f"\nBest result: {best_n} speaker(s)")

    if best_n == 1:
        print("Single speaker detected - no separation needed")
        return {"speaker_00": valid_segments}

    # Group segments by speaker
    speakers = {}
    for i, label in enumerate(best_labels):
        speaker_id = f"speaker_{label:02d}"
        if speaker_id not in speakers:
            speakers[speaker_id] = []

        speakers[speaker_id].append(valid_segments[i])

    # IMPROVEMENT 4: Verify clusters are actually different speakers
    # by comparing average embeddings between clusters
    print("\nVerifying speaker separation...")
    speaker_embeddings = {}
    for speaker_id, segs in speakers.items():
        indices = [i for i, s in enumerate(valid_segments) if s in segs]
        speaker_embeddings[speaker_id] = valid_embeddings[indices].mean(axis=0)

    if len(speaker_embeddings) == 2:
        spk_ids = list(speaker_embeddings.keys())
        inter_speaker_sim = cosine_similarity(
            [speaker_embeddings[spk_ids[0]]],
            [speaker_embeddings[spk_ids[1]]]
        )[0][0]
        print(f"Inter-speaker similarity: {inter_speaker_sim:.3f}")

        if inter_speaker_sim > similarity_threshold:
            print(f"WARNING: Speakers are very similar ({inter_speaker_sim:.3f})")
            print("This might be the same person with different vocal tones.")
            print("Consider merging into single speaker.")

    return speakers


def save_separated_audio(speakers, audio_file, output_dir):
    """Save separated audio segments to folders"""

    # Load original audio
    audio = AudioSegment.from_wav(str(audio_file))

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        'source_file': str(audio_file),
        'processed_at': datetime.now().isoformat(),
        'speakers': {}
    }

    for speaker_id, segments in speakers.items():
        speaker_dir = output_dir / speaker_id
        speaker_dir.mkdir(exist_ok=True)

        manifest['speakers'][speaker_id] = {
            'segment_count': len(segments),
            'total_duration': 0,
            'segments': []
        }

        total_duration = 0

        for i, seg in enumerate(segments):
            start_ms = int(seg['start'] * 1000)
            end_ms = int(seg['end'] * 1000)

            segment_audio = audio[start_ms:end_ms]

            segment_file = speaker_dir / f"segment_{i+1:03d}.wav"
            segment_audio.export(
                str(segment_file),
                format="wav",
                parameters=["-ar", "22050", "-ac", "1"]
            )

            duration = (end_ms - start_ms) / 1000
            total_duration += duration

            manifest['speakers'][speaker_id]['segments'].append({
                'file': str(segment_file.name),
                'start': seg['start'],
                'end': seg['end'],
                'duration': duration
            })

        manifest['speakers'][speaker_id]['total_duration'] = total_duration
        print(f"  {speaker_id}: {len(segments)} segments, {total_duration:.1f}s total")

    # Save manifest
    manifest_file = output_dir / "manifest.json"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"\nManifest saved: {manifest_file}")
    return manifest


def main():
    parser = argparse.ArgumentParser(description="Separate speakers in audio file")
    parser.add_argument("audio_file", help="Input audio file (WAV)")
    parser.add_argument("--output-dir", "-o", help="Output directory",
                       default="voices/separated")
    parser.add_argument("--segment-length", "-s", type=float, default=3.0,
                       help="Segment length in seconds (default: 3.0)")
    parser.add_argument("--max-speakers", "-m", type=int, default=5,
                       help="Maximum number of speakers to detect (default: 5)")
    parser.add_argument("--similarity-threshold", "-t", type=float, default=0.75,
                       help="Similarity threshold for same speaker (default: 0.75)")
    parser.add_argument("--hf-token", help="HuggingFace token for pyannote")
    parser.add_argument("--use-pyannote", action="store_true",
                       help="Force use of pyannote (requires HF token)")
    args = parser.parse_args()

    audio_file = Path(args.audio_file)
    if not audio_file.exists():
        print(f"Error: File not found: {audio_file}")
        sys.exit(1)

    # Create output directory based on input filename
    base_name = audio_file.stem
    output_dir = Path(args.output_dir) / base_name

    print("\n" + "="*60)
    print("  SPEAKER SEPARATION")
    print("="*60)
    print(f"Input: {audio_file}")
    print(f"Output: {output_dir}")

    duration = get_audio_duration(audio_file)
    print(f"Duration: {duration:.1f}s ({duration/60:.1f} min)")
    print("="*60 + "\n")

    # Try pyannote first if requested, otherwise use resemblyzer
    speakers = None

    if args.use_pyannote and PYANNOTE_AVAILABLE:
        speakers = separate_with_pyannote(audio_file, output_dir, args.hf_token)

    if speakers is None and RESEMBLYZER_AVAILABLE:
        speakers = separate_with_resemblyzer(
            audio_file, output_dir,
            segment_length=args.segment_length,
            max_speakers=args.max_speakers,
            similarity_threshold=args.similarity_threshold
        )

    if speakers is None:
        print("Error: Could not separate speakers")
        print("Install dependencies: pip install resemblyzer pydub scikit-learn")
        sys.exit(1)

    print(f"\nFound {len(speakers)} speakers:")

    # Save separated audio
    manifest = save_separated_audio(speakers, audio_file, output_dir)

    print("\n" + "="*60)
    print("DONE! Next steps:")
    print("="*60)
    print(f"1. Listen to segments in: {output_dir}/")
    print("2. Rename folders: speaker_00 → amma, speaker_01 → chinna, etc.")
    print("3. Use for training: python train_xtts.py train amma")
    print(f"\nTip: For more speakers, use --max-speakers 8")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
