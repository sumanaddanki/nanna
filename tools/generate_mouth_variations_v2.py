"""
Generate mouth variations using Gemini - with rate limit handling
"""
import google.generativeai as genai
import base64
import os
import time
from PIL import Image

# Configure API
API_KEY = "AIzaSyB5C3pZNvgLRPVGmvKaKKawVEgrctYMgMQ"
genai.configure(api_key=API_KEY)

def generate_variation(input_image_path, output_path, prompt):
    """Generate a variation of the face with different expression"""
    
    print(f"  Loading image...")
    img = Image.open(input_image_path)
    
    # Try different models
    models_to_try = [
        'gemini-2.5-flash',  # Standard model
        'gemini-1.5-flash',  # Older model
    ]
    
    for model_name in models_to_try:
        try:
            print(f"  Trying model: {model_name}")
            model = genai.GenerativeModel(model_name)
            
            response = model.generate_content([
                f"Look at this face photo. Describe how you would edit it to: {prompt}. Be very specific about the facial changes needed.",
                img
            ])
            
            if response.text:
                print(f"  Model response: {response.text[:200]}...")
                return response.text
                
        except Exception as e:
            print(f"  Error with {model_name}: {str(e)[:100]}")
            time.sleep(3)  # Wait before trying next model
    
    return None

def main():
    input_image = "./nanna_cropped/nanna_xga4.jpg"
    
    print(f"\n📸 Input: {input_image}")
    print("Note: Gemini can analyze but may not directly edit images.")
    print("Trying to get editing instructions...\n")
    
    # Just try one prompt to test
    prompt = "show the mouth open as if saying 'Ah'"
    print(f"Testing: {prompt}")
    result = generate_variation(input_image, "test.jpg", prompt)
    
    if result:
        print("\n✅ API is working! But Gemini text models can't edit images directly.")
        print("\nFor actual image editing, we need:")
        print("1. Imagen API (image generation) - $0.04/image")
        print("2. Or use FaceApp on phone (FREE)")

if __name__ == "__main__":
    main()
