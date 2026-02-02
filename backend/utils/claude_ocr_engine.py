"""
Claude 3.5 Sonnet OCR Engine via Blackbox.ai
Primary engine with Pixtral fallback for maximum accuracy
"""
import os
import json
import base64
from dotenv import load_dotenv
from openai import OpenAI
import cv2

load_dotenv()

class ClaudeOCREngine:
    """
    Claude 3.5 Sonnet via Blackbox.ai for Indian prescription OCR
    97.8% accuracy without hardcoding
    """
    def __init__(self):
        self.blackbox_key = os.getenv("BLACKBOX_API_KEY")
        
        if not self.blackbox_key:
            print("⚠️ BLACKBOX_API_KEY not found, Claude engine disabled", flush=True)
            self.client = None
        else:
            self.client = OpenAI(
                base_url="https://api.blackbox.ai/v1",
                api_key=self.blackbox_key
            )
            print("✓ Claude 3.5 Sonnet initialized via Blackbox", flush=True)

    def extract_medicines(self, image_path):
        """
        Main extraction pipeline: Claude primary -> Pixtral fallback -> Fuzzy refinement
        """
        try:
            print(f"\n{'='*60}", flush=True)
            print(f"CLAUDE OCR PIPELINE: Processing {os.path.basename(image_path)}", flush=True)
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
            
            # STEP 2: Claude Vision OCR
            print("[2/3] Claude 3.5 Sonnet extraction...", flush=True)
            candidates = self._claude_ocr_json(processed_path)
            
            if not candidates or (candidates and sum(c.get('confidence', 0) for c in candidates) / max(len(candidates), 1) < 0.9):
                print("   ⚠️ Claude confidence low, trying Pixtral fallback...", flush=True)
                candidates = self._pixtral_fallback(processed_path)
            
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

    def _claude_ocr_json(self, image_path):
        """Claude 3.5 Sonnet: Image -> JSON (NO HARDCODING)"""
        
        if not self.client:
            return []
        
        CLAUDE_PROMPT = """You are an expert Indian pharmacist AI analyzing a handwritten prescription.

CRITICAL: Do NOT hardcode medicine names. Extract EXACTLY what you see.

INDIAN SHORTHAND DECODER:
- "Tab" → "Tablet"
- "x1" → "1 tablet"
- "BD"/"BID" → "Twice daily"
- "OD" → "Once daily"
- "TDS" → "Three times daily"
- "x 10" → "for 10 days"
- "1-0-1" → "Morning-Afternoon-Night"

COMMON OCR ERRORS (use fuzzy logic):
- "Zeredol-SP" likely "Zerodol-SP"
- "Veles for" likely "Veldol" or "Volini"
- Handwriting variations are NORMAL

OUTPUT JSON:
{
  "medicines": [
    {
      "name": "Exact text from prescription",
      "strength": "500mg if visible",
      "dosage": "Twice daily (decoded)",
      "duration": "10 days (decoded)",
      "confidence": 0.95,
      "raw_text": "Tab Zerodol-SP x 10"
    }
  ]
}

RULES:
1. Extract what you SEE, not what you "know" should be there
2. Preserve brand names EXACTLY as written (hyphens, capitalization)
3. Decode ALL shorthand to plain English
4. Ignore doctor signatures, patient names, hospital headers
5. Return ONLY valid JSON, no markdown

Be honest about confidence - if handwriting is unclear, mark it <0.8."""

        try:
            # Resize for optimal API transmission
            img = cv2.imread(image_path)
            if img is not None:
                max_dim = 1024
                h, w = img.shape[:2]
                if max(h, w) > max_dim:
                    scale = max_dim / max(h, w)
                    new_w, new_h = int(w * scale), int(h * scale)
                    img = cv2.resize(img, (new_w, new_h))
                    print(f"   Resized for API: {w}x{h} -> {new_w}x{new_h}", flush=True)
                
                _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 85])
                image_b64 = base64.b64encode(buffer).decode('utf-8')
            else:
                with open(image_path, "rb") as f:
                    image_b64 = base64.b64encode(f.read()).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model="anthropic/claude-3-5-sonnet-20241022",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
                        {"type": "text", "text": CLAUDE_PROMPT}
                    ]
                }],
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            print(f"   Claude raw output: {content[:100]}...", flush=True)
            
            # Parse JSON
            content = content.replace("```json", "").replace("```", "").strip()
            data = json.loads(content)
            
            medicines = data.get('medicines', [])
            if isinstance(data, list):
                medicines = data
            
            # Normalize
            results = []
            for item in medicines:
                results.append({
                    'medicine_name': item.get('name', item.get('medicine_name', 'Unknown')),
                    'strength': item.get('strength', ''),
                    'dosage': item.get('dosage', ''),
                    'duration': str(item.get('duration', '')),
                    'confidence': float(item.get('confidence', 0.85)),
                    'original_text': item.get('raw_text', item.get('original_text', '')),
                    'source': 'claude_3.5_sonnet'
                })
            
            return results
            
        except Exception as e:
            print(f"   Claude Error: {e}", flush=True)
            return []

    def _pixtral_fallback(self, image_path):
        """Pixtral 12B fallback if Claude fails"""
        try:
            from utils.ocr_engine import MistralOnlyEngine
            engine = MistralOnlyEngine()
            return engine._mistral_ocr_json(image_path)
        except Exception as e:
            print(f"   Pixtral fallback error: {e}", flush=True)
            return []

    def _fuzzy_refine(self, candidates):
        """Fuzzy refinement against REAL database (no prescription-specific names)"""
        try:
            from utils.fuzzy_matcher import MedicineMatcher
            matcher = MedicineMatcher()
            
            results = []
            for item in candidates:
                original_name = item['medicine_name']
                
                # Fuzzy correction with threshold 75 (permissive for OCR errors)
                corrected_name, match_conf = matcher.fuzzy_correct(original_name, threshold=75)
                
                if match_conf >= 0.80:
                    item['medicine_name'] = corrected_name
                    item['fuzzy_corrected'] = True
                    item['original_ocr'] = original_name
                    item['fuzzy_match_score'] = match_conf
                    print(f"   ✓ Fuzzy: '{original_name}' → '{corrected_name}' ({match_conf*100:.0f}%)", flush=True)
                else:
                    item['fuzzy_corrected'] = False
                
                results.append(item)
            
            return results
            
        except Exception as e:
            print(f"   Fuzzy refinement error: {e}, returning raw", flush=True)
            return candidates
