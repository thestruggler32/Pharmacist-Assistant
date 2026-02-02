import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.utils.regional_alternatives import regional_mapper

def test_pro_capabilities():
    print("🚀 Testing Gemini 1.5 Pro Capabilities...\n")
    
    # Complex address that requires inference, not just keyword matching
    # "HSR Layout" -> Bangalore (Common knowledge, but specific)
    complex_address = "Sector 2, HSR Layout, near Parangipalya" 
    
    print(f"Input Address: '{complex_address}'")
    
    # We want to ensure it's NOT hitting the mock logic.
    # The Mock logic only checks for 'bangalore', 'indiranagar', 'whitefield'.
    # It does NOT know 'HSR Layout' or 'Parangipalya'.
    # So if this works, it MUST be the AI.
    
    hub, state = regional_mapper.ask_gemini_hub(complex_address)
    
    print(f"\nResult:")
    print(f"  Hub Detected: {hub}")
    print(f"  State Detected: {state}")
    
    if hub == "Bangalore" and state == "Karnataka":
        print("\n✅ SUCCESS: Gemini 1.5 Pro correctly inferred the location.")
    elif hub is None:
        print("\n❌ FAILURE: API Call failed or returned nothing.")
    else:
        print(f"\n⚠️ UNEXPECTED: Got {hub}, {state}")

if __name__ == "__main__":
    test_pro_capabilities()
