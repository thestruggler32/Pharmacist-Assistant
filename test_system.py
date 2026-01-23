"""
Test script for the AI Prescription Assistant system
Tests each component individually
"""

import sys
import os

# Test 1: Image Preprocessor
print("=" * 60)
print("TEST 1: Image Preprocessor")
print("=" * 60)

try:
    from utils.image_preprocessor import ImagePreprocessor
    preprocessor = ImagePreprocessor()
    
    test_image = "filled-medical-prescription-isolated-on-260nw-144551783.webp"
    if os.path.exists(test_image):
        result = preprocessor.preprocess(test_image)
        if result:
            print(f"✓ Preprocessing successful: {result}")
        else:
            print("✗ Preprocessing failed")
    else:
        print(f"⚠ Test image not found: {test_image}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: OCR Engine
print("\n" + "=" * 60)
print("TEST 2: OCR Engine")
print("=" * 60)

try:
    from utils.ocr_engine import OCREngine
    ocr_engine = OCREngine()
    
    test_image = "filled-medical-prescription-isolated-on-260nw-144551783.webp"
    if os.path.exists(test_image):
        results = ocr_engine.extract_text(test_image)
        print(f"✓ OCR extracted {len(results)} text items")
        for i, item in enumerate(results[:3]):  # Show first 3
            print(f"  {i+1}. Text: {item['text'][:50]}... | Confidence: {item['confidence']:.2f}")
    else:
        print(f"⚠ Test image not found: {test_image}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Prescription Parser
print("\n" + "=" * 60)
print("TEST 3: Prescription Parser")
print("=" * 60)

try:
    from utils.prescription_parser import PrescriptionParser
    parser = PrescriptionParser()
    
    # Test with sample OCR data
    sample_ocr = [
        {"text": "Paracetamol 500mg BID", "confidence": 0.95, "bbox": []},
        {"text": "Amoxicillin 250mg TID", "confidence": 0.85, "bbox": []},
        {"text": "Patient Name: John Doe", "confidence": 0.90, "bbox": []},
        {"text": "Ibuprofen 400mg 1-0-1", "confidence": 0.45, "bbox": []},
    ]
    
    medicines = parser.parse(sample_ocr)
    print(f"✓ Parser found {len(medicines)} medicines")
    for med in medicines:
        print(f"  - {med['medicine_name']} | {med['strength']} | {med['dosage']} | Risk: {med['risk_level']}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: Correction Store
print("\n" + "=" * 60)
print("TEST 4: Correction Store")
print("=" * 60)

try:
    from utils.correction_store import CorrectionStore
    store = CorrectionStore()
    
    # Test save
    test_correction = {
        "original_ocr_text": "Paracetmol 500mg",
        "corrected_fields": {
            "medicine_name": "Paracetamol",
            "strength": "500mg",
            "dosage": "BID"
        },
        "original_confidence": 0.75,
        "pharmacist_id": "test_pharma",
        "image_reference": "test_001"
    }
    
    success = store.save_correction(test_correction)
    if success:
        print("✓ Correction saved successfully")
    else:
        print("✗ Failed to save correction")
    
    # Test load
    corrections = store.load_all_corrections()
    print(f"✓ Loaded {len(corrections)} corrections from store")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 5: Correction Learner
print("\n" + "=" * 60)
print("TEST 5: Correction Learner")
print("=" * 60)

try:
    from utils.correction_learner import CorrectionLearner
    learner = CorrectionLearner()
    
    # Test suggestion
    suggestion, confidence = learner.suggest_correction("Paracetmol 500mg")
    if suggestion:
        print(f"✓ Suggestion: '{suggestion}' (confidence: {confidence:.2f})")
    else:
        print("⚠ No suggestion found (expected if no corrections stored)")
    
    # Test dosage patterns
    patterns = learner.get_common_dosage_patterns()
    print(f"✓ Common dosage patterns: {patterns[:5] if patterns else 'None yet'}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 6: Database
print("\n" + "=" * 60)
print("TEST 6: Database")
print("=" * 60)

try:
    import sqlite3
    conn = sqlite3.connect('database/pharmacy.db')
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"✓ Database tables: {[t[0] for t in tables]}")
    
    # Check medicines
    cursor.execute("SELECT COUNT(*) FROM medicines")
    count = cursor.fetchone()[0]
    print(f"✓ Medicines in database: {count}")
    
    # Check users
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    print(f"✓ Users in database: {count}")
    
    conn.close()
except Exception as e:
    print(f"✗ Error: {e}")

# Summary
print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print("All core components tested.")
print("Run 'python app.py' to start the Flask application.")
print("=" * 60)
