import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()

api_key = os.getenv("GOOGLE_AI_STUDIO_KEY")
genai.configure(api_key=api_key)

print("Querying available Gemini models...")

try:
    models = genai.list_models()
    
    vision_models = []
    
    for model in models:
        # Check if it supports generateContent (what we need)
        if 'generateContent' in model.supported_generation_methods:
            vision_models.append({
                'name': model.name,
                'display_name': model.display_name
            })
    
    # Write to file
    with open('available_models.json', 'w', encoding='utf-8') as f:
        json.dump(vision_models, f, indent=2)
    
    print(f"Found {len(vision_models)} models that support generateContent")
    print("Saved to available_models.json")
    
    # Print just the names
    print("\nModel names:")
    for m in vision_models:
        print(f"  {m['name']}")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
