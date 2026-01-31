
import os
import sys
import shutil
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
load_dotenv()

from utils.image_preprocessor import ImagePreprocessor
from utils.ocr_engine import MistralOnlyEngine

def test_app_flow():
    print("DEBUG: Simulating App Flow...")
    
    # 1. Setup
    original_path = "115.jpg"
    if not os.path.exists(original_path):
        print("Error: 115.jpg not found")
        return

    # Simulate 'uploads' folder
    upload_folder = "debug_uploads"
    os.makedirs(upload_folder, exist_ok=True)
    
    # Copy to uploads like app does
    filepath = os.path.join(upload_folder, "test_115.jpg")
    shutil.copy(original_path, filepath)
    
    # 2. Preprocessing (Exact logic from app.py)
    # app.py line 54: handwriting_mode = request.form.get('handwriting_mode') == 'on' 
    # Let's assume user might have toggled it? Or default False? 
    # User didn't specify, let's try BOTH.
    
    for mode in [False, True]:
        print(f"\n--- Testing with Handwriting Mode: {mode} ---")
        preprocessor = ImagePreprocessor(handwriting_mode=mode)
        preprocessed_path, report = preprocessor.preprocess(filepath)
        
        # Save like app does
        preprocessed_filename = f"test_preprocessed_{mode}.jpg"
        preprocessed_filepath = os.path.join(upload_folder, preprocessed_filename)
        preprocessor.save_preprocessed_image(preprocessed_path, preprocessed_filepath)
        
        print(f"Preprocessed saved to: {preprocessed_filepath}")
        print(f"Quality Report: {report['quality_score']}")
        
        # 3. OCR (MistralOnly using extract_medicines)
        engine = MistralOnlyEngine()
        print("Running OCR extraction on PREPROCESSED image...")
        results = engine.extract_medicines(preprocessed_filepath)
        
        print("Results:")
        for res in results:
             print(f"  - {res.get('medicine_name')} ({res.get('strength')})")
             
        if not results:
            print("  No medicines found.")

if __name__ == "__main__":
    test_app_flow()
