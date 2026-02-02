from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
import sys

# Force stdout to flush immediately for debugging
sys.stdout.flush()

# Load environment variables
load_dotenv()

# Database and annotation imports (optional - for new features)
prescription_db = None
create_annotated_image = None
create_digitized_image = None
calculate_confidence_from_medicines = None

try:
    from database.prescription_db import prescription_db
    from utils.annotation_utils import create_annotated_image, create_digitized_image, calculate_confidence_from_medicines
    print("✓ Annotation and approval features loaded", flush=True)
except ImportError as e:
    print(f"⚠ Annotation features disabled (missing imports): {e}", flush=True)

# Keep existing utils imports
try:
    from utils.image_preprocessor import ImagePreprocessor
    from utils.ocr_engine import OCREngine, MistralOnlyEngine
    from utils.prescription_parser import PrescriptionParser
    from utils.correction_store import CorrectionStore
    from utils.correction_learner import CorrectionLearner
except ImportError as e:
    print(f"Warning: Import error {e}. Check directory structure.", flush=True)

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# JWT Setup
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-pharmacist')
jwt = JWTManager(app)

# JWT Error Handlers for debugging
@jwt.invalid_token_loader
def invalid_token_callback(error_string):
    print(f"JWT ERROR - Invalid token: {error_string}", flush=True)
    return jsonify({'msg': 'Invalid token', 'error': error_string}), 422

@jwt.unauthorized_loader
def unauthorized_callback(error_string):
    print(f"JWT ERROR - Missing token: {error_string}", flush=True)
    return jsonify({'msg': 'Missing Authorization Header', 'error': error_string}), 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    print(f"JWT ERROR - Token expired", flush=True)
    return jsonify({'msg': 'Token has expired'}), 401

app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Utils
try:
    hybrid_ocr = MistralOnlyEngine()
    correction_store = CorrectionStore()
except Exception as e:
    print(f"Error initializing engines: {e}")

# Mock Database
PRESCRIPTIONS = {}
USERS = {
    # Multiple Patient Accounts
    'patient1@test.com': {
        'password': 'password', 
        'role': 'patient', 
        'name': 'John Doe',
        'patient_id': 'P001',
        'locality': 'Indiranagar, Bangalore'
    },
    'patient2@test.com': {
        'password': 'password', 
        'role': 'patient', 
        'name': 'Jane Smith',
        'patient_id': 'P002',
        'locality': 'Whitefield, Bangalore'
    },
    'patient3@test.com': {
        'password': 'password', 
        'role': 'patient', 
        'name': 'Rajesh Kumar',
        'patient_id': 'P003',
        'locality': 'Koramangala, Bangalore'
    },
    
    # Doctor Account
    'doctor@test.com': {
        'password': 'password', 
        'role': 'doctor', 
        'name': 'Dr. Aisha Patel', 
        'reg_no': 'MED12345'
    },
    
    # Pharmacist Account
    'pharmacist@test.com': {
        'password': 'password', 
        'role': 'pharmacist', 
        'name': 'Pharma Joe', 
        'license': '20B/KA/2024', 
        'license_verified': True
    }
}

# --- Routes ---

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "Backend is running"})

@app.route('/api/login', methods=['POST'])
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    user = USERS.get(email)
    if user and user['password'] == password:
        # JWT identity must be a string (email), additional data goes in claims
        access_token = create_access_token(
            identity=email,
            additional_claims={'role': user['role'], 'name': user['name']}
        )
        return jsonify({
            'access_token': access_token, 
            'role': user['role'], 
            'name': user['name'],
            'license_verified': user.get('license_verified', False)
        })
    
    return jsonify({"msg": "Invalid email or password"}), 401

@app.route('/api/verify-license', methods=['POST'])
def verify_license():
    # Mock External API call (IDfy / Surepass)
    # No JWT required - this is called during login flow
    data = request.json
    license_no = data.get('license_no')
    
    # Mock logic: if license starts with 'VALID', return success
    is_valid = license_no and license_no.upper().startswith('VALID')
    # Default to True for demo if not specified
    if not license_no: is_valid = True 

    return jsonify({
        "verified": is_valid,
        "details": "Verified against Surepass API (Mock)" if is_valid else "Invalid License"
    })

