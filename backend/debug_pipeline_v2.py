
import os
import sys
import base64
import json
import traceback
import requests
from dotenv import load_dotenv

# Setup logging
log_file = open("debug_log.txt", "w", encoding="utf-8")
def log(msg):
    print(msg)
    log_file.write(str(msg) + "\n")
    log_file.flush()

load_dotenv()

MISTAL_KEY = os.getenv("MISTRAL_API_KEY")
CALSTUDIO_KEY = os.getenv("CALSTUDIO_API_KEY")

log("DEBUG: Starting Pipeline Check V2")
log(f"Mistral Key present: {bool(MISTAL_KEY)}")
log(f"CalStudio Key present: {bool(CALSTUDIO_KEY)}")
log(f"CalStudio Key (First 10 chars): {CALSTUDIO_KEY[:10] if CALSTUDIO_KEY else 'None'}")

IMAGE_PATH = "115.jpg" # Ensure this file exists or use verification logic to find one
if not os.path.exists(IMAGE_PATH):
    # Try to find any .jpg/png in artifacts?
    # For now, just error if not found
    log(f"ERROR: {IMAGE_PATH} not found.")
    import glob
    images = glob.glob("*.jpg") + glob.glob("*.png")
    if images:
        IMAGE_PATH = images[0]
        log(f"Using alternative image: {IMAGE_PATH}")
    else:
        sys.exit(1)

log(f"Testing on {IMAGE_PATH}")

def run_test():
    try:
        # 1. Mistral OCR
        log("\n--- Step 1: Mistral OCR ---")
        with open(IMAGE_PATH, "rb") as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Only import if needed to avoid overhead if just testing CalStudio
        try:
            from mistralai import Mistral
            client = Mistral(api_key=MISTAL_KEY)
            
            chat_response = client.chat.complete(
                model="pixtral-12b-2409",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Transcribe the handwritten text."},
                            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_data}"}
                        ]
                    }
                ]
            )
            mistral_text = chat_response.choices[0].message.content
            log(f"Mistral Text Preview: {mistral_text[:100]}...")
            
        except Exception as e:
            log(f"Mistral Error: {e}")
            mistral_text = "DUMMY TEXT FOR TESTING CALSTUDIO"

        # 2. CalStudio
        log("\n--- Step 2: CalStudio Verifier ---")
        prompt = f"""
        Analyze the following text from a prescription and the image. Verify and correct.
        Return JSON with medicines list.
        OCR Text:
        {mistral_text}
        """
        
        payload = {
            "prompt": prompt,
            "apiKey": CALSTUDIO_KEY,
            "appName": "claudelccfyb",
            "fileUrl": f"data:image/jpeg;base64,{image_data}"
        }
        
        url = "https://calstudio.com/getbackResponse"
        log(f"Sending request to {url}...")
        
        resp = requests.post(url, json=payload, timeout=60)
        log(f"Status Code: {resp.status_code}")
        log(f"Response Headers: {resp.headers}")
        
        try:
            log(f"Response Text: {resp.text}")
        except:
            log("Could not print response text")

        if resp.status_code == 200:
            log("SUCCESS: CalStudio returned 200")
            log(resp.json())
        else:
            log("FAILURE: CalStudio returned non-200")
            
    except Exception as e:
        log(f"EXCEPTION: {e}")
        log(traceback.format_exc())

run_test()
log("Done.")
log_file.close()
