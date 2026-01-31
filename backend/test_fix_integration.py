
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

load_dotenv()

from utils.ocr_engine import MistralOnlyEngine

def test_engine():
    print("Initializing Engine...")
    engine = MistralOnlyEngine()
    
    image_path = "115.jpg"
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found.")
        return

    print(f"Running extract_medicines on {image_path}...")
    results = engine.extract_medicines(image_path)
    
    print("\n--- RESULTS ---")
    for i, med in enumerate(results):
        print(f"Medicine {i+1}:")
        print(f"  Name: {med.get('medicine_name')}")
        print(f"  Strength: {med.get('strength')}")
        print(f"  Dosage: {med.get('dosage')}")
        print(f"  Confidence: {med.get('confidence')}")
        print("-" * 20)
        
    if not results:
        print("No medicines found!")
    else:
        print(f"Found {len(results)} medicines.")

if __name__ == "__main__":
    test_engine()
