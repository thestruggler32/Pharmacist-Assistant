import google.generativeai as genai

# Hardcoded test
api_key = "AIzaSyCnPtPG9vH6V0FFh5U9CDyndCQPhOQP6Ew"
print(f"Testing key: {api_key[:10]}...")

genai.configure(api_key=api_key)

print("\nTesting simple text generation...")
try:
    # Use gemini-1.5-flash as it's more likely to be available for basic keys
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello, are you working? Reply with 'Yes, the API key is active'.")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error generating content: {e}")
