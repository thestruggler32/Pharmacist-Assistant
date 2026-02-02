"""
Fuzzy Medicine Name Matcher
Uses rapidfuzz to correct OCR errors against a comprehensive Indian medicine database
"""
from rapidfuzz import process, fuzz
import json
import os

class MedicineMatcher:
    def __init__(self):
        self.medicines = self._load_database()
        print(f"Loaded {len(self.medicines)} medicines for fuzzy matching", flush=True)
    
    def _load_database(self):
        """Load Indian medicine brands database"""
        # Priority: Common Indian brands (expandable)
        common_brands = [
            # Pain & Inflammation
            "Zerodol", "Zerodol-SP", "Zerodol-P", "Zerodol-MR",
            "Voldol", "Veldol", "Veldol-Plus",
            "Etosun", "Etosun-MR", "Etoricoxib",
            "Pain-O-Soma", "Paracetamol", "PCM",
            "Volini", "Volini Gel", "Volini Spray",
            "Crocin", "Crocin Advance", "Crocin Pain Relief",
            "Dolo-650", "Dolo", "Dolo-500",
            "Combiflam", "Combiflam Plus",
            "Ibuprofen", "Brufen",
            "Diclofenac", "Aceclofenac",
            "Tramadol", "Ultracet",
            
            # Antibiotics
            "Azithromycin", "Azee", "Azithral",
            "Amoxicillin", "Mox", "Augmentin",
            "Ciprofloxacin", "Cipro", "Ciplox",
            "Cefixime", "Taxim-O",
            
            # Topical
            "Clobetasol", "Clob-MR", "Dermovate",
            "Betamethasone", "Betnovate",
            "Lidocaine", "Lignocaine",
            "Mupirocin", "T-Bact",
            
            # Antivirals
            "Valacyclovir", "Valcivir",
            "Acyclovir", "Zovirax",
            
            # Antifungals
            "Fluconazole", "Forcan",
            "Itraconazole", "Candistat",
            
            # Gastro
            "Omeprazole", "Omez",
            "Pantoprazole", "Pan", "Pan-40",
            "Ranitidine", "Aciloc",
            
            # Others
            "Montelukast", "Montair",
            "Cetirizine", "Zyrtec",
            "Salbutamol", "Asthalin",
        ]
        
        # Load from JSON file if exists
        db_path = os.path.join(os.path.dirname(__file__), '../database/medicines.json')
        if os.path.exists(db_path):
            try:
                with open(db_path, 'r', encoding='utf-8') as f:
                    db_data = json.load(f)
                    if isinstance(db_data, list):
                        common_brands.extend([m if isinstance(m, str) else m.get('name', '') for m in db_data])
                    elif isinstance(db_data, dict) and 'brands' in db_data:
                        common_brands.extend(db_data['brands'])
            except Exception as e:
                print(f"Warning: Could not load medicines.json: {e}", flush=True)
        
        # Load from SQLite database
        sqlite_path = os.path.join(os.path.dirname(__file__), '../database/pharmacy.db')
        if os.path.exists(sqlite_path):
            try:
                import sqlite3
                conn = sqlite3.connect(sqlite_path)
                cursor = conn.cursor()
                cursor.execute("SELECT generic_name, brand_name FROM medicines")
                for row in cursor.fetchall():
                    common_brands.append(row[0])  # generic_name
                    common_brands.append(row[1])  # brand_name
                conn.close()
                print(f"✓ Loaded medicines from pharmacy.db", flush=True)
            except Exception as e:
                print(f"Warning: Could not load pharmacy.db: {e}", flush=True)
        
        # Remove duplicates and empty strings
        return list(set(filter(None, common_brands)))
    
    def fuzzy_correct(self, medicine_name, threshold=80):
        """
        Find best match for medicine name using token_set_ratio with correction feedback
        
        Args:
            medicine_name: OCR-extracted medicine name
            threshold: Minimum similarity score (0-100)
        
        Returns:
            tuple: (corrected_name, confidence_score)
        """
        if not medicine_name or len(medicine_name) < 3:
            return medicine_name, 0.0
        
        # STEP 1: Check correction feedback first
        try:
            from utils.correction_feedback import correction_feedback
            hint = correction_feedback.get_correction_hint(medicine_name)
            if hint:
                print(f"   📝 Feedback correction: '{medicine_name}' → '{hint}'", flush=True)
                return hint, 0.98  # High confidence from human feedback
        except Exception as e:
            pass  # Silently continue if feedback unavailable
        
        # STEP 2: Use token_set_ratio for better partial matching
        # This handles cases like "Zerodol SP" vs "Zerodol-SP"
        result = process.extractOne(
            medicine_name,
            self.medicines,
            scorer=fuzz.token_set_ratio
        )
        
        if result and result[1] >= threshold:
            match_name, score, _ = result
            return match_name, score / 100.0  # Normalize to 0-1
        
        # No good match found, return original
        return medicine_name, 0.5
    
    def batch_correct(self, medicine_list, threshold=80):
        """Correct a list of medicine names"""
        results = []
        for med_name in medicine_list:
            corrected, conf = self.fuzzy_correct(med_name, threshold)
            results.append({
                'original': med_name,
                'corrected': corrected,
                'confidence': conf,
                'matched': conf >= (threshold / 100.0)
            })
        return results
