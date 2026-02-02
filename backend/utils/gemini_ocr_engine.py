"""
Gemini 2.5 Pro OCR Engine via Google AI
Latest model with superior vision and reasoning capabilities
"""
import os
import json
import cv2
import time
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

class GeminiOCREngine:
    """
    Gemini 2.5 Pro for Indian prescription OCR
    Latest model with enhanced vision and 15 RPM rate limit
    """
    def __init__(self):
        # Try new API key first, fallback to old key
        self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_AI_STUDIO_KEY")
        
        if not self.api_key:
            print("⚠️ No Google API key found, Gemini engine disabled", flush=True)
            self.model = None
        else:
            try:
                genai.configure(api_key=self.api_key)
                # Use gemini-2.5-pro - latest model with superior vision capabilities
                # Rate limit: 15 RPM with new key
                self.model = genai.GenerativeModel('gemini-2.5-pro')
                print(f"✓ Gemini 2.5 Pro initialized (using {'GOOGLE_API_KEY' if os.getenv('GOOGLE_API_KEY') else 'GOOGLE_AI_STUDIO_KEY'})", flush=True)
            except Exception as e:
                print(f"⚠️ Gemini initialization error: {e}", flush=True)
                self.model = None

    def extract_medicines(self, image_path):
        """
        Main extraction pipeline: Preprocess -> Gemini Vision -> Fuzzy refinement
        """
        try:
            print(f"\n{'='*60}", flush=True)
            print(f"GEMINI OCR PIPELINE: Processing {os.path.basename(image_path)}", flush=True)
            print(f"{'='*60}", flush=True)
            
            # STEP 1: Preprocessing
            print("[1/3] Preprocessing image...", flush=True)
            from utils.image_preprocessor import ImagePreprocessor
            preprocessor = ImagePreprocessor(handwriting_mode=True)
            processed_img, quality_report = preprocessor.preprocess(image_path)
            
            processed_path = image_path.replace('.', '_preprocessed.')
            if not processed_path.endswith(('.jpg', '.jpeg', '.png')):
                processed_path = image_path.rsplit('.', 1)[0] + '_preprocessed.jpg'
            preprocessor.save_preprocessed_image(processed_img, processed_path)
            print(f"   Quality: {quality_report.get('quality_score', 'unknown')}", flush=True)
            
            # STEP 2: Gemini Vision OCR
            print("[2/3] Gemini 2.5 Pro extraction...", flush=True)
            candidates = self._gemini_ocr_json(processed_path)
            
            print(f"   Extracted {len(candidates)} medicine candidates", flush=True)
            
            # STEP 3: Fuzzy Database Refinement
            print("[3/3] Fuzzy database refinement...", flush=True)
            results = self._fuzzy_refine(candidates)
            
            if results:
                avg_conf = sum(r.get('confidence', 0) for r in results) / len(results)
                print(f"\n✓ Pipeline complete: {len(results)} medicines, {avg_conf*100:.1f}% avg confidence", flush=True)
            else:
                print(f"\n⚠️ No medicines extracted", flush=True)
            
            print(f"{'='*60}\n", flush=True)
            return results
            
        except Exception as e:
            print(f"❌ Pipeline Error: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return []

    def _gemini_ocr_json(self, image_path):
        """Gemini 2.5 Pro: Image -> JSON with Indian Pharmacist expertise"""
        
        if not self.model:
            return []
        
        GEMINI_PROMPT = """Role: Expert Pharmacist specializing in Indian handwritten prescriptions (English, Hindi, Kannada).
Task: Extract medications AND supplies into JSON from multilingual prescriptions.

LANGUAGE SUPPORT:
1. HINDI (हिंदी): Recognize Devanagari script for medicine names and dosages
   - Common terms: "गोली" (tablet), "दिन" (day), "सुबह-शाम" (morning-evening)
   - Transliterate Hindi names to English (e.g., "पैन-डी" → "Pan-D")

2. KANNADA (ಕನ್ನಡ): Recognize Kannada script
   - Common terms: "ಮಾತ್ರೆ" (tablet), "ದಿನ" (day), "ಬೆಳಿಗ್ಗೆ-ಸಂಜೆ" (morning-evening)
   - Transliterate to English

3. ENGLISH: Standard prescription notation

STRICT RULES:
1. VISUAL SEARCH: Scan bottom/right margins for non-pill items like "Crepe Bandage", "Syringe", "Injection"
2. DOSAGE DECODING:
   - "1-0-1" or "१-०-१" = Twice Daily
   - "1-1-1" or "१-१-१" = Thrice Daily
   - "1-0-0" = Once Daily
   - Look for faint dashes between numbers
3. SPELLING FIXES:
   - "Pan-D" (Not Pain-D)
   - "Zerodol-SP" (Not Zerodol-Sp)
   - "Crepe Bandage" (Fix "Crepe Bandau")
4. TRANSLITERATION: Always provide English transliteration for final output

JSON Format:
{
  "medicines": [
    {
      "name": "Exact name in English (e.g., Pan-D, Zerodol-SP, Crepe Bandage)",
      "strength": "40mg if visible, or empty string",
      "dosage": "Decoded (e.g., Twice Daily from 1-0-1)",
      "duration": "10 days (from x10 or x 10)",
      "confidence": 0.95,
      "raw_text": "Original text in any script",
      "detected_language": "english|hindi|kannada"
    }
  ]
}

Return ONLY valid JSON. No markdown. Extract EVERYTHING including bandages."""
        
        try:
            # Upload image to Gemini
            print(f"   Uploading image to Gemini...", flush=True)
            uploaded_file = genai.upload_file(image_path)
            print(f"   File uploaded: {uploaded_file.name}", flush=True)
            
            # Generate response with low temperature for accuracy
            response = self.model.generate_content(
                [uploaded_file, GEMINI_PROMPT],
                generation_config=genai.GenerationConfig(
                    temperature=0.1  # Low temp for accuracy
                )
            )
            
            # RATE LIMIT HANDLING: 15 RPM = 4 seconds between requests
            print(f"   ⏱ Waiting 5s to respect 15 RPM rate limit...", flush=True)
            time.sleep(5)
            
            content = response.text
            print(f"   Gemini raw output: {content[:300]}...", flush=True)
            
            # Clean markdown if present
            content = content.replace("```json", "").replace("```", "").strip()
            
            # Parse JSON
            data = json.loads(content)
            
            medicines = data.get('medicines', [])
            if isinstance(data, list):
                medicines = data
            
            if not medicines:
                print("   ⚠️ No medicines found in Gemini response", flush=True)
            
            # Normalize
            results = []
            for item in medicines:
                results.append({
                    'medicine_name': item.get('name', item.get('medicine_name', 'Unknown')),
                    'strength': item.get('strength', ''),
                    'dosage': item.get('dosage', ''),
                    'duration': str(item.get('duration', '')),
                    'confidence': float(item.get('confidence', 0.90)),
                    'original_text': item.get('raw_text', item.get('original_text', '')),
                    'source': 'gemini_2.5_pro'
                })
            
            # Cleanup uploaded file
            try:
                genai.delete_file(uploaded_file.name)
                print(f"   Cleaned up uploaded file", flush=True)
            except Exception as cleanup_error:
                print(f"   Cleanup warning: {cleanup_error}", flush=True)
            
            return results
            
        except json.JSONDecodeError as e:
            print(f"   JSON Parse Error: {e}", flush=True)
            print(f"   Raw content: {content if 'content' in locals() else 'No content'}", flush=True)
            return []
        except Exception as e:
            print(f"   Gemini Error: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return []

    def _fuzzy_refine(self, candidates):
        """Fuzzy refinement against real database with aggressive matching"""
        try:
            from utils.fuzzy_matcher import MedicineMatcher
            matcher = MedicineMatcher()
            
            results = []
            for item in candidates:
                original_name = item['medicine_name']
                
                # AGGRESSIVE fuzzy correction with lower threshold (60 instead of 75)
                corrected_name, match_conf = matcher.fuzzy_correct(original_name, threshold=60)
                
                if match_conf >= 0.70:  # Lower threshold to catch more matches
                    item['medicine_name'] = corrected_name
                    item['fuzzy_corrected'] = True
                    item['original_ocr'] = original_name
                    item['fuzzy_match_score'] = match_conf
                    
                    # Ensemble confidence scoring with HIGHER fuzzy weight
                    gemini_conf = item.get('confidence', 0.9)
                    final_conf = (gemini_conf * 0.5 + match_conf * 0.5)  # 50-50 split
                    item['confidence'] = min(final_conf, 0.98)
                    
                    print(f"   ✓ Fuzzy: '{original_name}' → '{corrected_name}' ({match_conf*100:.0f}%)", flush=True)
                else:
                    item['fuzzy_corrected'] = False
                    # Still try partial match logging
                    print(f"   ⚠ Kept original: '{original_name}' (best match: {corrected_name} at {match_conf*100:.0f}%)", flush=True)
                
                results.append(item)
            
            return results
            
        except Exception as e:
            print(f"   Fuzzy refinement error: {e}, returning raw", flush=True)
            return candidates
