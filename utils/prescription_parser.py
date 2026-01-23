"""
Enhanced Prescription Parser for Messy Handwritten Prescriptions
"""

import re


class PrescriptionParser:
    def __init__(self, lenient_mode=False):
        """
        Initialize parser
        
        Args:
            lenient_mode: If True, use very loose rules for messy handwriting
        """
        self.lenient_mode = lenient_mode
        
        # Header keywords to filter out
        self.header_keywords = [
            'name', 'age', 'date', 'address', 'signature', 'rx', 'dr.', 'doctor',
            'clinic', 'hospital', 'phone', 'email', 'patient', 'prescription',
            'hosp', 'consultant', 'ms', 'md', 'mbbs', 'doh'
        ]
        
        # Medicine indicators (expanded for handwriting)
        self.medicine_indicators = [
            # Dosage units
            'mg', 'ml', 'g', 'mcg', 'iu', 'tab', 'tablet', 'capsule', 'cap',
            'syrup', 'suspension', 'injection', 'inj', 'vial', 'vials',
            # Frequency
            'bid', 'tid', 'qid', 'qd', 'od', 'bd', 'tds', 'hs', 'prn', 'stat', 'sos',
            # Dosage patterns
            '1-0-1', '0-1-0', '1-1-1', '0-0-1', '1-0-0', '0-1-1',
            # Routes
            'iv', 'im', 'sc', 'po', 'pr', 'sl',
            # Additional
            'dose', 'day', 'daily', 'week', 'month'
        ]
        
        # Strength pattern - more flexible for handwriting
        # Matches: 50mg, 50 mg, 300mg, 2vials, etc.
        self.strength_pattern = re.compile(
            r'\b(\d+\.?\d*)\s*(mg|ml|g|mcg|iu|vial|vials|tab|tabs|cap|caps)\b',
            re.IGNORECASE
        )
        
        # Dosage patterns - expanded
        self.dosage_pattern = re.compile(
            r'\b(\d+-\d+-\d+|bid|tid|qid|qd|od|bd|tds|hs|prn|stat|sos|'
            r'\d+\s*vial[s]?/day|\d+\s*tab[s]?/day|daily|od|bd)\b',
            re.IGNORECASE
        )
        
        # Confidence threshold
        self.confidence_threshold = 0.3 if lenient_mode else 0.5
    
    def is_header_line(self, text):
        """Check if line is a header/metadata line"""
        text_lower = text.lower().strip()
        
        # Empty or very short lines
        if len(text_lower) < 2:
            return True
        
        # Check for header keywords
        for keyword in self.header_keywords:
            if keyword in text_lower:
                return True
        
        # Lines with only dates or numbers (but not medicine numbers)
        if re.match(r'^[\d\s/\-:]+$', text_lower):
            return True
        
        return False
    
    def is_medicine_line(self, text):
        """
        Check if line contains medicine information
        
        In lenient mode, we're VERY permissive:
        - Any line with a number + unit (50mg, 2vials)
        - Any line with medical abbreviations (Inj, IV, OD)
        - Any line with dosage frequency (BID, TID, daily)
        """
        text_lower = text.lower()
        
        # Check for medicine indicators
        for indicator in self.medicine_indicators:
            if indicator in text_lower:
                return True
        
        # In lenient mode, check for number + unit pattern anywhere
        if self.lenient_mode:
            # Match patterns like "50mg", "2 vials", "300 mg"
            if re.search(r'\d+\.?\d*\s*(mg|ml|g|mcg|iu|vial|tab|cap)', text_lower):
                return True
            
            # Match medical abbreviations
            if re.search(r'\b(inj|tab|cap|syp|susp|iv|im|sc|po)\b', text_lower):
                return True
        
        return False
    
    def extract_medicine_info(self, text, confidence):
        """Extract medicine name, strength, and dosage from text"""
        try:
            # Extract all strengths (there might be multiple)
            strength_matches = list(self.strength_pattern.finditer(text))
            strength = ' '.join([m.group(0) for m in strength_matches]) if strength_matches else ""
            
            # Extract dosage
            dosage_match = self.dosage_pattern.search(text)
            dosage = dosage_match.group(0) if dosage_match else ""
            
            # Extract medicine name
            medicine_name = text
            
            # Try to extract name before first strength indicator
            if strength_matches:
                medicine_name = text[:strength_matches[0].start()].strip()
            elif dosage_match:
                medicine_name = text[:dosage_match.start()].strip()
            
            # Clean medicine name
            medicine_name = re.sub(r'\s+', ' ', medicine_name).strip()
            
            # Remove common prefixes
            medicine_name = re.sub(r'^(inj|tab|cap|syp|susp)\s+', '', medicine_name, flags=re.IGNORECASE)
            
            # If medicine name is empty or too short, use original text
            if len(medicine_name) < 2:
                medicine_name = text.strip()
            
            # Determine risk level based on confidence
            # In lenient mode, lower thresholds
            if self.lenient_mode:
                if confidence > 0.7:
                    risk_level = "green"
                elif confidence >= 0.4:
                    risk_level = "yellow"
                else:
                    risk_level = "red"
            else:
                if confidence > 0.8:
                    risk_level = "green"
                elif confidence >= 0.5:
                    risk_level = "yellow"
                else:
                    risk_level = "red"
            
            return {
                "medicine_name": medicine_name,
                "strength": strength,
                "dosage": dosage,
                "confidence": confidence,
                "risk_level": risk_level,
                "original_text": text
            }
        
        except Exception as e:
            print(f"Error extracting medicine info: {e}")
            return None
    
    def parse(self, ocr_results):
        """
        Parse OCR results and extract medicine information
        
        Args:
            ocr_results: List of dicts with 'text' and 'confidence' keys
            
        Returns:
            List of medicine dicts
        """
        try:
            if not ocr_results:
                return []
            
            medicines = []
            
            for item in ocr_results:
                try:
                    text = item.get("text", "").strip()
                    confidence = item.get("confidence", 0.0)
                    
                    # Skip empty text
                    if not text:
                        continue
                    
                    # Skip very low confidence in strict mode
                    if not self.lenient_mode and confidence < self.confidence_threshold:
                        continue
                    
                    # Skip header lines
                    if self.is_header_line(text):
                        continue
                    
                    # Process medicine lines
                    if self.is_medicine_line(text):
                        medicine_info = self.extract_medicine_info(text, confidence)
                        if medicine_info:
                            medicines.append(medicine_info)
                            print(f"✓ Detected medicine: {medicine_info['medicine_name']}")
                
                except (KeyError, TypeError, AttributeError) as e:
                    print(f"Error processing item: {e}")
                    continue
            
            print(f"\nTotal medicines detected: {len(medicines)}")
            return medicines
        
        except Exception as e:
            print(f"Error in parse: {e}")
            return []


