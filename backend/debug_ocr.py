import os
import sys
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.ocr_engine import MistralOnlyEngine

def debug_pipeline():
    # File to test
    filename = "0b156e5a-7cf9-425a-b72a-b236c695386e_115.jpg"
    image_path = os.path.join("static", "uploads", filename)
    
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return

    print(f"DEBUGGING: {filename}")
    engine = MistralOnlyEngine()
    
    # SYSTEM 1: Preprocessing
    print("\n--- STEP 1: Preprocessing ---")
    processed_path = engine._preprocess_image(image_path)
    print(f"Processed path: {processed_path}")
    
    # SYSTEM 2: Single-Shot Pixtral VLM
    print("\n--- STEP 2: Pixtral VLM (Image -> JSON) ---")
    candidates = engine._mistral_ocr_json(processed_path)
    import json
    print(json.dumps(candidates, indent=2))
    
    # SYSTEM 3: Fuzzy Match
    print("\n--- STEP 3: Fuzzy Match ---")
    final = engine._apply_fuzzy_matching(candidates)
    print(json.dumps(final, indent=2))

if __name__ == "__main__":
    debug_pipeline()
