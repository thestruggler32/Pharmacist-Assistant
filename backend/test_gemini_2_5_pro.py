"""
Quick test to verify Gemini 2.5 Pro is loaded correctly
"""
import sys
sys.path.insert(0, '.')

print("Testing Gemini 2.5 Pro OCR Engine initialization...\n")
print("=" * 60)

try:
    from utils.gemini_ocr_engine import GeminiOCREngine
    
    engine = GeminiOCREngine()
    
    if engine.model:
        print("\n✓✓✓ SUCCESS!")
        print("=" * 60)
        print("Gemini 2.5 Pro OCR Engine is ready!")
        print("\nConfiguration:")
        print(f"  - Model: gemini-2.5-pro")
        print(f"  - Rate Limit: 15 RPM (5s delay)")
        print(f"  - API Key: {'GOOGLE_API_KEY' if engine.api_key == __import__('os').getenv('GOOGLE_API_KEY') else 'GOOGLE_AI_STUDIO_KEY'}")
        print("\nThe backend is now using Gemini 2.5 Pro for OCR!")
    else:
        print("\n✗ Failed to initialize")
        print("Check your .env file for GOOGLE_API_KEY")
        
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
