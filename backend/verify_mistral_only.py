
import os
import sys
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Setup paths (hack for imports)
sys.path.append(os.getcwd())

try:
    from utils.ocr_engine import MistralOnlyEngine
    
    print("Initializing Engine...")
    engine = MistralOnlyEngine()
    
    image_path = "test_image_ashok.png"
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found")
        sys.exit(1)
        
    print(f"Processing {image_path}...")
    
    # Peek at raw text first
    raw = engine._mistral_ocr(image_path)
    print("\n--- RAW MISTRAL OUTPUT ---")
    print(raw)
    print("--------------------------\n")
    
    # logic copy from extract_medicines to debug step-by-step
    candidates = engine._parse_mistral_text(raw)
    results = []
    
    # We can just call extract_medicines but we want to debug, so let's call it normally 
    # but I already modified the script to use engine.extract_medicines. 
    # Let's just print raw here and then call extract_medicines again (Mistral is cheap/fast enough or we cache it)
    # Actually, let's just use the internal method to get raw, print it, then pass it to parse/learn manually in script?
    # Or simpler: Just call extract specific methods.
    
    results = engine.extract_medicines(image_path) # This calls mistral again. That's fine.
    
    print("\n--- Extracted Medicines ---")
    for med in results:
        print(f"- Name: {med.get('medicine_name')}")
        print(f"  Confidence: {med.get('confidence')}")
        print(f"  Source: {med.get('source')}")
        print("  ---")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
