"""
Simple Gemini API test - no imports from other modules
"""
import os
import sys

# Force reload to avoid caching
if 'google.generativeai' in sys.modules:
    del sys.modules['google.generativeai']

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_AI_STUDIO_KEY")
print(f"Testing Gemini API...")
print(f"API Key Found: {'Yes' if api_key else 'No'}")

if not api_key:
    print("\n❌ No API key found in .env")
    print("Add: GOOGLE_AI_STUDIO_KEY=your_key_here")
    exit(1)

print(f"API Key (first 20 chars): {api_key[:20]}...")

try:
    # Configure
    genai.configure(api_key=api_key)
    print("✓ API key configured")
    
    # Try the simplest possible test - text generation with gemini-pro
    print("\nTesting gemini-pro (text only)...")
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say 'test successful'")
    print(f"✓ SUCCESS: {response.text}")
    
except Exception as e:
    print(f"\n❌ FAILED: {str(e)}")
    print("\nThis API key cannot access Google's Generative AI models.")
    print("\nPossible fixes:")
    print("1. Visit https://aistudio.google.com/apikey")
    print("2. Create a NEW API key")
    print("3. Make sure you're in the correct Google account")
    print("4. Replace the key in .env file")
