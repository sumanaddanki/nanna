"""
Generate mouth variations using Imagen API (Google Cloud)
This uses the $300 free credit
Cost: ~$0.04 per image
"""
import google.generativeai as genai
import base64
import os
import time
from PIL import Image
import io

API_KEY = "AIzaSyAcWJa3_ODygf0PlhrZ1YuR0H1AzSN7wUQ"
genai.configure(api_key=API_KEY)

def generate_with_imagen(input_image_path, output_path, edit_prompt):
    """Use Imagen to edit an image"""
    
    print(f"  Generating: {os.path.basename(output_path)}")
    
    # Load source image
    with open(input_image_path, 'rb') as f:
        image_bytes = f.read()
    
    # Try Gemini's image generation model
    model = genai.GenerativeModel('gemini-2.0-flash-exp-image-generation')
    
    # Create the prompt
    full_prompt = f"""Edit this photograph of an Indian man's face. 
    
IMPORTANT: Keep the EXACT same face, same person, same features, same skin tone, same mustache.
ONLY change: {edit_prompt}

The output should look like a real photograph, not artistic or cartoon."""

    try:
        # Load image for the model
        img = Image.open(input_image_path)

        # Use Gemini 2.0 Flash experimental image generation
        response = model.generate_content(
            [full_prompt, img]
        )

        # Check response for image data
        if response.candidates:
            for part in response.candidates[0].content.parts:
                # Check for inline image data
                if hasattr(part, 'inline_data') and part.inline_data:
                    # Get image bytes
                    img_data = part.inline_data.data
                    if isinstance(img_data, str):
                        img_data = base64.b64decode(img_data)
                    with open(output_path, 'wb') as f:
                        f.write(img_data)
                    print(f"  ✓ Saved: {output_path}")
                    return True
                # Some models return as file_data
                elif hasattr(part, 'file_data') and part.file_data:
                    print(f"  Got file_data response")
                    return False

        # Print what we got
        if hasattr(response, 'text'):
            print(f"  Got text response: {response.text[:100]}...")
        else:
            print(f"  No image in response")
        return False
        
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            print(f"  ⏳ Rate limited - waiting 60 seconds...")
            time.sleep(60)
            return generate_with_imagen(input_image_path, output_path, edit_prompt)  # Retry
        else:
            print(f"  Error: {error_msg[:150]}")
            return False


def main():
    input_image = "./nanna_cropped/nanna_xga4.jpg"
    output_dir = "./nanna_expressions"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n📸 Source: {input_image}")
    print(f"📁 Output: {output_dir}")
    print(f"💰 Cost: ~$0.04 per image (from $300 credit)\n")
    
    variations = [
        ("mouth_open_ah.jpg", "mouth wide open as if saying 'Aaah'"),
        ("mouth_round_oh.jpg", "mouth in a round 'O' shape as if saying 'Oh'"),
        ("mouth_closed_mm.jpg", "mouth firmly closed with lips pressed together"),
        ("big_smile.jpg", "a big warm smile showing happiness"),
    ]
    
    for filename, prompt in variations:
        output_path = os.path.join(output_dir, filename)
        print(f"\n🎨 Creating: {filename}")
        print(f"   Prompt: {prompt}")
        
        success = generate_with_imagen(input_image, output_path, prompt)
        
        if success:
            print(f"   ✅ Done!")
        else:
            print(f"   ❌ Failed")
        
        time.sleep(5)  # Small delay between requests
    
    print(f"\n✅ Finished! Check {output_dir} folder")
    print(f"💰 Estimated cost: ~$0.16 (4 images × $0.04)")

if __name__ == "__main__":
    main()
