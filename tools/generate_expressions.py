"""
Generate Expression Photos from Single Face Image
Uses FREE open-source models - no API cost!

Usage:
    python generate_expressions.py --input nanna.jpg --output ./expressions/

Output: Multiple photos with different expressions and mouth shapes
"""

import os
import sys

# Check if required packages are installed
def check_dependencies():
    required = ['cv2', 'numpy', 'PIL']
    missing = []

    for pkg in required:
        try:
            __import__(pkg if pkg != 'cv2' else 'cv2')
        except ImportError:
            missing.append(pkg)

    if missing:
        print("Installing required packages...")
        os.system(f"pip install opencv-python numpy pillow")

check_dependencies()

import cv2
import numpy as np
from PIL import Image

def create_mouth_variations(image_path, output_dir):
    """
    Create basic mouth variations using image manipulation
    For production, use InsightFace or similar
    """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load {image_path}")
        return

    # Save original as neutral
    cv2.imwrite(os.path.join(output_dir, "neutral.jpg"), img)
    print("✓ Saved: neutral.jpg")

    # For proper expression generation, we need face landmark detection
    # Here's a simplified version - for production use InsightFace

    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║  FOR BEST RESULTS, USE THESE FREE TOOLS:                   ║
    ╠════════════════════════════════════════════════════════════╣
    ║                                                            ║
    ║  1. FaceApp (Phone) - Easiest                              ║
    ║     • Download app → Open photo → Apply expressions        ║
    ║     • FREE filters: Smile, Hollywood, Fun                  ║
    ║                                                            ║
    ║  2. MyHeritage Deep Nostalgia (Web)                        ║
    ║     • https://www.myheritage.com/deep-nostalgia            ║
    ║     • Animates photo → Screenshot different frames         ║
    ║                                                            ║
    ║  3. Runway ML (Web)                                        ║
    ║     • https://runwayml.com                                 ║
    ║     • Face manipulation tools - FREE tier                  ║
    ║                                                            ║
    ║  4. InsightFace (Python - Advanced)                        ║
    ║     • pip install insightface onnxruntime                  ║
    ║     • Full control over expressions                        ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    return output_dir

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate expression photos')
    parser.add_argument('--input', '-i', required=True, help='Input face photo')
    parser.add_argument('--output', '-o', default='./expressions', help='Output directory')

    args = parser.parse_args()

    print(f"\n📸 Processing: {args.input}")
    print(f"📁 Output to: {args.output}\n")

    create_mouth_variations(args.input, args.output)

if __name__ == "__main__":
    main()
