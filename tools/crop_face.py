"""
Crop a specific person's face from photos with multiple people
Uses face detection to find faces, then lets you select which one to crop
"""

import cv2
import os
import sys
import numpy as np

try:
    import mediapipe as mp
except ImportError:
    print("Installing mediapipe...")
    os.system("pip3 install mediapipe")
    import mediapipe as mp

class FaceCropper:
    def __init__(self):
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1,  # 0 for close faces, 1 for far faces
            min_detection_confidence=0.5
        )

    def detect_and_crop_faces(self, image_path, output_dir, padding=0.3):
        """
        Detect all faces in image and save each as separate file
        padding: extra space around face (0.3 = 30% extra on each side)
        """

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Load image
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: Cannot load {image_path}")
            return []

        h, w = img.shape[:2]
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Detect faces
        results = self.face_detection.process(rgb_img)

        if not results.detections:
            print(f"No faces found in {image_path}")
            return []

        saved_files = []
        base_name = os.path.splitext(os.path.basename(image_path))[0]

        print(f"Found {len(results.detections)} face(s) in {image_path}")

        for i, detection in enumerate(results.detections):
            # Get bounding box
            bbox = detection.location_data.relative_bounding_box

            # Convert relative to absolute coordinates
            x = int(bbox.xmin * w)
            y = int(bbox.ymin * h)
            face_w = int(bbox.width * w)
            face_h = int(bbox.height * h)

            # Add padding
            pad_x = int(face_w * padding)
            pad_y = int(face_h * padding)

            x1 = max(0, x - pad_x)
            y1 = max(0, y - pad_y)
            x2 = min(w, x + face_w + pad_x)
            y2 = min(h, y + face_h + pad_y)

            # Crop face
            face_img = img[y1:y2, x1:x2]

            # Determine position (left or right)
            center_x = x + face_w // 2
            position = "left" if center_x < w // 2 else "right"

            # Save
            filename = f"{base_name}_face_{position}.jpg"
            filepath = os.path.join(output_dir, filename)
            cv2.imwrite(filepath, face_img)
            saved_files.append(filepath)

            print(f"  ✓ Saved: {filename} ({face_w}x{face_h} pixels, {position} side)")

        return saved_files

    def crop_specific_position(self, image_path, output_path, position="left", padding=0.4):
        """
        Crop face from a specific position (left or right)
        For photos where Nanna is always on one side
        """

        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: Cannot load {image_path}")
            return None

        h, w = img.shape[:2]
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        results = self.face_detection.process(rgb_img)

        if not results.detections:
            print(f"No faces found in {image_path}")
            return None

        # Find face on specified side
        target_face = None
        target_x = 0

        for detection in results.detections:
            bbox = detection.location_data.relative_bounding_box
            center_x = bbox.xmin + bbox.width / 2

            if position == "left" and center_x < 0.5:
                if target_face is None or center_x < target_x:
                    target_face = detection
                    target_x = center_x
            elif position == "right" and center_x >= 0.5:
                if target_face is None or center_x > target_x:
                    target_face = detection
                    target_x = center_x

        if target_face is None:
            print(f"No face found on {position} side")
            return None

        # Crop with padding
        bbox = target_face.location_data.relative_bounding_box
        x = int(bbox.xmin * w)
        y = int(bbox.ymin * h)
        face_w = int(bbox.width * w)
        face_h = int(bbox.height * h)

        pad_x = int(face_w * padding)
        pad_y = int(face_h * padding)

        x1 = max(0, x - pad_x)
        y1 = max(0, y - pad_y)
        x2 = min(w, x + face_w + pad_x)
        y2 = min(h, y + face_h + pad_y)

        face_img = img[y1:y2, x1:x2]

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)

        cv2.imwrite(output_path, face_img)
        print(f"✓ Saved: {output_path}")

        return output_path


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Crop faces from photos')
    parser.add_argument('--input', '-i', required=True, help='Input image')
    parser.add_argument('--output', '-o', default='./cropped_faces', help='Output directory or file')
    parser.add_argument('--position', '-p', choices=['left', 'right', 'all'], default='all',
                        help='Which face to crop (left, right, or all)')
    parser.add_argument('--padding', type=float, default=0.4, help='Padding around face (0.4 = 40%)')

    args = parser.parse_args()

    cropper = FaceCropper()

    if args.position == 'all':
        cropper.detect_and_crop_faces(args.input, args.output, args.padding)
    else:
        output_path = args.output if args.output.endswith('.jpg') else os.path.join(args.output, 'face.jpg')
        cropper.crop_specific_position(args.input, output_path, args.position, args.padding)


if __name__ == "__main__":
    main()
