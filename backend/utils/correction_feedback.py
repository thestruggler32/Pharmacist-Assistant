"""
Correction Feedback System
Stores pharmacist corrections to improve future OCR accuracy
"""
import sqlite3
import os
from datetime import datetime

class CorrectionFeedback:
    """Track and learn from pharmacist corrections"""
    
    def __init__(self, db_path='backend/database/pharmacy.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_corrections_table()
    
    def _init_corrections_table(self):
        """Ensure corrections table exists"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS corrections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prescription_id TEXT NOT NULL,
                    original_text TEXT NOT NULL,
                    corrected_text TEXT NOT NULL,
                    pharmacist_id TEXT,
                    correction_type TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Index for faster lookups
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_original_text 
                ON corrections(original_text)
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠ Corrections table init error: {e}", flush=True)
    
    def add_correction(self, prescription_id, original_text, corrected_text, 
                      pharmacist_id=None, correction_type='medicine_name'):
        """Store a correction for future reference"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO corrections 
                (prescription_id, original_text, corrected_text, pharmacist_id, correction_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (prescription_id, original_text, corrected_text, pharmacist_id, correction_type))
            conn.commit()
            conn.close()
            print(f"✓ Correction saved: '{original_text}' → '{corrected_text}'", flush=True)
        except Exception as e:
            print(f"⚠ Failed to save correction: {e}", flush=True)
    
    def get_correction_hint(self, ocr_text):
        """Check if we've seen this OCR error before"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT corrected_text, COUNT(*) as frequency
                FROM corrections
                WHERE original_text = ?
                GROUP BY corrected_text
                ORDER BY frequency DESC
                LIMIT 1
            ''', (ocr_text,))
            result = cursor.fetchone()
            conn.close()
            
            if result and result[1] >= 2:  # At least 2 pharmacists agreed
                return result[0]
            return None
        except Exception as e:
            print(f"⚠ Correction lookup error: {e}", flush=True)
            return None
    
    def batch_add_corrections(self, prescription_id, original_medicines, corrected_medicines, pharmacist_id=None):
        """Add corrections from full approval workflow"""
        for orig, corrected in zip(original_medicines, corrected_medicines):
            orig_name = orig.get('medicine_name', orig.get('name', ''))
            corrected_name = corrected.get('medicine_name', corrected.get('name', ''))
            
            if orig_name != corrected_name:
                self.add_correction(
                    prescription_id,
                    orig_name,
                    corrected_name,
                    pharmacist_id,
                    'medicine_name'
                )
    
    def get_common_mistakes(self, limit=20):
        """Get most frequently corrected OCR mistakes"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT original_text, corrected_text, COUNT(*) as frequency
                FROM corrections
                WHERE correction_type = 'medicine_name'
                GROUP BY original_text, corrected_text
                ORDER BY frequency DESC
                LIMIT ?
            ''', (limit,))
            results = cursor.fetchall()
            conn.close()
            return [{'original': r[0], 'corrected': r[1], 'frequency': r[2]} for r in results]
        except Exception as e:
            print(f"⚠ Common mistakes query error: {e}", flush=True)
            return []

# Global instance
correction_feedback = CorrectionFeedback()
