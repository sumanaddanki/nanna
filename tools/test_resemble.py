"""
Test Resemble.ai voice and compare with original
"""
import requests
import os

API_TOKEN = "DDAUBqxvIm3kToMoM8XCUgtt"
VOICE_UUID = "680d1fb7"
PROJECT_UUID = "f0a60a69"

def generate_test_audio():
    """Generate test audio with Resemble"""

    url = f"https://app.resemble.ai/api/v2/projects/{PROJECT_UUID}/clips"

    # Test text (similar to what Nanna would say)
    test_text = "Ra Chinna, nenu Nanna. Emi cheptav? Baaga cheppu ra."

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token token={API_TOKEN}"
    }

    body = {
        "body": test_text,
        "voice_uuid": VOICE_UUID,
        "is_public": False,
        "is_archived": False
    }

    print(f"Generating audio for: {test_text}")
    print(f"Using voice: {VOICE_UUID}")

    response = requests.post(url, headers=headers, json=body)

    if response.status_code in [200, 201]:
        data = response.json()
        print(f"Response: {data}")

        # Check for audio_src
        if data.get('item') and data['item'].get('audio_src'):
            audio_url = data['item']['audio_src']
            print(f"Audio URL: {audio_url}")

            # Download audio
            audio_response = requests.get(audio_url)
            if audio_response.status_code == 200:
                output_path = "/Users/sumanaddanke/git/nanna/webapp/resemble_test.wav"
                with open(output_path, 'wb') as f:
                    f.write(audio_response.content)
                print(f"✓ Saved: {output_path}")
                return output_path
        else:
            # Audio might need polling
            clip_uuid = data.get('item', {}).get('uuid')
            print(f"Clip created, UUID: {clip_uuid}")
            print("Audio may need time to generate. Check Resemble dashboard.")
            return None
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

if __name__ == "__main__":
    result = generate_test_audio()

    if result:
        print("\n" + "="*50)
        print("Compare these two files:")
        print("="*50)
        print(f"1. Original Nanna: /Users/sumanaddanke/git/nanna/webapp/nanna_voice_only.wav")
        print(f"2. Resemble clone: {result}")
        print("\nOpening both...")

        os.system(f'open -a "QuickTime Player" "/Users/sumanaddanke/git/nanna/webapp/nanna_voice_only.wav"')
        os.system(f'open -a "QuickTime Player" "{result}"')
