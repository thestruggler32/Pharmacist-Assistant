"""
Debug script to test OCR and parsing on a specific image
"""

import os
import sys

print("=" * 70)
print("PRESCRIPTION OCR DEBUG TOOL")
print("=" * 70)

# Test image path
test_image = input("\nEnter image path (or press Enter for default): ").strip()
if not test_image:
    test_image = "filled-medical-prescription-isolated-on-260nw-144551783.webp"

if not os.path.exists(test_image):
    print(f"\n✗ Image not found: {test_image}")
    sys.exit(1)

print(f"\n📷 Testing image: {test_image}")

# Step 1: Preprocessing
print("\n" + "=" * 70)
print("STEP 1: IMAGE PREPROCESSING")
print("=" * 70)

from utils.image_preprocessor import ImagePreprocessor

# Test both modes
print("\n[1a] Standard Mode:")
preprocessor_std = ImagePreprocessor(handwriting_mode=False)
processed_std, report_std = preprocessor_std.preprocess(test_image)
preprocessor_std.save_preprocessed_image(processed_std, "debug_standard.jpg")
print(f"  Quality: {report_std['quality_score']}")
print(f"  Blur score: {report_std['blur_score']:.2f}")
print(f"  Contrast: {report_std['contrast_score']:.2f}")
print(f"  Saved: debug_standard.jpg")

print("\n[1b] Handwriting Mode:")
preprocessor_hw = ImagePreprocessor(handwriting_mode=True)
processed_hw, report_hw = preprocessor_hw.preprocess(test_image)
preprocessor_hw.save_preprocessed_image(processed_hw, "debug_handwriting.jpg")
print(f"  Quality: {report_hw['quality_score']}")
print(f"  Blur score: {report_hw['blur_score']:.2f}")
print(f"  Contrast: {report_hw['contrast_score']:.2f}")
print(f"  Saved: debug_handwriting.jpg")

# Step 2: OCR
print("\n" + "=" * 70)
print("STEP 2: OCR TEXT EXTRACTION")
print("=" * 70)

from utils.ocr_engine import OCREngine

ocr_engine = OCREngine()

print("\n[2a] OCR on Standard Preprocessing:")
ocr_std = ocr_engine.extract_text("debug_standard.jpg")
print(f"  Extracted {len(ocr_std)} text items")

print("\n[2b] OCR on Handwriting Preprocessing:")
ocr_hw = ocr_engine.extract_text("debug_handwriting.jpg")
print(f"  Extracted {len(ocr_hw)} text items")

# Show OCR results
print("\n  Raw OCR Output (Handwriting Mode):")
print("  " + "-" * 66)
for i, item in enumerate(ocr_hw[:20], 1):  # Show first 20
    text = item.get('text', '')
    conf = item.get('confidence', 0)
    print(f"  {i:2d}. [{conf:.2f}] {text}")
if len(ocr_hw) > 20:
    print(f"  ... and {len(ocr_hw) - 20} more items")

# Step 3: Parsing
print("\n" + "=" * 70)
print("STEP 3: MEDICINE PARSING")
print("=" * 70)

from utils.prescription_parser import PrescriptionParser

print("\n[3a] Standard Parser:")
parser_std = PrescriptionParser(lenient_mode=False)
medicines_std = parser_std.parse(ocr_hw)
print(f"  Detected: {len(medicines_std)} medicines")

print("\n[3b] Lenient Parser (for handwriting):")
parser_lenient = PrescriptionParser(lenient_mode=True)
medicines_lenient = parser_lenient.parse(ocr_hw)
print(f"  Detected: {len(medicines_lenient)} medicines")

# Show parsed medicines
if medicines_lenient:
    print("\n  Parsed Medicines:")
    print("  " + "-" * 66)
    for i, med in enumerate(medicines_lenient, 1):
        print(f"\n  Medicine {i}:")
        print(f"    Name: {med['medicine_name']}")
        print(f"    Strength: {med['strength']}")
        print(f"    Dosage: {med['dosage']}")
        print(f"    Confidence: {med['confidence']:.2f}")
        print(f"    Risk Level: {med['risk_level']}")
        print(f"    Original: {med['original_text'][:60]}...")
else:
    print("\n  ⚠️ No medicines detected!")
    print("\n  Possible reasons:")
    print("    1. OCR couldn't extract text properly")
    print("    2. Text doesn't match medicine patterns")
    print("    3. Image quality too low")
    print("\n  Suggestions:")
    print("    ✓ Use Handwriting Mode in the UI")
    print("    ✓ Check debug_handwriting.jpg to see preprocessed image")
    print("    ✓ Review raw OCR output above")

# Step 4: Medicine Matching
if medicines_lenient:
    print("\n" + "=" * 70)
    print("STEP 4: MEDICINE DATABASE MATCHING")
    print("=" * 70)
    
    from utils.correction_learner import CorrectionLearner
    
    learner = CorrectionLearner()
    
    for i, med in enumerate(medicines_lenient[:3], 1):  # First 3 only
        print(f"\n[4.{i}] Searching for: '{med['medicine_name']}'")
        suggestions = learner.suggest_correction(
            med['medicine_name'],
            region='All',
            threshold=0.6
        )
        
        if suggestions:
            print(f"  Found {len(suggestions)} suggestions:")
            for j, sug in enumerate(suggestions[:3], 1):
                print(f"    {j}. {sug['text']} ({sug.get('brand', 'N/A')}) "
                      f"- {sug['confidence']:.0%}")
        else:
            print("  No matches found in database")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"\n✓ OCR extracted: {len(ocr_hw)} text items")
print(f"✓ Medicines detected: {len(medicines_lenient)}")
print(f"\nGenerated files:")
print(f"  - debug_standard.jpg (standard preprocessing)")
print(f"  - debug_handwriting.jpg (handwriting preprocessing)")
print("\n" + "=" * 70)

if len(medicines_lenient) == 0:
    print("\n⚠️  IMPORTANT: No medicines detected!")
    print("\nTo use in the web UI:")
    print("  1. Go to http://localhost:5000/upload?user_id=pharma_001")
    print("  2. ✅ CHECK the 'Handwriting Mode' checkbox")
    print("  3. Upload your image")
    print("  4. Review detected medicines")
    print("\n" + "=" * 70)
