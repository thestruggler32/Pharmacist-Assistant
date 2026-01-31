import os
import sys
from utils.ocr_engine import MedicalVerificationEngine
from dotenv import load_dotenv

load_dotenv()

print("DEBUG: Starting Pipeline Check")
engine = MedicalVerificationEngine()
print(f"Mistral Key present: {bool(engine.mistral_key)}")
print(f"CalStudio Key present: {bool(engine.calstudio_key)}")

image_path = "115.jpg"
# Fallback to a known image if 115.jpg missing
if not os.path.exists(image_path):
    # Try to find any jpg/png in current dir
    files = [f for f in os.listdir('.') if f.endswith('.jpg') or f.endswith('.png')]
    if files:
        image_path = files[0]
    else:
        print("No image found to test.")
        sys.exit(1)

print(f"Testing on {image_path}")

try:
    print("\n--- Step 1: Mistral OCR (Pixtral) ---")
    raw = engine._mistral_ocr(image_path)
    print(f"Mistral Output (First 200 chars):\n{raw[:200]}")
    
    print("\n--- Step 2: CalStudio Verifier ---")
    final = engine._calstudio_verify(image_path, raw)
    print("CalStudio Output:")
    print(final)
    
except Exception as e:
    print(f"\nFATAL ERROR: {e}")
    import traceback
    traceback.print_exc()
