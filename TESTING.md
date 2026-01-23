# AI Prescription Assistant - Testing Guide

## Quick Start Testing

### 1. Initialize System
```bash
# Initialize database
python database/init_db.py

# Load medicine database
python database/load_medicines.py

# Run comprehensive tests
python test_system.py
```

### 2. Start Application
```bash
python app.py
```

Access at: `http://localhost:5000`

## Test Users

### Admin Account
- **Username**: admin
- **Password**: admin123
- **Access**: User management, correction logs

### Demo Pharmacist (Hardcoded)
- **User ID**: pharma_001
- **Role**: pharmacist
- **Access**: Upload, review, approve prescriptions

### Demo Doctor (Hardcoded)
- **User ID**: doctor_001
- **Role**: doctor
- **Access**: View prescriptions (read-only)

### Demo Patient (Hardcoded)
- **User ID**: patient_001
- **Role**: patient
- **Access**: View approved prescriptions only

## End-to-End Workflow Test

### Step 1: Upload Prescription (Pharmacist)
1. Navigate to `/upload?user_id=pharma_001`
2. Upload test image: `filled-medical-prescription-isolated-on-260nw-144551783.webp`
3. System processes: Preprocessing → OCR → Parsing
4. Redirects to review page

### Step 2: Review OCR Results (Pharmacist)
1. View color-coded medicines:
   - 🟢 Green: High confidence (>0.8)
   - 🟡 Yellow: Medium confidence (0.5-0.8)
   - 🔴 Red: Low confidence (<0.5) - **Must correct**
2. Edit any incorrect fields
3. Click "Save Corrections and Continue"

### Step 3: Approve Prescription (Pharmacist)
1. Review final medicine list
2. Confirm accuracy
3. Click "Approve and Finalize"
4. Prescription status changes to "approved"

### Step 4: View as Patient
1. Navigate to `/patient/<prescription_id>?user_id=patient_001`
2. View approved prescription (read-only)
3. No editing capabilities

## Component Tests

### Test 1: Image Preprocessing
```bash
python -c "from utils.image_preprocessor import ImagePreprocessor; p = ImagePreprocessor(); print(p.preprocess('filled-medical-prescription-isolated-on-260nw-144551783.webp'))"
```

**Expected**: Preprocessed image path returned

### Test 2: OCR Engine
```bash
python -c "from utils.ocr_engine import OCREngine; ocr = OCREngine(); results = ocr.extract_text('filled-medical-prescription-isolated-on-260nw-144551783.webp'); print(f'Extracted {len(results)} text items')"
```

**Expected**: List of text items with confidence scores

### Test 3: Prescription Parser
```bash
python -c "from utils.prescription_parser import PrescriptionParser; parser = PrescriptionParser(); medicines = parser.parse([{'text': 'Paracetamol 500mg BID', 'confidence': 0.9, 'bbox': []}]); print(medicines)"
```

**Expected**: Parsed medicine with name, strength, dosage, risk level

### Test 4: Correction Store
```bash
python -c "from utils.correction_store import CorrectionStore; store = CorrectionStore(); corrections = store.load_all_corrections(); print(f'Loaded {len(corrections)} corrections')"
```

**Expected**: List of stored corrections

### Test 5: Database
```bash
python -c "import sqlite3; conn = sqlite3.connect('database/pharmacy.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM medicines'); print(f'Medicines: {cursor.fetchone()[0]}'); conn.close()"
```

**Expected**: Count of medicines in database (~30)

## Role-Based Access Control Tests

### Test Pharmacist Access
- ✅ Can upload prescriptions
- ✅ Can review OCR results
- ✅ Can correct medicines
- ✅ Can approve prescriptions
- ❌ Cannot manage users

### Test Doctor Access
- ✅ Can view prescriptions
- ❌ Cannot upload prescriptions
- ❌ Cannot approve prescriptions
- ❌ Cannot manage users

### Test Patient Access
- ✅ Can view approved prescriptions
- ❌ Cannot view pending prescriptions
- ❌ Cannot edit prescriptions
- ❌ Cannot upload prescriptions

### Test Admin Access
- ✅ Can manage users
- ✅ Can view correction logs
- ❌ Cannot upload prescriptions
- ❌ Cannot approve prescriptions

## Validation Tests

### Test 1: Red Item Approval Block
1. Upload prescription with low confidence items
2. Try to approve without corrections
3. **Expected**: Validation prevents approval

### Test 2: Correction Logging
1. Make corrections to OCR results
2. Check `data/corrections.json`
3. **Expected**: Corrections logged with timestamp and pharmacist ID

### Test 3: Image Quality Detection
1. Upload very blurry/dark image
2. **Expected**: Quality warning displayed

### Test 4: Empty Medicine Detection
1. Upload non-prescription image
2. **Expected**: "No medicines detected" message

## Performance Tests

### OCR Processing Time
- **Target**: < 5 seconds for typical prescription
- **Test**: Upload and measure time to review page

### Database Query Performance
- **Target**: < 100ms for medicine lookup
- **Test**: Search alternatives for common medicine

## Security Tests

### Test 1: Role Enforcement
```bash
# Try to access pharmacist route as patient
curl http://localhost:5000/upload?user_id=patient_001
```
**Expected**: 403 Forbidden

### Test 2: File Upload Validation
- Upload non-image file
- **Expected**: Rejection or error handling

### Test 3: SQL Injection Prevention
- Try malicious input in forms
- **Expected**: Sanitized and safe

## Known Limitations (Expected Behavior)

1. **Demo Authentication**: Hardcoded users, no real login
2. **Limited Medicine Database**: ~30 medicines for Karnataka region
3. **No Real-time Availability**: Alternative suggestions don't check stock
4. **English Only**: PaddleOCR configured for English text
5. **Image Quality Dependent**: Requires reasonably clear handwriting

## Troubleshooting

### Issue: OCR returns empty results
- **Solution**: Check image quality, try preprocessing

### Issue: No medicines detected
- **Solution**: Verify prescription contains medicine indicators (mg, ml, BID, etc.)

### Issue: Database error
- **Solution**: Run `python database/init_db.py` again

### Issue: Import errors
- **Solution**: Install dependencies: `pip install -r requirements.txt`

### Issue: PaddleOCR errors
- **Solution**: Reinstall: `pip uninstall paddleocr paddlepaddle && pip install paddleocr==2.7.0`

## Success Criteria

✅ All components pass individual tests
✅ End-to-end workflow completes successfully
✅ Role-based access control enforced
✅ Corrections logged properly
✅ Color-coded confidence indicators display correctly
✅ Pharmacist can approve prescriptions
✅ Patients can view approved prescriptions only

## Next Steps After Testing

1. Review correction logs for patterns
2. Update parser rules based on corrections
3. Expand medicine database
4. Implement proper authentication
5. Add more comprehensive error handling
6. Deploy with HTTPS for production use

---

**Remember**: This is a safety-critical system. All prescriptions must be verified by licensed pharmacists before dispensing.
