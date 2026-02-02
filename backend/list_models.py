import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_AI_STUDIO_KEY")
genai.configure(api_key=api_key)

print("Available Gemini models with vision support:\n")
for m in genai.list_models():
    if 'gemini' in m.name.lower() and 'generateContent' in m.supported_generation_methods:
        print(f"- {m.name}")
        print(f"  Methods: {m.supported_generation_methods}")
        print()
