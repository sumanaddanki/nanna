"""
Generate mouth variations using Gemini Image Generation
"""
import google.generativeai as genai
import base64
import os
from PIL import Image
import io

# Configure API
API_KEY = "AIzaSyB5C3pZNvgLRPVGmvKaKKawVEgrctYMgMQ"
genai.configure(api_key=API_KEY)

def image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def generate_variation(input_image_path, output_path, prompt):
    """Generate a variation of the face with different expression"""
    
    # Load image
    img = Image.open(input_image_path)
    
    # Use Gemini with image input
    model = genai.GenerativeModel('gemini-2.0-flash-exp-image-generation')
    
    response = model.generate_content([
        prompt,
        img
    ])
    
    # Check if image was generated
    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                # Save the generated image
                img_data = base64.b64decode(part.inline_data.data)
                with open(output_path, 'wb') as f:
                    f.write(img_data)
                print(f"✓ Saved: {output_path}")
                return True
            elif hasattr(part, 'text'):
                print(f"Text response: {part.text[:200]}")
    
    print(f"Could not generate image for: {prompt}")
    return False

def main():
    input_image = "./nanna_cropped/nanna_xga4.jpg"
    output_dir = "./nanna_expressions"
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Variations to generate
    variations = [
        ("mouth_open.jpg", "Edit this photo to show the same person with mouth open as if saying 'Ah'. Keep the face exactly the same, only change mouth position."),
        ("mouth_round.jpg", "Edit this photo to show the same person with mouth in round 'O' shape. Keep the face exactly the same, only change mouth position."),
        ("mouth_closed.jpg", "Edit this photo to show the same person with mouth firmly closed, lips pressed together. Keep the face exactly the same."),
        ("smiling_wide.jpg", "Edit this photo to show the same person with a wide happy smile. Keep the face exactly the same."),
    ]
    
    for filename, prompt in variations:
        output_path = os.path.join(output_dir, filename)
        print(f"\nGenerating: {filename}")
        generate_variation(input_image, output_path, prompt)

if __name__ == "__main__":
    main()
