"""
Regional Medicine Alternatives Finder
Helps users find equivalent medicines available in their region
"""
import sqlite3
import os
from rapidfuzz import process, fuzz

class RegionalMedicineMapper:
    """Find regional alternatives for medicines"""
    
    def __init__(self, db_path=None):
        if db_path is None:
             # Cloud Compatibility: Use absolute path relative to this file
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            # Go up one level from utils/ to backend/ then into database/
            db_path = os.path.join(os.path.dirname(BASE_DIR), 'database', 'pharmacy.db')
            
        self.db_path = db_path
        self.medicine_cache = {}
        self._load_medicines()
        self._configure_gemini()
        
    def _configure_gemini(self):
        try:
            import google.generativeai as genai
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("GOOGLE_AI_STUDIO_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-pro')
                print("✓ Gemini Hub Detective configured")
            else:
                self.model = None
                print("⚠ No Gemini Key found")
        except Exception as e:
            self.model = None
            print(f"⚠ Gemini config failed: {e}")
    
    def _load_medicines(self):
        """Load all medicines from database with region AND city info"""
        if not os.path.exists(self.db_path):
            print(f"⚠ pharmacy.db not found at {self.db_path}", flush=True)
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all medicines with their generic names
            cursor.execute('''
                SELECT generic_name, brand_name, region, city, strength
                FROM medicines
            ''')
            
            for row in cursor.fetchall():
                generic_name, brand_name, region, city, strength = row
                
                if generic_name not in self.medicine_cache:
                    self.medicine_cache[generic_name] = []
                
                self.medicine_cache[generic_name].append({
                    'brand_name': brand_name,
                    'region': region if region else 'All India',
                    'city': city,
                    'strength': strength if strength else 'N/A',
                    'generic_name': generic_name
                })
            
            conn.close()
            print(f"✓ Loaded {len(self.medicine_cache)} generic medicines", flush=True)
        except Exception as e:
            print(f"⚠ Failed to load medicines from DB: {e}", flush=True)
            
    def ask_gemini_hub(self, address):
        """Ask Gemini to find the nearest Major Hub for an address (with Mock Fallback)"""
        hub = None
        state = None
        
        # 1. Try Gemini (Skipped if key invalid/expired to save time, or try-catch)
        try:
            if self.model:
                prompt = f"""
                You are a Logistics Hub Detective.
                User Address: "{address}"
                
                Map this address to the NEAREST Major City Hub from this list:
                [Bangalore, Mumbai, Chennai, Delhi, Kolkata]
                
                Also identify the State.
                
                Return JSON ONLY:
                {{ "hub_city": "CityName", "state": "StateName" }}
                """
                response = self.model.generate_content(prompt)
                import json
                text = response.text.replace('```json', '').replace('```', '').strip()
                data = json.loads(text)
                hub = data.get('hub_city')
                state = data.get('state')
        except Exception as e:
            print(f"⚠ Gemini Detective Failed: {e}. Switching to Mock.")
            
        # 2. Mock Fallback (For Demo Stability)
        if not hub:
            print(f"ℹ Using Mock Hub Logic for: {address}")
            a = address.lower()
            if 'bangalore' in a or 'indiranagar' in a or 'whitefield' in a:
                hub = 'Bangalore'
                state = 'Karnataka'
            elif 'mysore' in a or 'mangalore' in a or 'hubli' in a:
                # True Hub & Spoke: Map these cities to the Bangalore Hub
                hub = 'Bangalore' 
                state = 'Karnataka' 
            elif 'mumbai' in a or 'pune' in a:
                hub = 'Mumbai'
                state = 'Maharashtra'
            elif 'chennai' in a:
                hub = 'Chennai'
                state = 'Tamil Nadu'
            elif 'delhi' in a:
                hub = 'Delhi'
                state = 'Delhi'
                
        return hub, state

    def find_generic_name(self, medicine_name):
        """Find generic name for a brand medicine using fuzzy matching"""
        if not medicine_name:
            return None
        
        # Try exact match first
        for generic, brands in self.medicine_cache.items():
            for brand_info in brands:
                if brand_info['brand_name'].lower() == medicine_name.lower():
                    return generic
        
        # Try fuzzy match on brand names
        all_brands = []
        generic_map = {}
        for generic, brands in self.medicine_cache.items():
            for brand_info in brands:
                all_brands.append(brand_info['brand_name'])
                generic_map[brand_info['brand_name']] = generic
        
        result = process.extractOne(
            medicine_name,
            all_brands,
            scorer=fuzz.token_set_ratio
        )
        
        if result and result[1] >= 70:  # 70% match threshold
            matched_brand = result[0]
            return generic_map[matched_brand]
        
        return None

    def find_alternatives(self, medicine_name, user_region='Karnataka', locality=None):
        """
        Find regional alternatives using BROAD SQL SEARCH (Wildcard)
        """
        # 1. Detect Hub from Locality (Address)
        hub_city = None
        detected_state = user_region
        
        if locality:
            # Use Gemini to infer Hub
            ai_city, ai_state = self.ask_gemini_hub(locality)
            if ai_city:
                hub_city = ai_city
                detected_state = ai_state
        
        print(f"DEBUG: Searching DB for '%{medicine_name}%' near '{hub_city}'", flush=True)

        try:
            # 2. execute DIRECT BROAD SEARCH on Database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Wildcard search for Brand OR Generic
            query = f"%{medicine_name}%"
            cursor.execute('''
                SELECT generic_name, brand_name, region, city, strength
                FROM medicines
                WHERE brand_name LIKE ? OR generic_name LIKE ?
                LIMIT 50
            ''', (query, query))
            
            rows = cursor.fetchall()
            conn.close()
            
            alternatives = []
            for row in rows:
                g_name, b_name, reg, cty, st = row
                alternatives.append({
                    'brand_name': b_name,
                    'generic_name': g_name,
                    'region': reg,
                    'city': cty,
                    'strength': st
                })
                
            if not alternatives:
                return {
                    'original': medicine_name,
                    'generic_name': 'Unknown',
                    'user_region': detected_state,
                    'locality': locality,
                    'hub_city': hub_city,
                    'alternatives': [],
                    'message': 'No alternatives found'
                }

            # 3. Sort Buckets (Hub > State > National)
            hub_matches = []      # Tier 1 (City Match)
            state_matches = []    # Tier 2 (State Match)
            national_matches = [] # Tier 3 (All India)
            others = []
            
            for alt in alternatives:
                # Skip exact brand name match only if strictly identical
                if alt['brand_name'].lower() == medicine_name.lower():
                    # Optional: decide if we want to show itself. Let's keep it to show availability.
                    pass 
                
                status = 'Check Availability'
                
                if hub_city and alt['city'] == hub_city:
                    status = f"Available in {hub_city} Hub (Next Day)"
                    hub_matches.append({**alt, 'availability': status, 'tier': 1})
                elif alt['region'] == detected_state:
                    status = "Standard Shipping (2-3 Days)"
                    state_matches.append({**alt, 'availability': status, 'tier': 2})
                elif alt['region'] == 'All India':
                    status = "National Stock"
                    national_matches.append({**alt, 'availability': status, 'tier': 3})
                else:
                    status = f"Ships from {alt['region']}"
                    others.append({**alt, 'availability': status, 'tier': 4})
            
            sorted_alternatives = hub_matches + state_matches + national_matches + others
            
            # Infer generic name from the first result if logical
            primary_generic = sorted_alternatives[0]['generic_name'] if sorted_alternatives else "Unknown"
            
            return {
                'original': medicine_name,
                'generic_name': primary_generic,
                'user_region': detected_state,
                'locality': locality,
                'hub_detected': hub_city,
                'alternatives': sorted_alternatives[:10],
                'total_found': len(sorted_alternatives)
            }

        except Exception as e:
            print(f"BROAD SEARCH ERROR: {e}")
            return {
                'original': medicine_name,
                'generic_name': 'Error',
                'user_region': detected_state,
                'locality': locality,
                'hub_city': hub_city,
                'alternatives': [],
                'message': f"Search failed: {e}"
            }
    
    def _check_availability(self, medicine_region, user_region):
        # Deprecated by new logic inside find_alternatives
        return "Available"

# Global instance
regional_mapper = RegionalMedicineMapper()
