# AI Prescription Assistant

A safety-critical handwritten prescription OCR and interpretation system with mandatory human-in-the-loop verification.

## ⚠️ Safety Principles

1. **Pharmacist is Final Authority**: All OCR results require mandatory pharmacist verification before finalization
2. **No Autonomous Decisions**: System assists but does NOT make autonomous medical decisions
3. **No Automatic ML Training**: Learning from corrections uses rule-based improvements only (fuzzy matching, misspelling mappings)
4. **Transparency**: All corrections are logged with pharmacist ID and timestamp

## 🏗️ System Architecture

```
┌─────────────────┐
│ Image Upload    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Preprocessing   │ (OpenCV: grayscale, resize, threshold)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ OCR Engine      │ (PaddleOCR: text extraction + confidence)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Rule Parser     │ (Header removal, medicine detection)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Pharmacist      │ (Review, correct, approve)
│ Verification    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Approved Rx     │
└─────────────────┘
```

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. Clone the repository
```bash
cd "Pharmacist Assistant"
```

2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Initialize database
```bash
python database/init_db.py
python database/load_medicines.py
```

5. Create required directories
```bash
mkdir static\uploads
mkdir data
```

6. Run the application
```bash
python app.py
```

7. Access at `http://localhost:5000`

## 👥 User Roles

### Admin
- **Username**: admin
- **Password**: admin123
- **Capabilities**:
  - Approve/reject user registrations
  - View correction logs
  - Monitor system statistics

### Pharmacist
- Upload prescription images
- Review OCR results with color-coded confidence
- Correct parsing errors
- Approve final prescriptions
- View alternative medicine brands

### Doctor
- View prescriptions they issued (read-only)
- No editing or approval permissions

### Patient
- View approved prescriptions only
- No editing capabilities

## 🔐 Role-Based Access Control

| Action | Admin | Pharmacist | Doctor | Patient |
|--------|-------|------------|--------|---------|
| Upload Prescription | ❌ | ✅ | ❌ | ❌ |
| Review OCR Results | ❌ | ✅ | ❌ | ❌ |
| Correct Medicines | ❌ | ✅ | ❌ | ❌ |
| Approve Prescription | ❌ | ✅ | ❌ | ❌ |
| View Own Prescriptions | ❌ | ✅ | ✅ | ✅ |
| Approve Users | ✅ | ❌ | ❌ | ❌ |
| View Correction Logs | ✅ | ✅ | ❌ | ❌ |

## 🎨 Confidence Color Coding

- 🟢 **Green** (> 0.8): High confidence - auto-accept recommended
- 🟡 **Yellow** (0.5 - 0.8): Medium confidence - review recommended
- 🔴 **Red** (< 0.5): Low confidence - **mandatory correction required**

## 📋 Usage Guide

### For Pharmacists

1. **Login** with pharmacist credentials
2. **Upload** prescription image
3. **Review** OCR results:
   - Green items: Verify accuracy
   - Yellow items: Review carefully
   - Red items: Correct before approval
4. **Edit** any incorrect fields inline
5. **View alternatives** for generic substitutions
6. **Approve** prescription (disabled until all red items corrected)

### For Patients

1. **Login** with patient credentials
2. **View** approved prescriptions
3. **Read** medicine instructions
4. **Report** adverse reactions (if applicable)

### For Admins

1. **Login** with admin credentials
2. **Approve** pending pharmacist/doctor registrations
3. **Monitor** correction logs
4. **Review** system statistics

## 🧪 Testing

### Test Image Preprocessing
```bash
python -c "from utils.image_preprocessor import ImagePreprocessor; p = ImagePreprocessor(); p.preprocess('test_prescription.jpg')"
```

### Test OCR Engine
```bash
python -c "from utils.ocr_engine import OCREngine; ocr = OCREngine(); print(ocr.extract_text('test_prescription.jpg'))"
```

### Test Parser
```bash
python -c "from utils.prescription_parser import PrescriptionParser; parser = PrescriptionParser(); print(parser.parse([{'text': 'Paracetamol 500mg BID', 'confidence': 0.9, 'bbox': []}]))"
```

## 📊 Database Schema

### Users Table
- id, username, password_hash, role, license_number, status, created_at

### Prescriptions Table
- id, patient_name, uploaded_by, image_path, ocr_data, approved_data, status, created_at, approved_at

### Medicines Table
- id, generic_name, brand_name, strength, region, created_at

### Corrections Table
- id, prescription_id, original_text, corrected_text, pharmacist_id, timestamp

## 🔒 Security Notes

- **Demo System**: Uses hardcoded users for demonstration
- **Production**: Implement proper authentication (OAuth, JWT)
- **HTTPS**: Deploy with SSL/TLS in production
- **Input Validation**: All user inputs are sanitized
- **Audit Trail**: All corrections logged with pharmacist ID

## ⚠️ Limitations

1. **Demo Medicine Database**: Limited to ~30 medicines for Karnataka region
2. **No Real-time Availability**: Alternative suggestions don't check pharmacy stock
3. **No ML Training**: System uses rule-based learning only
4. **Image Quality**: Requires reasonably clear handwritten prescriptions
5. **Language**: English only (PaddleOCR configured for English)

## 🚀 Future Enhancements

- Multi-language support
- Real-time pharmacy inventory integration
- Mobile app for prescription upload
- Barcode/QR code generation for prescriptions
- Integration with electronic health records (EHR)
- Advanced ML models with pharmacist-supervised training

## 📝 License

This is a demo/educational project. Not for production medical use without proper validation and regulatory approval.

## 🤝 Contributing

This is a safety-critical healthcare system. All contributions must:
1. Maintain human-in-the-loop verification
2. Include comprehensive testing
3. Follow medical software best practices
4. Document all changes in audit logs

## 📞 Support

For issues or questions, please refer to the project documentation or contact the development team.

---

**DISCLAIMER**: This system assists pharmacists and does not replace professional medical judgment. All prescriptions must be verified by licensed pharmacists before dispensing.
