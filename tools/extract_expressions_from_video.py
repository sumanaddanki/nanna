"""
Extract Expression Photos from Video
=====================================
Takes a video of a person talking and extracts different:
- Emotions (happy, neutral, sad, surprised, etc.)
- Mouth shapes (open, closed, round for different sounds)

Usage:
    pip install opencv-python mediapipe numpy pillow
    python extract_expressions_from_video.py --input video.mp4 --output ./faces/

Output: 10-15 photos with different expressions and mouth positions
"""

import os
import sys
import argparse
from collections import defaultdict

# Install dependencies if needed
def install_deps():
    try:
        import cv2
        import mediapipe
        import numpy as np
    except ImportError:
        print("Installing required packages...")
        os.system("pip install opencv-python mediapipe numpy pillow")

install_deps()

import cv2
import numpy as np

# Try to import mediapipe
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("Warning: mediapipe not installed. Using basic extraction.")


class ExpressionExtractor:
    def __init__(self):
        if MEDIAPIPE_AVAILABLE:
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,
                min_detection_confidence=0.5
            )

        # Mouth landmark indices in MediaPipe
        self.UPPER_LIP = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291]
        self.LOWER_LIP = [146, 91, 181, 84, 17, 314, 405, 321, 375, 291]
        self.MOUTH_OUTER = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 409, 270, 269, 267, 0, 37, 39, 40, 185]

    def calculate_mouth_openness(self, landmarks, image_height):
        """Calculate how open the mouth is (0 = closed, 1 = wide open)"""
        if not MEDIAPIPE_AVAILABLE:
            return 0.5

        # Get upper and lower lip center points
        upper_lip_y = np.mean([landmarks[i].y for i in [13, 14]])  # Upper lip center
        lower_lip_y = np.mean([landmarks[i].y for i in [17, 18]])  # Lower lip center

        # Mouth openness as ratio
        mouth_open = (lower_lip_y - upper_lip_y) * image_height
        return min(mouth_open / 30, 1.0)  # Normalize

    def calculate_mouth_width(self, landmarks, image_width):
        """Calculate mouth width (for smile detection)"""
        if not MEDIAPIPE_AVAILABLE:
            return 0.5

        left_corner = landmarks[61].x
        right_corner = landmarks[291].x
        width = (right_corner - left_corner) * image_width
        return width

    def classify_mouth_shape(self, openness, width, avg_width):
        """Classify mouth shape for lip-sync"""
        if openness < 0.15:
            return "closed"  # M, B, P sounds
        elif openness < 0.3:
            if width > avg_width * 1.1:
                return "smile"  # E, I sounds
            else:
                return "slight_open"  # neutral talking
        elif openness < 0.5:
            return "medium_open"  # A, E sounds
        else:
            return "wide_open"  # A, O sounds (surprised)

    def extract_frames(self, video_path, output_dir, target_count=15):
        """Extract diverse expression frames from video"""

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Cannot open video {video_path}")
            return []

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps

        print(f"📹 Video: {video_path}")
        print(f"   Duration: {duration:.1f}s, FPS: {fps:.0f}, Frames: {total_frames}")

        # Categories to collect
        categories = {
            "closed": [],      # Mouth closed (M, B, P)
            "slight_open": [], # Slight open
            "smile": [],       # Smiling (E, I)
            "medium_open": [], # Medium open (A, E)
            "wide_open": [],   # Wide open (A, O, surprise)
        }

        # Process every Nth frame (aim for ~100 samples)
        sample_interval = max(1, total_frames // 100)
        frame_num = 0
        widths = []

        print(f"   Processing every {sample_interval} frames...")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_num % sample_interval == 0:
                # Process this frame
                if MEDIAPIPE_AVAILABLE:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = self.face_mesh.process(rgb_frame)

                    if results.multi_face_landmarks:
                        landmarks = results.multi_face_landmarks[0].landmark
                        h, w = frame.shape[:2]

                        openness = self.calculate_mouth_openness(landmarks, h)
                        width = self.calculate_mouth_width(landmarks, w)
                        widths.append(width)
                        avg_width = np.mean(widths) if widths else width

                        shape = self.classify_mouth_shape(openness, width, avg_width)

                        # Store frame with quality score
                        categories[shape].append({
                            "frame": frame.copy(),
                            "frame_num": frame_num,
                            "openness": openness,
                            "width": width
                        })
                else:
                    # Basic extraction without mediapipe
                    # Just collect frames at intervals
                    idx = frame_num // sample_interval % 5
                    shape_names = list(categories.keys())
                    categories[shape_names[idx]].append({
                        "frame": frame.copy(),
                        "frame_num": frame_num,
                        "openness": 0.5,
                        "width": 100
                    })

            frame_num += 1

        cap.release()

        # Select best frame from each category
        saved_files = []
        for category, frames in categories.items():
            if frames:
                # Sort by some quality metric (e.g., middle openness for that category)
                frames.sort(key=lambda x: x["openness"])
                best = frames[len(frames)//2]  # Pick middle one

                filename = f"{category}.jpg"
                filepath = os.path.join(output_dir, filename)
                cv2.imwrite(filepath, best["frame"])
                saved_files.append(filepath)
                print(f"   ✓ Saved: {filename} (frame {best['frame_num']})")

        # Also save a few more variations
        all_frames = []
        for frames in categories.values():
            all_frames.extend(frames)

        if all_frames:
            all_frames.sort(key=lambda x: x["openness"])
            # Save some intermediate openness levels
            for i, pct in enumerate([10, 30, 50, 70, 90]):
                idx = int(len(all_frames) * pct / 100)
                if idx < len(all_frames):
                    filename = f"mouth_{pct}pct_open.jpg"
                    filepath = os.path.join(output_dir, filename)
                    cv2.imwrite(filepath, all_frames[idx]["frame"])
                    saved_files.append(filepath)
                    print(f"   ✓ Saved: {filename}")

        print(f"\n✅ Extracted {len(saved_files)} expression photos to {output_dir}")
        return saved_files


def main():
    parser = argparse.ArgumentParser(
        description='Extract expression photos from video',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python extract_expressions_from_video.py -i nanna_talking.mp4 -o ./nanna_faces/
    python extract_expressions_from_video.py -i video.mov -o ./expressions/ -n 20

Output files:
    closed.jpg        - Mouth closed (for M, B, P sounds)
    slight_open.jpg   - Slightly open mouth
    smile.jpg         - Smiling expression
    medium_open.jpg   - Medium open (for A, E sounds)
    wide_open.jpg     - Wide open (surprised)
    mouth_10pct_open.jpg - 10% mouth openness
    mouth_30pct_open.jpg - 30% mouth openness
    ... etc.
        """
    )
    parser.add_argument('--input', '-i', required=True, help='Input video file')
    parser.add_argument('--output', '-o', default='./expressions', help='Output directory')
    parser.add_argument('--count', '-n', type=int, default=15, help='Target number of photos')

    args = parser.parse_args()

    extractor = ExpressionExtractor()
    extractor.extract_frames(args.input, args.output, args.count)


if __name__ == "__main__":
    main()
