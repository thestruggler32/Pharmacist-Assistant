import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GOOGLE_AI_STUDIO_KEY")
genai.configure(api_key=api_key)

print("Querying available Gemini models with current API key...\n")
print("="*70)

try:
    models = genai.list_models()
    
    vision_models = []
    text_models = []
    
    for model in models:
        # Check if it supports generateContent (what we need)
        if 'generateContent' in model.supported_generation_methods:
            print(f"\n✓ {model.name}")
            print(f"   Display Name: {model.display_name}")
            print(f"   Description: {model.description[:100] if model.description else 'N/A'}...")
            print(f"   Methods: {', '.join(model.supported_generation_methods)}")
            
            if 'vision' in model.name.lower() or 'pro' in model.name.lower() or 'flash' in model.name.lower():
                vision_models.append(model.name)
            else:
                text_models.append(model.name)
    
    print("\n" + "="*70)
    print("\nRECOMMENDED FOR OCR (Vision Models):")
    print("="*70)
    for m in vision_models:
        print(f"  - {m}")
    
    if not vision_models:
        print("  ⚠️ NO VISION MODELS FOUND!")
        print("\n  Available text models:")
        for m in text_models:
            print(f"  - {m}")
            
except Exception as e:
    print(f"\n❌ Error listing models: {e}")
    import traceback
    traceback.print_exc()
