import os
import json
import base64
import time
import requests
from dotenv import load_dotenv
from mistralai import Mistral
from mistralai.models.sdkerror import SDKError

load_dotenv()

def retry_api(max_retries=5, delay=5):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for i in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (SDKError, Exception) as e:
                    error_str = str(e).lower()
                    if "rate" in error_str or "limit" in error_str or "429" in error_str:
                        wait = delay * (2 ** i)
                        print(f"⚠ API Rate limited (Attempt {i+1}/{max_retries}). Retrying in {wait}s...", flush=True)
                        time.sleep(wait)
                    else:
                        raise e
            return func(*args, **kwargs)
        return wrapper
    return decorator

class OCREngine:
    def __init__(self, lang='en'):
        pass # Legacy stub
    def extract_text(self, image_path):
        return []

class MistralOnlyEngine:
    """
    OCR Pipeline 2.0: Indian Prescription Specialist
    1. Image Preprocessing (Bilateral Filter + CLAHE)
    2. Pixtral OCR with Indian Medicine Context
    3. Mistral LLM Structured Parsing (Shorthand aware)
    4. Fuzzy Database Matching for Error Correction
    """
    def __init__(self):
        self.mistral_key = os.getenv("MISTRAL_API_KEY")
        
        if self.mistral_key:
            self.mistral_client = Mistral(api_key=self.mistral_key)
            print("✓ Mistral API initialized", flush=True)
        else:
            print("ERROR: MISTRAL_API_KEY not found in environment", flush=True)
            raise ValueError("MISTRAL_API_KEY required")
        
        # Vision prompt for Indian prescriptions
        self.VISION_PROMPT = """You are transcribing an Indian medical prescription with handwritten text.

COMMON INDIAN PRESCRIPTION ABBREVIATIONS:
- Tab = Tablet
- Inj = Injection  
- Syr = Syrup
- Cap = Capsule
- x = multiply/times (e.g., "x 10" = for 10 days, "x1" = 1 tablet)
- BD / BID = Twice daily (bis in die)
- OD = Once daily
- TDS = Three times daily
- QID = Four times daily
- SOS = If needed (as needed)
- 1-0-1 = Morning-None-Night dosing pattern

COMMON INDIAN MEDICINE BRANDS (recognize these):
Zerodol, Zerodol-SP, Zerodol-P, Veldol, Voldol, Etosun, Etosun-MR, Pain-O-Soma, Pain-O, Volini, Crocin, Dolo-650, Combiflam, Paracetamol, PCM, Clobetasol, Clob-MR, Lidocaine, Lignocaine, Aceclofenac, Diclofenac, Etoricoxib

INSTRUCTIONS:
1. Transcribe ALL handwritten medicine lines exactly as written
2. Include medicine names, numbers, dosages, and symbols (x, BD, OD, etc.)
3. Preserve brand names like "Zerodol-SP" exactly
4. Include dosing patterns like "1-0-1" or "x 10" or "BD"
5. Ignore doctor signatures, patient names, dates, and hospital headers
6. Each medicine should be on a separate line

OUTPUT FORMAT:
Raw transcribed text only, one medicine per line.
Example output:
Tab Zerodol-SP x 10
Tab Veldol x 10 BD
Tab Pain-O 1-0-1 x 10"""

    def extract_medicines(self, image_path):
        """
        Execute enhanced pipeline: Preprocess → Vision → Parse → Fuzzy Match
        """
        try:
            print(f"\n{'='*60}", flush=True)
            print(f"OCR PIPELINE 2.0: Processing {os.path.basename(image_path)}", flush=True)
            print(f"{'='*60}", flush=True)
            
            # STEP 1: Enhanced Image Preprocessing
            print("[1/4] Preprocessing image for handwriting...", flush=True)
            processed_path = self._preprocess_image(image_path)
            
            # STEP 2: Single-Shot Pixtral OCR -> JSON
            print("[2/4] Pixtral single-shot extraction...", flush=True)
            candidates = self._mistral_ocr_json(processed_path)
            print(f"   Extracted {len(candidates)} medicine candidates", flush=True)
            
            # STEP 3: Fuzzy Database Matching
            print("[3/4] Fuzzy database correction...", flush=True)
            results = self._apply_fuzzy_matching(candidates)
            
            # Calculate overall confidence
            if results:
                avg_conf = sum(r.get('confidence', 0) for r in results) / len(results)
                print(f"\n✓ Pipeline complete: {len(results)} medicines, {avg_conf*100:.1f}% avg confidence", flush=True)
            else:
                print(f"\n⚠ No medicines extracted", flush=True)
            
            print(f"{'='*60}\n", flush=True)
            return results
            
        except Exception as e:
            print(f"❌ Pipeline Error: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return []

    def _preprocess_image(self, image_path):
        """Enhanced preprocessing with bilateral filtering for handwriting"""
        try:
            from utils.image_preprocessor import ImagePreprocessor
            preprocessor = ImagePreprocessor(handwriting_mode=True)
            processed_img, quality_report = preprocessor.preprocess(image_path)
            
            # Save preprocessed version
            output_path = image_path.replace('.', '_preprocessed.')
            if not output_path.endswith(('.jpg', '.jpeg', '.png')):
                output_path = image_path.rsplit('.', 1)[0] + '_preprocessed.jpg'
            
            preprocessor.save_preprocessed_image(processed_img, output_path)
            print(f"   Quality: {quality_report.get('quality_score', 'unknown')}", flush=True)
            
            return output_path
        except Exception as e:
            print(f"   Preprocessing error: {e}, using original image", flush=True)
            return image_path

    @retry_api(max_retries=5, delay=5)
    def _mistral_ocr_json(self, image_path):
        """Single-shot Pixtral VLM: Image -> Structured JSON"""
        
        JSON_PROMPT = """You are an Indian Pharmacist AI. Analyze this handwritten prescription image and output structured JSON.

INSTRUCTIONS:
1. Identify all medicines, dosages, and durations.
2. Decode abbreviations: 
   - "Tab" -> "Tablet"
   - "BD"/"BID" -> "Twice daily"
   - "OD" -> "Once daily"
   - "TDS" -> "Three times daily"
   - "x 10" -> "for 10 days"
   - "1-0-1" -> "Morning-Afternoon-Night"
3. Preserve brand names EXACTLY (e.g., Zerodol-SP, Veldol).

OUTPUT JSON FORMAT:
{
  "medicines": [
    {
      "medicine_name": "Exact Brand Name",
      "strength": "500mg (if visible)",
      "dosage": "Twice daily (decoded)",
      "duration": "10 days (decoded)",
      "confidence": 0.95,
      "original_text": "Tab Zerodol-SP x 10"
    }
  ]
}

Return ONLY valid JSON. No markdown.
"""
        try:
            # Resize image for API to avoid rate limits (huge token count)
            import cv2
            import numpy as np
            
            img = cv2.imread(image_path)
            if img is not None:
                # Max dimension 1024px
                max_dim = 1024
                h, w = img.shape[:2]
                if max(h, w) > max_dim:
                    scale = max_dim / max(h, w)
                    new_w, new_h = int(w * scale), int(h * scale)
                    img = cv2.resize(img, (new_w, new_h))
                    print(f"   Resized for API: {w}x{h} -> {new_w}x{new_h}", flush=True)
                
                # Compress to JPEG
                _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 85])
                image_data = base64.b64encode(buffer).decode('utf-8')
            else:
                # Fallback to direct read if cv2 fails
                with open(image_path, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
            
            chat_response = self.mistral_client.chat.complete(
                model="pixtral-12b-2409",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": JSON_PROMPT},
                            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_data}"}
                        ]
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            content = chat_response.choices[0].message.content
            print(f"   Raw VLM output: {content[:100]}...", flush=True)
            
            content = content.replace("```json", "").replace("```", "").strip()
            data = json.loads(content)
            
            medicines = data.get('medicines', [])
            if isinstance(data, list): medicines = data
            
            # Normalize
            results = []
            for item in medicines:
                results.append({
                    'medicine_name': item.get('medicine_name', 'Unknown'),
                    'strength': item.get('strength', ''),
                    'dosage': item.get('dosage', ''),
                    'duration': str(item.get('duration', '')),
                    'confidence': float(item.get('confidence', 0.8)),
                    'original_text': item.get('original_text', ''),
                    'source': 'pixtral_vlm'
                })
            return results

        except Exception as e:
            print(f"   VLM Error: {e}", flush=True)
            return []

    def _apply_fuzzy_matching(self, candidates):
        """Apply fuzzy database matching to correct OCR errors"""
        try:
            from utils.fuzzy_matcher import MedicineMatcher
            matcher = MedicineMatcher()
            
            results = []
            for item in candidates:
                original_name = item['medicine_name']
                
                # Apply fuzzy correction
                corrected_name, match_conf = matcher.fuzzy_correct(original_name, threshold=75)
                
                # Ensemble confidence scoring
                pixtral_conf = 0.30  # Vision weight
                mistral_conf = 0.40  # Parsing weight  
                fuzzy_conf = 0.30    # Database match weight
                
                original_confidence = item.get('confidence', 0.8)
                
                # If strong fuzzy match, boost confidence
                if match_conf >= 0.85:
                    item['medicine_name'] = corrected_name
                    item['fuzzy_corrected'] = True
                    item['original_ocr'] = original_name
                    
                    # Ensemble confidence calculation
                    item['confidence'] = min(
                        (pixtral_conf * 0.9 + 
                         mistral_conf * original_confidence + 
                         fuzzy_conf * match_conf),
                        0.98  # Cap at 98%
                    )
                    item['fuzzy_match_score'] = match_conf
                    print(f"   ✓ Corrected: '{original_name}' → '{corrected_name}' ({match_conf*100:.0f}% match)", flush=True)
                else:
                    # Keep original but flag low confidence
                    item['fuzzy_corrected'] = False
                    if match_conf < 0.5:
                        # Very low match, reduce confidence
                        item['confidence'] = min(original_confidence, 0.7)
                        print(f"   ⚠ Low match: '{original_name}' (kept original, conf: {item['confidence']*100:.0f}%)", flush=True)
                
                results.append(item)
            
            return results
            
        except Exception as e:
            print(f"   Fuzzy matching error: {e}, returning raw results", flush=True)
            return candidates
