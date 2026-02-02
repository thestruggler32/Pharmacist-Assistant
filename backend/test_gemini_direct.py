import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Force UTF-8 encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

api_key = os.getenv("GOOGLE_AI_STUDIO_KEY")
genai.configure(api_key=api_key)

# Test with gemini-1.5-pro
model = genai.GenerativeModel('gemini-1.5-pro')

test_file = "static/uploads/0b156e5a-7cf9-425a-b72a-b236c695386e_115.jpg"

print("Testing Gemini 1.5 Pro OCR...")
print(f"File: {test_file}")
print(f"Exists: {os.path.exists(test_file)}")

if os.path.exists(test_file):
    print("\nUploading...")
    uploaded = genai.upload_file(test_file)
    print(f"Uploaded: {uploaded.name}")
    
    prompt = """Extract all medicines from this prescription. Return JSON format:
{"medicines": [{"name": "medicine name", "dosage": "dosage", "confidence": 0.9}]}"""
    
    print("\nGenerating response...")
    response = model.generate_content([uploaded, prompt])
    
    print("\n=== RESPONSE ===")
    print(response.text[:500])
    
    genai.delete_file(uploaded.name)
    print("\nDone!")
else:
    print("ERROR: File not found")
