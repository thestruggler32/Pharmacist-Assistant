"""
Testing with CORRECT model names found in available models
"""
import urllib.request
import json

api_key = "AIzaSyCnPtPG9vH6V0FFh5U9CDyndCQPhOQP6Ew"

print("=" * 70)
print("Google API Key Test - Using Correct Models")
print("=" * 70)

# Test with the models that ARE available
test_models = ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-2.0-flash']

for model_name in test_models:
    print(f"\nTesting {model_name}...")
    
    gen_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{"text": "Reply with: 'The new API key works perfectly!'"}]
        }]
    }
    
    try:
        req = urllib.request.Request(
            gen_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
            
            if 'candidates' in result:
                text = result['candidates'][0]['content']['parts'][0]['text']
                print(f"  ✓✓✓ SUCCESS!")
                print(f"  Response: {text}")
                print(f"\n{'='*70}")
                print(f"API KEY IS FULLY WORKING!")
                print(f"{'='*70}")
                print(f"\nConfiguration:")
                print(f"  Key: {api_key[:20]}...")
                print(f"  Working Model: {model_name}")
                print(f"  Rate Limit: 15 RPM")
                print(f"\nThe key is ready to use in your backend!")
                exit(0)
            else:
                print(f"  ✗ Unexpected response: {result}")
                
    except urllib.error.HTTPError as e:
        error_data = e.read().decode()
        print(f"  ✗ HTTP {e.code}: {e.reason}")
        try:
            error_json = json.loads(error_data)
            print(f"  Error: {error_json.get('error', {}).get('message', '')}")
        except:
            print(f"  Raw: {error_data[:200]}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

print(f"\n{'='*70}")
print("All models failed - API key may have restrictions")
print(f"{'='*70}")
