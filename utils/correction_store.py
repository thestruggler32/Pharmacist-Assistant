import json
import os
from datetime import datetime


class CorrectionStore:
    def __init__(self, filepath="data/corrections.json"):
        self.filepath = filepath
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create corrections file if it doesn't exist"""
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            if not os.path.exists(self.filepath):
                with open(self.filepath, 'w') as f:
                    json.dump([], f)
        except Exception:
            pass
    
    def save_correction(self, correction_data):
        """
        Save a correction entry to the JSON file.
        
        Expected correction_data structure:
        {
            "original_ocr_text": str,
            "corrected_fields": {
                "medicine_name": str,
                "strength": str,
                "dosage": str
            },
            "original_confidence": float,
            "pharmacist_id": str,
            "timestamp": str (ISO format),
            "image_reference": str
        }
        
        Returns: True if successful, False otherwise
        """
        try:
            # Add timestamp if not provided
            if "timestamp" not in correction_data:
                correction_data["timestamp"] = datetime.now().isoformat()
            
            # Load existing corrections
            corrections = self.load_all_corrections()
            
            # Append new correction
            corrections.append(correction_data)
            
            # Write back to file
            with open(self.filepath, 'w') as f:
                json.dump(corrections, f, indent=2)
            
            return True
        
        except Exception:
            return False
    
    def load_all_corrections(self):
        """
        Load all corrections from the JSON file.
        
        Returns: List of correction entries, or empty list if error
        """
        try:
            if not os.path.exists(self.filepath):
                self._ensure_file_exists()
                return []
            
            with open(self.filepath, 'r') as f:
                corrections = json.load(f)
            
            return corrections if isinstance(corrections, list) else []
        
        except Exception:
            return []
