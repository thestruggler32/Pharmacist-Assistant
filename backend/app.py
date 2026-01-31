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
    'patient@test.com': {'password': 'password', 'role': 'patient', 'name': 'John Doe'},
    'doctor@test.com': {'password': 'password', 'role': 'doctor', 'name': 'Dr. Smith', 'reg_no': '12345'},
    'pharmacist@test.com': {'password': 'password', 'role': 'pharmacist', 'name': 'Pharma Joe', 'license': '20B/TEST', 'license_verified': True}
}

# --- Routes ---

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "Backend is running"})

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
    
    if user_role not in ['pharmacist']:
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
        
        if 'hybrid_ocr' not in globals():
            print("ERROR: hybrid_ocr engine not initialized!")
            return jsonify({"msg": "OCR engine not available. Check backend logs."}), 500
            
        parsed_medicines = hybrid_ocr.extract_medicines(filepath)
        print(f"Parsed {len(parsed_medicines)} medicines")
        
        PRESCRIPTIONS[prescription_id] = {
            'id': prescription_id,
            'image_url': f"/static/uploads/{prescription_id}_{filename}", 
            'medicines': parsed_medicines,
            'status': 'pending',
            'uploaded_by': current_user_email,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(PRESCRIPTIONS[prescription_id])

    except Exception as e:
        print(f"OCR Failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"msg": f"Processing failed: {str(e)}"}), 500

@app.route('/api/prescriptions/<id>', methods=['GET'])
@jwt_required()
def get_prescription(id):
    p = PRESCRIPTIONS.get(id)
    if not p:
        return jsonify({"msg": "Not found"}), 404
    return jsonify(p)

@app.route('/api/translate', methods=['POST'])
def translate_text():
    data = request.json
    text = data.get('text')
    target = data.get('target', 'hi')
    
    try:
        from google.cloud import translate_v2 as translate
        client = translate.Client()
        result = client.translate(text, target_language=target)
        return jsonify({'translatedText': result['translatedText']})
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

# Serve Static Files (Images)
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
