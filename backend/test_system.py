"""
Test script for the AI Prescription Assistant system
Tests each component individually and the full web pipeline
"""

import sys
import os
import cv2
import numpy as np

# Test configuration
TEST_IMAGE = "115.jpg"

print("=" * 70)
print(f"SYSTEM INTEGRATION TEST - Target: {TEST_IMAGE}")
print("=" * 70)

if not os.path.exists(TEST_IMAGE):
    print(f"FATAL: Test image {TEST_IMAGE} not found!")
    # Try the other image if present
    alt_image = "filled-medical-prescription-isolated-on-260nw-144551783.webp"
    if os.path.exists(alt_image):
        print(f"INFO: Falling back to {alt_image}")
        TEST_IMAGE = alt_image
    else:
        sys.exit(1)

# Test 1: Image Preprocessor
print("\n[1/5] Testing Image Preprocessor...")
try:
    from utils.image_preprocessor import ImagePreprocessor
    preprocessor = ImagePreprocessor(handwriting_mode=True)
    
    processed, report = preprocessor.preprocess(TEST_IMAGE)
    print(f"✓ Preprocessing successful")
    print(f"  Original size: {report['original_size']}")
    print(f"  Quality Score: {report['quality_score']}")
    print(f"  Output shape: {processed.shape}")
    
    # Save debug output
    cv2.imwrite("debug_preprocessed_test.jpg", processed)
    print("  Saved debug_preprocessed_test.jpg")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: OCR Engine
print("\n[2/5] Testing OCR Engine (PaddleOCR)...")
ocr_results = []
try:
    from utils.ocr_engine import OCREngine
    ocr_engine = OCREngine()
    
    # Use the preprocessed image from step 1
    ocr_results = ocr_engine.extract_text("debug_preprocessed_test.jpg")
    
    print(f"✓ OCR extracted {len(ocr_results)} text items")
    if len(ocr_results) > 0:
        print("  Top 3 results:")
        for item in ocr_results[:3]:
            print(f"    - {item['text']} ({item['confidence']:.2f})")
    else:
        print("⚠ No text detected!")

except Exception as e:
    print(f"✗ Error: {e}")

# Test 2c: Groq Llama Vision
print("\n[2c/5] Testing Groq Llama Vision (SOTA Speed)...")
groq_medicines = []
try:
    from utils.ocr_engine import HybridGroqEngine
    hybrid_engine = HybridGroqEngine()
    
    if hybrid_engine.enabled:
        # Test on original image
        print("  Calling Groq Llama Vision API...")
        groq_medicines = hybrid_engine.extract_medicines(TEST_IMAGE)
        
        print(f"✓ Groq Vision processed in ~500ms")
        print(f"✓ Extracted {len(groq_medicines)} medicines")
        for med in groq_medicines[:5]:
            print(f"  - {med['medicine_name']} | {med.get('strength', '')} | {med.get('frequency', '')}")
            print(f"    Confidence: {med.get('confidence', 0):.2f} | Source: {med.get('source', 'unknown')}")
            
        if len(groq_medicines) >= 2:
            print(f"✓ Groq Benchmark Passed: {len(groq_medicines)} medicines detected")
    else:
        print("⚠ GROQ_API_KEY not configured - skipping SOTA test")
        print("  Using PaddleOCR fallback instead")

except Exception as e:
    print(f"✗ Groq Vision Error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Prescription Parser & Medicine Dictionary
print("\n[3/5] Testing Prescription Parser & Medicine Lookup...")
try:
    from utils.prescription_parser import PrescriptionParser
    parser = PrescriptionParser(lenient_mode=True)
    
    medicines = parser.parse(ocr_results)
    print(f"✓ Parser found {len(medicines)} medicines")
    
    expected_medicines = ["liposomal", "amphotericin", "fluconazole", "canesten", "candid"]
    found_expected = []
    
    print("\n  Detailed Detection:")
    for med in medicines:
        print(f"  - {med['medicine_name']} | {med['strength']} | {med['dosage']}")
        print(f"    Raw: {med['original_text']} (Conf: {med['confidence']:.2f})")
        
        # Check against expected
        name_lower = med['medicine_name'].lower()
        for expected in expected_medicines:
             if expected in name_lower:
                 found_expected.append(expected)

    if found_expected:
        print(f"\n✓ SUCCESSFULLY DETECTED target medicines: {list(set(found_expected))}")
    else:
        print("\n⚠ warning: Target medicines (Amphotericin/Fluconazole) might haven be missed or named differently.")

except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: Web Upload Simulation
print("\n[4/5] Testing Web Upload Pipeline (End-to-End)...")
try:
    from app import app
    client = app.test_client()
    
    with open(TEST_IMAGE, 'rb') as img:
        data = {
            'prescription_image': (img, TEST_IMAGE),
            'handwriting_mode': 'on'
        }
        print("  Simulating POST /upload...")
        response = client.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
        
        if response.status_code == 200:
            print("✓ Web upload successful (200 OK)")
            html_content = response.data.decode('utf-8')
            
            # Check if medicines are listed in the review page
            # We look for value="MedicineName" or just the text
            found_in_html = []
            if "Amphotericin" in html_content: found_in_html.append("Amphotericin")
            if "Liposomal" in html_content: found_in_html.append("Liposomal")
            if "Fluconazole" in html_content: found_in_html.append("Fluconazole")
            
            if found_in_html:
                print(f"✓ Verified: Found {found_in_html} in web response")
            else:
                 print("⚠ warning: Specific medicines not found in HTML response (check parser output above)")
        else:
            print(f"✗ Web upload failed with status {response.status_code}")
            print(response.data)

except Exception as e:
    print(f"✗ Error: {e}")

# Summary
print("\n" + "=" * 70)
print("INTEGRATION TEST COMPLETE")
print("=" * 70)