@app.route('/api/ocr/upload', methods=['POST'])
@jwt_required()
def upload_prescription():
    print("========== UPLOAD REQUEST RECEIVED ==========", flush=True)
    print(f"Request method: {request.method}", flush=True)
    print(f"Request files: {request.files}", flush=True)
    print(f"Request headers: {dict(request.headers)}", flush=True)
    
    current_user_email = get_jwt_identity()  # Returns email string
    claims = get_jwt()  # Returns the full JWT with claims
    user_role = claims.get('role', '')
    print(f"Current user: {current_user_email}, Role: {user_role}", flush=True)
    
    # Get patient_email from formdata (for doctors/pharmacists)
    patient_email = request.form.get('patient_email', None)
    prescription_owner = patient_email if patient_email else current_user_email
    
    if user_role not in ['patient', 'pharmacist', 'doctor']:
        return jsonify({"msg": "Unauthorized"}), 403

    if 'file' not in request.files:
        return jsonify({"msg": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"msg": "No selected file"}), 400

    filename = secure_filename(file.filename)
    prescription_id = str(uuid.uuid4())
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{prescription_id}_{filename}")
    file.save(filepath)

    try:
        # Use Mistral Hybrid Engine
        print(f"Processing {filepath}...")
        print(f"File exists: {os.path.exists(filepath)}")
        print(f"File size: {os.path.getsize(filepath) if os.path.exists(filepath) else 'N/A'}")
        
        # OCR Processing - Gemini 2.5 Pro (Free Unlimited)
        print(f"\nDEBUG: Starting Gemini OCR processing for {file.filename}", flush=True)
        sys.stdout.flush()
        
        from utils.gemini_ocr_engine import GeminiOCREngine
        ocr_engine = GeminiOCREngine()
        
        medicines = ocr_engine.extract_medicines(filepath)
        print(f"DEBUG: OCR returned {len(medicines)} medicines", flush=True)
        
        prescription_data = {
            'id': prescription_id,
            'patient_id': prescription_owner,  # FIXED: Who owns this prescription
            'issued_by': current_user_email,   # Who created/uploaded it
            'type': 'scanned',  # scanned vs digital
            'image_url': f"/static/uploads/{prescription_id}_{filename}", 
            'medicines': medicines,
            'status': 'pending',  # ALL prescriptions start as pending
            'uploaded_by': current_user_email,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save to in-memory dict
        PRESCRIPTIONS[prescription_id] = prescription_data
        
        # Also save to persistent database if available
        if prescription_db:
            try:
                prescription_db.save_prescription(prescription_id, prescription_data)
                print(f"✓ Saved to prescription_db: {prescription_id}", flush=True)
            except Exception as e:
                print(f"⚠ Failed to save to prescription_db: {e}", flush=True)
        
        return jsonify(prescription_data)

    except Exception as e:
        print(f"OCR Failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"msg": f"Processing failed: {str(e)}"}), 500

# List all prescriptions (for Dashboard)
@app.route('/api/prescriptions', methods=['GET'])
@jwt_required()
def list_prescriptions():
    """Get all prescriptions for the current user"""
    current_user = get_jwt_identity()
    claims = get_jwt()
    user_role = claims.get('role', '')
    
    # If prescription_db exists, try to get from there
    # RBAC: Filter prescriptions by role
    if prescription_db:
        try:
            all_prescriptions = prescription_db.get_all_prescriptions()
        except Exception as e:
            print(f"⚠ prescription_db.get_all failed: {e}", flush=True)
            all_prescriptions = PRESCRIPTIONS
    else:
        all_prescriptions = PRESCRIPTIONS
    
    # Filter based on role
    if user_role == 'patient':
        # Patients see only THEIR prescriptions
        filtered = {k: v for k, v in all_prescriptions.items() 
                   if v.get('patient_id') == current_user}
    elif user_role == 'doctor':
        # Doctors see prescriptions THEY issued
        filtered = {k: v for k, v in all_prescriptions.items() 
                   if v.get('issued_by') == current_user}
    elif user_role == 'pharmacist':
        # Pharmacists see ALL prescriptions
        filtered = all_prescriptions
    else:
        filtered = {}
    
    return jsonify({"prescriptions": list(filtered.values())})

@app.route('/api/prescriptions/<id>', methods=['GET'])
@jwt_required()
def get_prescription(id):
    # Check prescription_db first, fallback to in-memory
    if prescription_db:
        try:
            p = prescription_db.get_prescription(id)
            if p:
                return jsonify(p)
        except Exception as e:
            print(f"⚠ prescription_db.get failed: {e}", flush=True)
    
    # Fallback to in-memory
    p = PRESCRIPTIONS.get(id)
    if not p:
        return jsonify({"msg": "Not found"}), 404
    return jsonify(p)

# New approve/reject endpoints for human-in-loop
@app.route('/api/prescriptions/<id>/approve', methods=['POST'])
@jwt_required()
def approve_prescription(id):
    """Pharmacist approves prescription after reviewing/editing medicines"""
    current_user = get_jwt_identity()
    claims = get_jwt()
    
    # RBAC: Only pharmacists can approve
    if claims.get('role') != 'pharmacist':
        return jsonify({"msg": "Unauthorized - Only pharmacists can approve prescriptions"}), 403
    
    data = request.json
    edited_medicines = data.get('medicines', [])
    
    # Track corrections for feedback loop
    original_prescription = PRESCRIPTIONS.get(id)
    if original_prescription:
        try:
            from utils.correction_feedback import correction_feedback
            original_meds = original_prescription.get('medicines', [])
            if len(original_meds) == len(edited_medicines):
                correction_feedback.batch_add_corrections(
                    id, original_meds, edited_medicines, current_user
                )
        except Exception as e:
            print(f"⚠ Correction feedback error: {e}", flush=True)
    
    # Update in-memory
    if id in PRESCRIPTIONS:
        PRESCRIPTIONS[id]['medicines'] = edited_medicines
        PRESCRIPTIONS[id]['status'] = 'approved'
        PRESCRIPTIONS[id]['approved_by'] = current_user
        PRESCRIPTIONS[id]['approved_at'] = datetime.now().isoformat()
    
    # Update in database
    if prescription_db:
        try:
            prescription_db.update_prescription(id, {
                'medicines': edited_medicines,
                'status': 'approved',
                'approved_by': current_user,
                'approved_at': datetime.now().isoformat()
            })
            print(f"✓ Approved prescription {id} by {current_user}", flush=True)
        except Exception as e:
            print(f"⚠ Failed to save approval to prescription_db: {e}", flush=True)
    
    return jsonify({"msg": "Prescription approved", "status": "approved"})

@app.route('/api/prescriptions/<id>/reject', methods=['POST'])
@jwt_required()
def reject_prescription(id):
    """Pharmacist rejects prescription"""
    current_user = get_jwt_identity()
    claims = get_jwt()
    
    if claims.get('role') not in ['pharmacist']:
        return jsonify({"msg": "Unauthorized - Pharmacists only"}), 403
    
    data = request.json
    reason = data.get('reason', 'No reason provided')
    
    # Update in-memory
    if id in PRESCRIPTIONS:
        PRESCRIPTIONS[id]['status'] = 'rejected'
        PRESCRIPTIONS[id]['rejected_by'] = current_user
        PRESCRIPTIONS[id]['rejection_reason'] = reason
        PRESCRIPTIONS[id]['rejected_at'] = datetime.now().isoformat()
    
    # Update in database
    if prescription_db:
        try:
            prescription_db.update_prescription(id, {
                'status': 'rejected',
                'rejected_by': current_user,
                'rejection_reason': reason,
                'rejected_at': datetime.now().isoformat()
            })
            print(f"✓ Rejected prescription {id} by {current_user}", flush=True)
        except Exception as e:
            print(f"⚠ Failed to save rejection to prescription_db: {e}", flush=True)
    
    return jsonify({"msg": "Prescription rejected", "status": "rejected"})


# Doctor Digital Prescription Issuance
@app.route('/api/prescriptions/issue', methods=['POST'])
@jwt_required()
def issue_prescription():
    """Doctor issues digital prescription to a patient"""
    current_user = get_jwt_identity()
    claims = get_jwt()
    
    # RBAC: Only doctors can issue prescriptions
    if claims.get('role') != 'doctor':
        return jsonify({"msg": "Unauthorized - Only doctors can issue prescriptions"}), 403
    
    data = request.json
    patient_email = data.get('patient_email')
    medicines = data.get('medicines', [])
    notes = data.get('notes', '')
    
    if not patient_email:
        return jsonify({"msg": "Patient email required"}), 400
    
    # Verify patient exists
    if patient_email not in USERS or USERS[patient_email]['role'] != 'patient':
        return jsonify({"msg": "Invalid patient email"}), 400
    
    prescription_id = str(uuid.uuid4())
    prescription_data = {
        'id': prescription_id,
        'patient_id': patient_email,      # For the patient
        'issued_by': current_user,         # By this doctor
        'type': 'digital',                 # Not scanned
        'medicines': medicines,
        'status': 'pending',
        'notes': notes,
        'timestamp': datetime.now().isoformat(),
        'image_url': None,  # No image for digital prescriptions
        'doctor_name': claims.get('name', 'Doctor')
    }
    
    PRESCRIPTIONS[prescription_id] = prescription_data
    
    if prescription_db:
        try:
            prescription_db.save_prescription(prescription_id, prescription_data)
            print(f"✓ Doctor issued prescription {prescription_id} to {patient_email}", flush=True)
        except Exception as e:
            print(f"⚠ Failed to save to prescription_db: {e}", flush=True)
    
    return jsonify({
        "msg": "Prescription issued successfully",
        "prescription_id": prescription_id,
        "prescription": prescription_data
    })


# Annotation Endpoint
@app.route('/api/prescriptions/<id>/annotate', methods=['POST'])
@jwt_required()
def add_annotation(id):
    """Save bounding box annotations for prescription"""
    if not prescription_db:
        return jsonify({"msg": "Annotation features not available"}), 503
    
    current_user = get_jwt_identity()
    data = request.json
    
    try:
        annotations = data.get('annotations', [])
        prescription_db.add_annotation(id, {
            'annotations': annotations,
            'annotated_by': current_user
        })
        return jsonify({"msg": "Annotations saved successfully"})
    except Exception as e:
        print(f"Annotation save error: {e}", flush=True)
        return jsonify({"msg": "Failed to save annotations"}), 500

@app.route('/api/translate', methods=['POST'])
def translate_text():
    data = request.json
    text = data.get('text')
    target = data.get('target', 'hi')
    
    try:
        from googletrans import Translator
        translator = Translator()
        result = translator.translate(text, dest=target)
        return jsonify({'translatedText': result.text})
    except Exception as e:
        print(f"Translation Error (using mock): {e}")
        # Mock translation for demo
        mock_map = {
            "Paracetamol": "पैरासिटामोल",
            "Dolo 650": "डोलो 650",
            "Morning": "सुबह",
            "Night": "रात"
        }
        translated = mock_map.get(text, text + f" ({target})")
        return jsonify({'translatedText': translated})

@app.route('/api/medicines/alternatives', methods=['POST'])
@jwt_required()
def get_alternatives():
    data = request.json
    medicine_name = data.get('medicine_name')
    client_locality = data.get('locality')
    client_region = data.get('region', 'Karnataka')
    
    current_user_email = get_jwt_identity()
    # Get user profile safely
    user_data = USERS.get(current_user_email, {})
    
    # Priority: Params > User Profile > Default
    locality = client_locality or user_data.get('locality')
    
    if not medicine_name:
        return jsonify({"msg": "Medicine name required"}), 400
        
    try:
        from utils.regional_alternatives import regional_mapper
        result = regional_mapper.find_alternatives(
            medicine_name, 
            user_region=client_region,
            locality=locality
        )
        return jsonify(result)
    except Exception as e:
        print(f"Alternatives error: {e}")
        return jsonify({"msg": "Failed to fetch alternatives"}), 500

@app.route('/api/approvals', methods=['GET'])
@jwt_required()
def get_approvals():
    """Get pending approval requests"""
    if not prescription_db:
        return jsonify({"approvals": [], "count": 0})
    
    current_user = get_jwt_identity()
    pharmacist_id = current_user.get('email') if current_user.get('role') == 'pharmacist' else None
    approvals = prescription_db.get_pending_approvals(pharmacist_id)
    
    enriched_approvals = []
    for approval in approvals:
        prescription = prescription_db.get_prescription(approval['prescription_id'])
        enriched_approvals.append({**approval, 'prescription': prescription})
    
    return jsonify({"approvals": enriched_approvals, "count": len(enriched_approvals)})

@app.route('/api/approvals/<approval_id>/submit', methods=['POST'])
@jwt_required()
def submit_approval(approval_id):
    """Submit approval review"""
    if not prescription_db:
        return jsonify({"msg": "Approval features not available"}), 503
    
    current_user = get_jwt_identity()
    if current_user.get('role') not in ['pharmacist']:
        return jsonify({"msg": "Unauthorized"}), 403
    
    data = request.json
    updated = prescription_db.update_approval(
        approval_id,
        data.get('status', 'approved'),
        current_user['email'],
        data.get('corrected_medicines')
    )
    
    return jsonify(updated) if updated else (jsonify({"msg": "Not found"}), 404)

# Serve Static Files (Images)
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)


# Regional Medicine Alternatives API
@app.route('/api/medicines/<name>/alternatives', methods=['GET'])
@jwt_required()
def get_medicine_alternatives(name):
    """Get regional alternatives for a medicine"""
    try:
        from utils.regional_alternatives import regional_mapper
        user_region = request.args.get('region', 'Karnataka')
        result = regional_mapper.find_alternatives(name, user_region)
        return jsonify(result)
    except Exception as e:
        print(f"Regional alternatives error: {e}", flush=True)
        return jsonify({'error': str(e), 'alternatives': []}), 500




