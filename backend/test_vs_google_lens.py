import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

# Copy test image to backend uploads
import shutil
source = r"C:\Users\amogh\.gemini\antigravity\brain\946c0803-7546-4cc8-a692-94a3d8326f5c\uploaded_media_1769869945678.png"
dest = "static/uploads/test_prescription.png"

if os.path.exists(source):
    shutil.copy(source, dest)
    print(f"✓ Copied to {dest}")
else:
    print("Source file not found")
    exit(1)

# Test improved Gemini OCR
from utils.gemini_ocr_engine import GeminiOCREngine

engine = GeminiOCREngine()
results = engine.extract_medicines(dest)

print("\n" + "="*70)
print("RESULTS vs GOOGLE LENS")
print("="*70)

if results:
    for i, med in enumerate(results, 1):
        fuzzy = " [FUZZY CORRECTED]" if med.get('fuzzy_corrected') else ""
        orig = f" (was: {med.get('original_ocr')})" if med.get('fuzzy_corrected') else ""
        
        print(f"\n{i}. {med['medicine_name']}{fuzzy}")
        print(f"   Dosage: {med.get('dosage', 'N/A')}")
        print(f"   Duration: {med.get('duration', 'N/A')}")
        print(f"   Confidence: {med.get('confidence', 0) * 100:.1f}%{orig}")
    
    avg_conf = sum(m.get('confidence', 0) for m in results) / len(results) * 100
    print(f"\n📊 Total: {len(results)} medicines at {avg_conf:.1f}% confidence")
else:
    print("❌ No medicines extracted")

print("\n" + "="*70)
print("GOOGLE LENS EXTRACTED:")
print("- Tab Zeredol-SP")
print("- Tab Velef (uncertain)")
print("- Cap Etoshine-MR")
print("- Tab Pan-D")
print("="*70)
