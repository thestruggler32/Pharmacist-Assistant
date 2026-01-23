from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime

from utils.auth import role_required, get_current_user
from utils.image_preprocessor import ImagePreprocessor
from utils.ocr_engine import OCREngine
from utils.prescription_parser import PrescriptionParser
from utils.correction_store import CorrectionStore
from utils.correction_learner import CorrectionLearner

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

preprocessor = ImagePreprocessor()
ocr_engine = OCREngine()
parser = PrescriptionParser()
correction_store = CorrectionStore()
correction_learner = CorrectionLearner()

prescriptions = {}


@app.route('/')
def index():
    user = get_current_user()
    return render_template('base.html', user=user)


@app.route('/upload', methods=['GET', 'POST'])
@role_required(['pharmacist'])
def upload():
    user = get_current_user()
    
    if request.method == 'POST':
        if 'prescription_image' not in request.files:
            return "No file uploaded", 400
        
        file = request.files['prescription_image']
        if file.filename == '':
            return "No file selected", 400
        
        # Check if handwriting mode is enabled
        handwriting_mode = request.form.get('handwriting_mode') == 'on'
        
        filename = secure_filename(file.filename)
        prescription_id = str(uuid.uuid4())
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{prescription_id}_{filename}")
        file.save(filepath)
        
        # Use appropriate preprocessing mode
        preprocessor_mode = ImagePreprocessor(handwriting_mode=handwriting_mode)
        preprocessed_path, quality_report = preprocessor_mode.preprocess(filepath)
        
        # Save preprocessed image
        preprocessed_filename = f"{prescription_id}_preprocessed.jpg"
        preprocessed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], preprocessed_filename)
        preprocessor_mode.save_preprocessed_image(preprocessed_path, preprocessed_filepath)
        
        # Run OCR
        ocr_results = ocr_engine.extract_text(preprocessed_filepath)
        
        # Use lenient parser for handwriting mode
        parser_mode = PrescriptionParser(lenient_mode=handwriting_mode)
        parsed_medicines = parser_mode.parse(ocr_results)
        
        prescriptions[prescription_id] = {
            'id': prescription_id,
            'image_path': filepath,
            'preprocessed_path': preprocessed_filepath,
            'ocr_results': ocr_results,
            'parsed_medicines': parsed_medicines,
            'status': 'pending',
            'uploaded_at': datetime.now().isoformat(),
            'handwriting_mode': handwriting_mode,
            'quality_report': quality_report
        }
        
        return redirect(url_for('review', prescription_id=prescription_id))
    
    return render_template('upload.html', user=user)


@app.route('/review/<prescription_id>', methods=['GET', 'POST'])
@role_required(['pharmacist'])
def review(prescription_id):
    user = get_current_user()
    
    if prescription_id not in prescriptions:
        return "Prescription not found", 404
    
    prescription = prescriptions[prescription_id]
    
    if request.method == 'POST':
        selected_region = request.form.get('selected_region', 'Karnataka')
        
        for i, medicine in enumerate(prescription['parsed_medicines']):
            corrected_name = request.form.get(f'medicine_name_{i}', '')
            corrected_strength = request.form.get(f'strength_{i}', '')
            corrected_dosage = request.form.get(f'dosage_{i}', '')
            
            if corrected_name != medicine['medicine_name'] or \
               corrected_strength != medicine['strength'] or \
               corrected_dosage != medicine['dosage']:
                
                correction_data = {
                    'original_ocr_text': medicine['original_text'],
                    'corrected_fields': {
                        'medicine_name': corrected_name,
                        'strength': corrected_strength,
                        'dosage': corrected_dosage
                    },
                    'original_confidence': medicine['confidence'],
                    'pharmacist_id': user.get('name', 'Unknown'),
                    'timestamp': datetime.now().isoformat(),
                    'image_reference': prescription_id
                }
                correction_store.save_correction(correction_data)
                
                medicine['medicine_name'] = corrected_name
                medicine['strength'] = corrected_strength
                medicine['dosage'] = corrected_dosage
        
        return redirect(url_for('approve', prescription_id=prescription_id))
    
    return render_template('review.html', prescription=prescription, user=user)


@app.route('/api/medicine-suggestions')
def medicine_suggestions():
    """API endpoint for medicine suggestions"""
    query = request.args.get('query', '')
    region = request.args.get('region', 'All')
    
    if not query or len(query) < 2:
        return jsonify({'suggestions': []})
    
    try:
        suggestions = correction_learner.suggest_correction(query, region=region, threshold=0.6)
        return jsonify({'suggestions': suggestions})
    except Exception as e:
        print(f"Error in medicine suggestions: {e}")
        return jsonify({'suggestions': [], 'error': str(e)})


@app.route('/approve/<prescription_id>', methods=['GET', 'POST'])
@role_required(['pharmacist'])
def approve(prescription_id):
    user = get_current_user()
    
    if prescription_id not in prescriptions:
        return "Prescription not found", 404
    
    if request.method == 'POST':
        prescriptions[prescription_id]['status'] = 'approved'
        prescriptions[prescription_id]['approved_by'] = user.get('name', 'Unknown')
        prescriptions[prescription_id]['approved_at'] = datetime.now().isoformat()
        return redirect(url_for('patient_view', prescription_id=prescription_id))
    
    prescription = prescriptions[prescription_id]
    return render_template('approve.html', prescription=prescription, user=user)


@app.route('/patient/<prescription_id>')
@role_required(['patient', 'pharmacist'])
def patient_view(prescription_id):
    user = get_current_user()
    
    if prescription_id not in prescriptions:
        return "Prescription not found", 404
    
    prescription = prescriptions[prescription_id]
    
    if prescription['status'] != 'approved' and user.get('role') == 'patient':
        return "Prescription not yet approved", 403
    
    return render_template('patient_view.html', prescription=prescription, user=user)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
