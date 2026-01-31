from utils.correction_store import CorrectionStore
from utils.medicine_matcher import MedicineMatcher
from difflib import SequenceMatcher
import re


class CorrectionLearner:
    """Enhanced correction-based learning with medicine database matching"""
    
    def __init__(self):
        self.store = CorrectionStore()
        self.matcher = MedicineMatcher()
        self.misspelling_map = {}
        self.dosage_patterns = []
        self._load_corrections()
    
    def _load_corrections(self):
        """Load historical corrections and build mappings"""
        try:
            corrections = self.store.load_all_corrections()
            
            for correction in corrections:
                try:
                    original = correction.get('original_ocr_text', '').strip().lower()
                    corrected_fields = correction.get('corrected_fields', {})
                    corrected_name = corrected_fields.get('medicine_name', '').strip().lower()
                    
                    if original and corrected_name:
                        original_clean = self._extract_medicine_name(original)
                        if original_clean != corrected_name:
                            self.misspelling_map[original_clean] = corrected_name
                    
                    dosage = corrected_fields.get('dosage', '').strip().upper()
                    if dosage and dosage not in self.dosage_patterns:
                        self.dosage_patterns.append(dosage)
                
                except (KeyError, TypeError, AttributeError):
                    continue
        
        except Exception:
            pass
    
    def _extract_medicine_name(self, text):
        """Extract medicine name from OCR text"""
        try:
            text = re.sub(r'\b\d+\.?\d*\s*(mg|ml|g|mcg|iu)\b', '', text, flags=re.IGNORECASE)
            text = re.sub(r'\b(\d+-\d+-\d+|bid|tid|qd|od|hs|prn|stat|sos)\b', '', text, flags=re.IGNORECASE)
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        except Exception:
            return text
    
    def suggest_correction(self, ocr_text, region='All', threshold=0.7):
        """
        Suggest correction using medicine database and fuzzy matching.
        
        Args:
            ocr_text: OCR extracted text
            region: Region to search in ('All', 'Karnataka', 'Mysore', 'National')
            threshold: Minimum confidence threshold (0-1)
        
        Returns: List of suggestions with confidence scores
        """
        try:
            ocr_clean = self._extract_medicine_name(ocr_text.lower())
            
            # First check historical corrections
            if ocr_clean in self.misspelling_map:
                return [{
                    'text': self.misspelling_map[ocr_clean],
                    'confidence': 1.0,
                    'source': 'historical'
                }]
            
            # Use medicine matcher for database lookup
            matches = self.matcher.find_matches(ocr_clean, region=region, top_n=3, threshold=int(threshold * 100))
            
            suggestions = []
            for match in matches:
                suggestions.append({
                    'text': match['name'],
                    'brand': match['brand'],
                    'strength': match['strength'],
                    'confidence': match['score'] / 100.0,
                    'source': 'database'
                })
            
            return suggestions
        
        except Exception as e:
            print(f"Error in suggest_correction: {e}")
            return []
    
    def get_common_dosage_patterns(self):
        """Return list of common dosage patterns from corrections"""
        return self.dosage_patterns.copy()
    
    def add_correction(self, original_text, corrected_fields, pharmacist_id, prescription_id):
        """Store a new correction and update mappings"""
        try:
            correction_data = {
                'original_ocr_text': original_text,
                'corrected_fields': corrected_fields,
                'original_confidence': 0.0,
                'pharmacist_id': pharmacist_id,
                'image_reference': prescription_id
            }
            
            success = self.store.save_correction(correction_data)
            
            if success:
                # Update internal mappings
                original_clean = self._extract_medicine_name(original_text.lower())
                corrected_name = corrected_fields.get('medicine_name', '').strip().lower()
                
                if original_clean and corrected_name and original_clean != corrected_name:
                    self.misspelling_map[original_clean] = corrected_name
                
                dosage = corrected_fields.get('dosage', '').strip().upper()
                if dosage and dosage not in self.dosage_patterns:
                    self.dosage_patterns.append(dosage)
            
            return success
        
        except Exception:
            return False
