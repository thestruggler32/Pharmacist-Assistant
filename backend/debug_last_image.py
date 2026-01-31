
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
load_dotenv()

from utils.ocr_engine import MistralOnlyEngine

def test_last_image():
    engine = MistralOnlyEngine()
    img = "filled-medical-prescription-isolated-on-260nw-144551783.webp"
    
    if os.path.exists(img):
        print(f"\nTesting {img}...")
        try:
            results = engine.extract_medicines(img)
            print(f"Found {len(results)} items.")
            for res in results:
                print(f"  - {res.get('medicine_name')} ({res.get('original_text')})")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"Skipping {img} (not found)")

if __name__ == "__main__":
    test_last_image()
