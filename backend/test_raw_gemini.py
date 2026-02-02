import os
import sys
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GOOGLE_AI_STUDIO_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('models/gemini-2.5-pro')

# Test with actual prescription
import glob
uploads = glob.glob("static/uploads/*.png") + glob.glob("static/uploads/*.jpg")
latest = max(uploads, key=os.path.getctime)

print(f"Testing: {latest}")
print("="*70)

# Upload
uploaded = genai.upload_file(latest)
print(f"Uploaded: {uploaded.name}")

# Simple prompt to test
simple_prompt = """Extract medicines from this prescription as JSON:
{"medicines": [{"name": "Medicine name", "dosage": "dosage", "duration": "duration"}]}
Return ONLY JSON."""

response = model.generate_content([uploaded, simple_prompt])

print("\n" + "="*70)
print("RAW RESPONSE:")
print("="*70)
with open("gemini_response.txt", "w", encoding="utf-8") as f:
    f.write(response.text)
    print(response.text[:1000])

# Try to parse
print("\n" + "="*70)
print("PARSING:")
print("="*70)
try:
    content = response.text.replace("```json", "").replace("```", "").strip()
    data = json.loads(content)
    print(f"SUCCESS: {json.dumps(data, indent=2)[:500]}")
except Exception as e:
    print(f"FAILED: {e}")

genai.delete_file(uploaded.name)