if __name__ == "__main__":
    # Test the parser
    print("=" * 70)
    print("PRESCRIPTION PARSER TEST")
    print("=" * 70)
    
    # Test with sample OCR data (simulating handwritten prescription)
    sample_ocr = [
        {"text": "Manipal Hospital", "confidence": 0.95},
        {"text": "Dr. Shalina Ray", "confidence": 0.90},
        {"text": "Inj LIPOSOMAL AMPHOTERICIN", "confidence": 0.75},
        {"text": "50mg IV x 2vials [6 VIALS/day]", "confidence": 0.65},
        {"text": "dose 300mg OD", "confidence": 0.70},
        {"text": "Inj AMPHOTERICIN CONVENTIONAL", "confidence": 0.72},
        {"text": "50mg x 8 vials", "confidence": 0.68},
        {"text": "[1 VIAL/day]", "confidence": 0.60},
    ]
    
    print("\n[1/2] Standard Mode:")
    parser_std = PrescriptionParser(lenient_mode=False)
    medicines_std = parser_std.parse(sample_ocr)
    print(f"Detected: {len(medicines_std)} medicines")
    
    print("\n[2/2] Lenient Mode (for handwriting):")
    parser_lenient = PrescriptionParser(lenient_mode=True)
    medicines_lenient = parser_lenient.parse(sample_ocr)
    print(f"Detected: {len(medicines_lenient)} medicines")
    
    for i, med in enumerate(medicines_lenient, 1):
        print(f"\n  Medicine {i}:")
        print(f"    Name: {med['medicine_name']}")
        print(f"    Strength: {med['strength']}")
        print(f"    Dosage: {med['dosage']}")
        print(f"    Confidence: {med['confidence']:.2f}")
        print(f"    Risk: {med['risk_level']}")
    
    print("\n" + "=" * 70)
