"""
Database models for prescriptions, annotations, and pharmacist approvals
"""
from datetime import datetime
import json
import os

class PrescriptionDB:
    """Simple file-based database for prescriptions"""
    
    def __init__(self, db_path='backend/database/prescriptions.json'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._load()
    
    def _load(self):
        try:
            with open(self.db_path, 'r') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {
                'prescriptions': {},
                'approvals': {},
                'annotations': {}
            }
            self._save()
    
    def _save(self):
        with open(self.db_path, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def add_prescription(self, prescription_id, prescription_data):
        """Add or update prescription with confidence scoring"""
        self.data['prescriptions'][prescription_id] = {
            **prescription_data,
            'created_at': datetime.now().isoformat(),
            'confidence': self._calculate_confidence(prescription_data.get('medicines', []))
        }
        self._save()
        return self.data['prescriptions'][prescription_id]
    
    def _calculate_confidence(self, medicines):
        """Calculate average confidence from medicine extractions"""
        if not medicines:
            return 0.0
        
        confidences = []
        for med in medicines:
            if isinstance(med, dict) and 'confidence' in med:
                confidences.append(med['confidence'])
        
        return round(sum(confidences) / len(confidences), 2) if confidences else 0.5
    
    def get_prescription(self, prescription_id):
        return self.data['prescriptions'].get(prescription_id)
    
    def get_all_prescriptions(self):
        return self.data['prescriptions']
    
    def needs_approval(self, prescription_id, threshold=0.75):
        """Check if prescription needs pharmacist approval based on confidence"""
        prescription = self.get_prescription(prescription_id)
        if not prescription:
            return False
        return prescription.get('confidence', 0) < threshold
    
    def add_annotation(self, prescription_id, annotation_data):
        """Store bounding box annotations for prescription"""
        if prescription_id not in self.data['annotations']:
            self.data['annotations'][prescription_id] = []
        
        self.data['annotations'][prescription_id].append({
            **annotation_data,
            'created_at': datetime.now().isoformat()
        })
        self._save()
    
    def get_annotations(self, prescription_id):
        return self.data['annotations'].get(prescription_id, [])
    
    def save_prescription(self, prescription_id, prescription_data):
        """Save or update a prescription"""
        self.data['prescriptions'][prescription_id] = {
            **prescription_data,
            'updated_at': datetime.now().isoformat()
        }
        self._save()
        return self.data['prescriptions'][prescription_id]
    
    def update_prescription(self, prescription_id, updates):
        """Update specific fields of a prescription"""
        if prescription_id in self.data['prescriptions']:
            self.data['prescriptions'][prescription_id].update(updates)
            self.data['prescriptions'][prescription_id]['updated_at'] = datetime.now().isoformat()
            self._save()
            return self.data['prescriptions'][prescription_id]
        return None
    
    def create_approval_request(self, prescription_id, pharmacist_id=None):
        """Create approval request for low-confidence prescription"""
        approval_id = f"approval_{prescription_id}_{datetime.now().timestamp()}"
        self.data['approvals'][approval_id] = {
            'id': approval_id,
            'prescription_id': prescription_id,
            'status': 'pending',
            'assigned_to': pharmacist_id,
            'created_at': datetime.now().isoformat(),
            'reviewed_at': None,
            'reviewed_by': None
        }
        self._save()
        return self.data['approvals'][approval_id]
    
    def get_pending_approvals(self, pharmacist_id=None):
        """Get all pending approval requests"""
        approvals = []
        for approval in self.data['approvals'].values():
            if approval['status'] == 'pending':
                if pharmacist_id is None or approval.get('assigned_to') == pharmacist_id:
                    approvals.append(approval)
        return approvals
    
    def update_approval(self, approval_id, status, reviewer_id, corrected_medicines=None):
        """Update approval status and optionally store corrections"""
        if approval_id in self.data['approvals']:
            self.data['approvals'][approval_id].update({
                'status': status,
                'reviewed_at': datetime.now().isoformat(),
                'reviewed_by': reviewer_id,
                'corrected_medicines': corrected_medicines
            })
            
            # Update prescription with corrected data if provided
            if corrected_medicines and status == 'approved':
                prescription_id = self.data['approvals'][approval_id]['prescription_id']
                if prescription_id in self.data['prescriptions']:
                    self.data['prescriptions'][prescription_id]['medicines'] = corrected_medicines
                    self.data['prescriptions'][prescription_id]['confidence'] = 1.0  # Manually verified
            
            self._save()
            return self.data['approvals'][approval_id]
        return None

# Global instance
prescription_db = PrescriptionDB()
