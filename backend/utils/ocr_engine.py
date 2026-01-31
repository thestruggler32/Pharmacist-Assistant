import os
import json
import base64
import requests # Using requests for CalStudio to be safe on endpoint structure
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()

class OCREngine:
    def __init__(self, lang='en'):
        pass # Legacy stub
    def extract_text(self, image_path):
        return []

class MistralOnlyEngine:
    """
    Mistral OCR + Correction Learner Pipeline
    1. Mistral OCR (Source of Truth)
    2. Heuristic Parsing
    3. Correction Learner (Historical & Database matching)
    """
    def __init__(self):
        self.mistral_key = os.getenv("MISTRAL_API_KEY")
        
        if self.mistral_key:
            self.mistral_client = Mistral(api_key=self.mistral_key)
        else:
            print("ERROR: Mistral Key missing")
            
        # Initialize Correction Learner
        from utils.correction_learner import CorrectionLearner
        self.learner = CorrectionLearner()

    def extract_medicines(self, image_path):
        """
        Execute the Mistral-only pipeline with learning.
        """
        try:
            # STEP 1: Mistral OCR
            raw_text = self._mistral_ocr(image_path)
            
            # STEP 2: Parse raw text
            candidates = self._parse_mistral_text(raw_text)
            
            # STEP 3: Apply Correction Learning
            results = []
            for item in candidates:
                # Only try to correct if we think it IS a medicine (has indicators)
                if item['confidence'] < 0.6: 
                     results.append(item)
                     continue 

                # Try to get a better suggestion for the medicine name
                # raw_name = item['medicine_name']
                # suggestions = self.learner.suggest_correction(raw_name)
                
                # if suggestions and suggestions[0]['confidence'] > 0.95:
                #     # Apply high-confidence correction
                #     best = suggestions[0]
                #     item['medicine_name'] = best['text']
                #     item['original_text'] = raw_name # Keep original for reference
                #     item['confidence'] = best['confidence']
                #     item['source'] = f"learned_{best['source']}"
                
                results.append(item)
            
            return results
            
        except Exception as e:
            print(f"Pipeline Error: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _mistral_ocr(self, image_path):
        """Get raw text from Mistral"""
        print("DEBUG: Mistral OCR...")
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
            
        chat_response = self.mistral_client.chat.complete(
            model="pixtral-12b-2409",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Transcribe the handwritten text from this prescription exactly. List each medicine on a new line. Output ONLY the raw text."},
                        {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_data}"}
                    ]
                }
            ]
        )
        return chat_response.choices[0].message.content

    def _parse_mistral_text(self, raw_text):
        """
        Parse raw text into structured candidates using Mistral LLM (replacing regex/CalStudio).
        This ensures high-quality extraction of Medicine Name, Strength, Dosage, etc.
        """
        print("DEBUG: Using Mistral LLM for Parsing...")
        try:
            prompt = f"""
            You are a specialized pharmacist assistant. 
            Extract medicines from the following handwritten prescription OCR text.
            
            Return a JSON array of objects with these fields:
            - medicine_name (string): Name of the medicine. Fix spelling errors if obvious.
            - strength (string): e.g., "500mg", "10ml". Empty if not found.
            - dosage (string): e.g., "1-0-1", "BD", "Once a day".
            - confidence (float): 0.0 to 1.0 (Estimate based on clarity).
            - original_text (string): The substring from the text that generated this entry.

            Ignore dates, doctor names, patient details, and unrelated text.
            Omit items that are clearly not medicines.

            OCR TEXT:
            {raw_text}
            
            Return ONLY the JSON array. Do not wrap in markdown code blocks.
            """

            chat_response = self.mistral_client.chat.complete(
                model="mistral-large-latest", 
                messages=[
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = chat_response.choices[0].message.content
            # Clean potential markdown wrappers if model ignores instruction
            content = content.replace("```json", "").replace("```", "").strip()
            
            data = json.loads(content)
            
            # Handle if it returns a dict with a key like "medicines" instead of direct array
            if isinstance(data, dict):
                # Look for lists in values
                for key, val in data.items():
                    if isinstance(val, list):
                        data = val
                        break
                if isinstance(data, dict): # Still a dict?
                    data = [] # Fallback
            
            # Normalize fields
            results = []
            for item in data:
                results.append({
                    'medicine_name': item.get('medicine_name', 'Unknown'),
                    'strength': item.get('strength', ''),
                    'dosage': item.get('dosage', ''),
                    'confidence': item.get('confidence', 0.8),
                    'original_text': item.get('original_text', ''),
                    'source': 'mistral_llm'
                })
                
            return results

        except Exception as e:
            print(f"LLM Parsing Error: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to empty list or basic regex if LLM completely fails (optional, but let's return [] for now)
            return []
