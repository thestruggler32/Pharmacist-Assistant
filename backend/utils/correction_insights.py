from utils.correction_store import CorrectionStore
import re


class CorrectionInsights:
    def __init__(self):
        self.store = CorrectionStore()
    
    def get_common_misspellings(self):
        """
        Extract common misspellings from corrections.
        
        Returns: dict mapping original OCR text to corrected medicine name
        Example: {"paracetmol": "paracetamol", "asprin": "aspirin"}
        """
        try:
            corrections = self.store.load_all_corrections()
            if not corrections:
                return {}
            
            misspellings = {}
            
            for correction in corrections:
                try:
                    original_text = correction.get("original_ocr_text", "").strip().lower()
                    corrected_fields = correction.get("corrected_fields", {})
                    corrected_name = corrected_fields.get("medicine_name", "").strip().lower()
                    
                    # Skip if either is empty
                    if not original_text or not corrected_name:
                        continue
                    
                    # Extract medicine name from original text (before strength/dosage)
                    original_name = self._extract_medicine_name(original_text)
                    
                    # Only record if names differ
                    if original_name and original_name != corrected_name:
                        misspellings[original_name] = corrected_name
                
                except (KeyError, TypeError, AttributeError):
                    continue
            
            return misspellings
        
        except Exception:
            return {}
    
    def get_common_dosage_patterns(self):
        """
        Extract frequently corrected dosage patterns.
        
        Returns: list of corrected dosage patterns
        Example: ["1-0-1", "BID", "TID", "0-1-0"]
        """
        try:
            corrections = self.store.load_all_corrections()
            if not corrections:
                return []
            
            dosage_counts = {}
            
            for correction in corrections:
                try:
                    corrected_fields = correction.get("corrected_fields", {})
                    dosage = corrected_fields.get("dosage", "").strip().upper()
                    
                    # Skip empty dosages
                    if not dosage:
                        continue
                    
                    # Count occurrences
                    dosage_counts[dosage] = dosage_counts.get(dosage, 0) + 1
                
                except (KeyError, TypeError, AttributeError):
                    continue
            
            # Sort by frequency and return patterns
            sorted_dosages = sorted(dosage_counts.items(), key=lambda x: x[1], reverse=True)
            return [dosage for dosage, count in sorted_dosages]
        
        except Exception:
            return []
    
    def _extract_medicine_name(self, text):
        """Extract medicine name from OCR text (before strength/dosage indicators)"""
        try:
            # Remove common strength patterns
            text = re.sub(r'\b\d+\.?\d*\s*(mg|ml|g|mcg|iu)\b', '', text, flags=re.IGNORECASE)
            
            # Remove common dosage patterns
            text = re.sub(r'\b(\d+-\d+-\d+|bid|tid|qd|od|hs|prn|stat|sos)\b', '', text, flags=re.IGNORECASE)
            
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text
        
        except Exception:
            return text
