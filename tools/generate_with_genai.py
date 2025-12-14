"""
Generate mouth variations using Google GenAI SDK (newer)
"""
from google import genai
from google.genai import types
import base64
import os
import time
from PIL import Image
import io

# Configure with API key
API_KEY = "AIzaSyAcWJa3_ODygf0PlhrZ1YuR0H1AzSN7wUQ"
client = genai.Client(api_key=API_KEY)

def generate_variation(input_image_path, output_path, edit_prompt):
    """Generate a face variation using Gemini"""

    print(f"  Generating: {os.path.basename(output_path)}")

    # Load and encode image
    with open(input_image_path, 'rb') as f:
        image_bytes = f.read()

    # Create prompt - STRONGLY emphasize keeping mustache
    full_prompt = f"""Edit this photograph of an Indian man's face.

CRITICAL REQUIREMENTS - DO NOT CHANGE:
- Keep the EXACT same thick black MUSTACHE - this is ESSENTIAL
- Keep the EXACT same face shape
- Keep the EXACT same skin tone
- Keep the EXACT same hair
- Keep the EXACT same person identity

ONLY CHANGE: {edit_prompt}

The man MUST have his mustache in the output. Generate a realistic photograph."""

    try:
        # Use Gemini image generation model
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=[
                full_prompt,
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
            ],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"]
            )
        )

        # Check for image in response
        if response.candidates:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    img_data = part.inline_data.data
                    with open(output_path, 'wb') as f:
                        f.write(img_data)
                    print(f"  ✓ Saved: {output_path}")
                    return True
                elif part.text:
                    print(f"  Text response: {part.text[:100]}...")

        print(f"  No image generated")
        return False

    except Exception as e:
        error_msg = str(e)
        print(f"  Error: {error_msg[:200]}")
        return False


def main():
    input_image = "/Users/sumanaddanke/git/nanna/nana.jpg"
    output_dir = "./nanna_expressions"
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n📸 Source: {input_image}")
    print(f"📁 Output: {output_dir}")
    print(f"💰 Cost: ~$0.04 per image\n")

    # First, let's check available models
    print("Checking available models...")
    try:
        for model in client.models.list():
            if 'image' in model.name.lower() or 'imagen' in model.name.lower():
                print(f"  Found: {model.name}")
    except Exception as e:
        print(f"  Could not list models: {e}")

    print("\nGenerating variations...")

    variations = [
        ("mouth_open_ah.jpg", "mouth moderately open as if saying a word, natural speaking position"),
    ]

    for filename, prompt in variations:
        output_path = os.path.join(output_dir, filename)
        print(f"\n🎨 Creating: {filename}")
        print(f"   Prompt: {prompt}")

        success = generate_variation(input_image, output_path, prompt)

        if success:
            print(f"   ✅ Done!")
        else:
            print(f"   ❌ Failed")

        time.sleep(2)

    print(f"\n✅ Finished!")

if __name__ == "__main__":
    main()
