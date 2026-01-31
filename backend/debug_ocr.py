"""Debug OCR output structure v3 - print as dict"""
import sys
sys.path.insert(0, '.')

from utils.ocr_engine import OCREngine
import cv2
import json

# Initialize OCR
print("Initializing OCR engine...")
ocr_engine = OCREngine(lang='en')

# Load image
image_path = 'filled-medical-prescription-isolated-on-260nw-144551783.webp'
image = cv2.imread(image_path)

print("\nRunning OCR...")
result = ocr_engine.ocr.ocr(image)

ocr_result = result[0]

# Try to convert to dict
try:
    result_dict = dict(ocr_result)
    print("\nOCRResult as dict keys:")
    for key in result_dict.keys():
        print(f"  - {key}")
    
    # Print rec_texts if it exists
    if 'rec_texts' in result_dict:
        print(f"\nrec_texts (first 3): {result_dict['rec_texts'][:3]}")
    if 'rec_scores' in result_dict:
        print(f"\nrec_scores (first 3): {result_dict['rec_scores'][:3]}")
except Exception as e:
    print(f"\nError converting to dict: {e}")
    print(f"\nTrying str():")
    print(str(ocr_result)[:500])
