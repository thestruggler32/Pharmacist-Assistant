import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.claude_ocr_engine import ClaudeOCREngine

def test_claude():
    # Test image
    filename = "0b156e5a-7cf9-425a-b72a-b236c695386e_115.jpg"
    image_path = os.path.join("static", "uploads", filename)
    
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return
    
    print("="*70)
    print("TESTING CLAUDE 3.5 SONNET OCR ENGINE")
    print("="*70)
    
    engine = ClaudeOCREngine()
    
    if not engine.client:
        print("\n⚠️ BLACKBOX_API_KEY is missing from .env file!")
        print("Please add: BLACKBOX_API_KEY=your_api_key")
        return
    
    # Run full pipeline
    results = engine.extract_medicines(image_path)
    
    # Display results
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    if not results:
        print("❌ No medicines extracted")
        return
    
    import json
    print(json.dumps(results, indent=2))
    
    # Confidence analysis
    print("\n" + "="*70)
    print("CONFIDENCE ANALYSIS")
    print("="*70)
    
    for med in results:
        source = med.get('source', 'unknown')
        conf = med.get('confidence', 0) * 100
        fuzzy = " (fuzzy corrected)" if med.get('fuzzy_corrected') else ""
        print(f"{med['medicine_name']}: {conf:.1f}% [{source}]{fuzzy}")
    
    avg_conf = sum(m.get('confidence', 0) for m in results) / len(results) * 100
    print(f"\nAverage Confidence: {avg_conf:.1f}%")
    
    # Compare to Google Lens
    print("\n" + "="*70)
    print("VS GOOGLE LENS")
    print("="*70)
    print("✓ Structured JSON output (medicine, dosage, duration)")
    print("✓ Shorthand decoded (BD → Twice daily)")
    print("✓ Fuzzy error correction") 
    print("✓ Confidence scoring")
    print(f"✓ {len(results)} medicines extracted with {avg_conf:.1f}% confidence")

if __name__ == "__main__":
    test_claude()
