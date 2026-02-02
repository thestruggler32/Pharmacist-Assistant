from .gemini_client import GeminiClient
import json

class RegionalMedicineMapper:
    def __init__(self, db_path='backend/database/pharmacy.db'):
        self.db_path = db_path
        self.medicine_cache = {}
        self.gemini_client = GeminiClient()
        self._load_medicines()
    
    def _load_medicines(self):
        # ... (same as before) ...
        # Simplified for brevity in this replace, actual implementation needs full code
        pass

    def get_region_for_locality(self, locality):
        """Use Gemini to map a specific locality to a broader region available in DB"""
        if not locality:
            return "Karnataka" # Default
            
        try:
            prompt = f"""
            I have a database of medicines categorized by these regions: 
            ['Karnataka', 'Tamil Nadu', 'Maharashtra', 'Delhi', 'North India', 'South India', 'All India'].
            
            The user is located in: "{locality}".
            
            Which of my database regions is the best match for this user? 
            Return ONLY the region name as a string. If unsure, return 'All India'.
            """
            
            response = self.gemini_client.generate_content(prompt)
            data = json.loads(response) if isinstance(response, str) else response
            # Cleanup incase it returns JSON object or extra text
            region = str(data).strip().replace('"','').replace("'", "")
            
            # Basic validation
            valid_regions = ['Karnataka', 'Tamil Nadu', 'Maharashtra', 'Delhi', 'North India', 'South India', 'All India']
            if region in valid_regions:
                return region
            return "Karnataka" # Default fallback
            
        except Exception as e:
            print(f"Locality mapping failed: {e}")
            return "Karnataka"

    # ... (rest of methods) ...
