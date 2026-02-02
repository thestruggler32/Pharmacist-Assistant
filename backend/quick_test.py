import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

print("Quick Gemini 1.5 Pro Test\n" + "="*60)

from utils.gemini_ocr_engine import GeminiOCREngine
import glob

# Find latest upload
uploads = glob.glob("static/uploads/*.png") + glob.glob("static/uploads/*.jpg")
if not uploads:
    print("No uploaded images found")
    exit(1)

latest = max(uploads, key=os.path.getctime)
print(f"Testing: {latest}\n")

engine = GeminiOCREngine()

if not engine.model:
    print("ERROR: Model not initialized!")
    print(f"API Key present: {engine.api_key is not None}")
    exit(1)

print("Model initialized successfully")
print("Starting extraction (this will take ~40s with rate limiting)...\n")

results = engine.extract_medicines(latest)

print("\n" + "="*60)
print(f"RESULTS: {len(results)} medicines extracted")
print("="*60)

if results:
    for i, med in enumerate(results, 1):
        print(f"\n{i}. {med['medicine_name']}")
        print(f"   Dosage: {med.get('dosage', 'N/A')}")
        print(f"   Duration: {med.get('duration', 'N/A')}")
        print(f"   Confidence: {med.get('confidence', 0)*100:.1f}%")
        if med.get('fuzzy_corrected'):
            print(f"   [Fuzzy corrected from: {med.get('original_ocr')}]")
else:
    print("\n❌ EXTRACTION FAILED - No medicines found")
    print("\nThis could mean:")
    print("1. Gemini API quota exhausted")
    print("2. JSON parsing error")
    print("3. Gemini returned empty response")
