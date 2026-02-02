import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Test basic Gemini connectivity
api_key = os.getenv("GOOGLE_AI_STUDIO_KEY")
print(f"API Key: {'Found' if api_key else 'Missing'}")

if not api_key:
    print("ERROR: GOOGLE_AI_STUDIO_KEY not found in .env")
    exit(1)

try:
    genai.configure(api_key=api_key)
    print("✓ Gemini configured")
    
    # List available models
    print("\nAvailable models:")
    for m in genai.list_models():
        if 'gemini' in m.name.lower():
            print(f"  - {m.name}")
    
    # Try a simple text-only test first
    model = genai.GenerativeModel('gemini-1.5-pro')
    print("\n✓ Model loaded: gemini-2.0-flash-exp")
    
    response = model.generate_content("Say hello")
    print(f"✓ Text generation works: {response.text[:50]}")
    
    # Now try file upload
    test_file = "static/uploads/0b156e5a-7cf9-425a-b72a-b236c695386e_115.jpg"
    if os.path.exists(test_file):
        print(f"\n✓ Test file exists: {test_file}")
        uploaded = genai.upload_file(test_file)
        print(f"✓ File uploaded: {uploaded.name}")
        
        response = model.generate_content([uploaded, "What do you see in this image?"])
        print(f"✓ Vision works: {response.text[:100]}")
        
        genai.delete_file(uploaded.name)
        print("✓ File deleted")
    else:
        print(f"✗ Test file not found: {test_file}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
