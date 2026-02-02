import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.utils.regional_alternatives import regional_mapper

def test_hub_logic():
    print("Testing Hub & Spoke Logic...\n")
    
    # Test Case 1: Tier 1 Match (Bangalore Address -> Bangalore Hub)
    # Mock data has Karnataka medicines in 'Bangalore'
    print("--- User in Bangalore (Expect Tier 1: Next Day) ---")
    result_blr = regional_mapper.find_alternatives("Dolo", locality="Indiranagar, Bangalore")
    
    print(f"Original: {result_blr['original']}")
    print(f"Generic: {result_blr['generic_name']}")
    print(f"Hub Detected: {result_blr.get('hub_detected')}")
    print(f"State Detected: {result_blr.get('user_region')}")
    
    found_tier1 = False
    for alt in result_blr.get('alternatives', [])[:3]:
        print(f"  - {alt['brand_name']} ({alt['region']}): {alt['availability']}")
        if "Hub" in alt['availability']:
            found_tier1 = True
            
    if found_tier1:
        print("✓ Tier 1 Logic Works!\n")
    else:
        print("⚠ Tier 1 Logic Failed (Did Gemini map to Bangalore?)\n")

    # Test Case 2: Tier 2 Match (Mysore Address -> Mysore Hub?)
    # DB has no stock in Mysore, only Bangalore. So should fall back to State Match.
    print("--- User in Mysore (Expect Tier 2: Standard Shipping) ---")
    result_mys = regional_mapper.find_alternatives("Dolo", locality="Palace Road, Mysore")
    
    print(f"Hub Detected: {result_mys.get('hub_detected')}")
    
    found_tier2 = False
    for alt in result_mys.get('alternatives', [])[:3]:
        print(f"  - {alt['brand_name']} ({alt['region']}): {alt['availability']}")
        if "Standard Shipping" in alt['availability']:
            found_tier2 = True
            
    if found_tier2:
        print("✓ Tier 2 Logic Works!\n")
    else:
        print("⚠ Tier 2 Logic Failed\n")

if __name__ == "__main__":
    test_hub_logic()
