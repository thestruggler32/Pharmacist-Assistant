import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

print("Testing Gemini OCR Engine initialization and extraction...\n")

from utils.gemini_ocr_engine import GeminiOCREngine

engine = GeminiOCREngine()

print(f"\nEngine initialized: {engine.model is not None}")
print(f"API Key present: {engine.api_key is not None}")

if engine.model:
    # Find the most recent uploaded image
    import glob
    uploads = glob.glob("static/uploads/*.png") + glob.glob("static/uploads/*.jpg")
    if uploads:
        latest = max(uploads, key=os.path.getctime)
        print(f"\nTesting on: {latest}")
        
        results = engine.extract_medicines(latest)
        
        print(f"\n{'='*70}")
        print(f"FINAL RESULTS: {len(results)} medicines")
        print(f"{'='*70}")
        
        for i, med in enumerate(results, 1):
            print(f"\n{i}. {med['medicine_name']}")
            print(f"   Dosage: {med.get('dosage')}")
            print(f"   Duration: {med.get('duration')}")
            print(f"   Confidence: {med.get('confidence', 0)*100:.1f}%")
    else:
        print("No images found in static/uploads/")
else:
    print("\n❌ Model not initialized! Check API key and initialization logs above.")
