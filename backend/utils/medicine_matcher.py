"""
Enhanced medicine matcher with rapidfuzz and region filtering
"""

from rapidfuzz import fuzz, process
import sqlite3
import os


class MedicineMatcher:
    def __init__(self, db_path='database/pharmacy.db'):
        self.db_path = db_path
        self.medicines_cache = {}
        self._load_medicines()
    
    def _load_medicines(self):
        """Load all medicines from database and cache by region"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT generic_name, brand_name, strength, region FROM medicines')
            medicines = cursor.fetchall()
            
            # Group by region
            for name, brand, strength, region in medicines:
                if region not in self.medicines_cache:
                    self.medicines_cache[region] = []
                
                # Store as searchable string
                search_str = f"{name} {brand} {strength}".strip()
                self.medicines_cache[region].append({
                    'name': name,
                    'brand': brand,
                    'strength': strength,
                    'search_str': search_str
                })
            
            conn.close()
            
            # Also create "All" region with all medicines
            all_medicines = []
            for region_meds in self.medicines_cache.values():
                all_medicines.extend(region_meds)
            self.medicines_cache['All'] = all_medicines
            
        except Exception as e:
            print(f"Error loading medicines: {e}")
            self.medicines_cache = {'All': []}
    
    def find_matches(self, query, region='All', top_n=3, threshold=60):
        """
        Find top N medicine matches using rapidfuzz
        
        Args:
            query: Medicine name to search for
            region: Region to filter by ('All', 'Karnataka', 'Mysore', 'National')
            top_n: Number of top matches to return
            threshold: Minimum similarity score (0-100)
        
        Returns:
            List of dicts with match info
        """
        try:
            if not query or len(query) < 2:
                return []
            
            # Get medicines for region
            region_medicines = self.medicines_cache.get(region, self.medicines_cache.get('All', []))
            
            if not region_medicines:
                return []
            
            # Create list of search strings
            search_strings = [m['search_str'] for m in region_medicines]
            
            # Use rapidfuzz to find matches
            matches = process.extract(
                query,
                search_strings,
                scorer=fuzz.WRatio,  # Weighted ratio for better results
                limit=top_n
            )
            
            # Filter by threshold and format results
            results = []
            for match_str, score, idx in matches:
                if score >= threshold:
                    medicine = region_medicines[idx]
                    results.append({
                        'name': medicine['name'],
                        'brand': medicine['brand'],
                        'strength': medicine['strength'],
                        'score': round(score, 1),
                        'match_text': match_str
                    })
            
            return results
        
        except Exception as e:
            print(f"Error finding matches: {e}")
            return []
    
    def get_regions(self):
        """Get list of available regions"""
        return list(self.medicines_cache.keys())
    
    def get_medicine_count(self, region='All'):
        """Get count of medicines in a region"""
        return len(self.medicines_cache.get(region, []))


# Standalone function for quick matching
def quick_match(medicine_name, region='All', top_n=3):
    """Quick medicine matching function"""
    matcher = MedicineMatcher()
    return matcher.find_matches(medicine_name, region=region, top_n=top_n)


if __name__ == '__main__':
    # Test the matcher
    print("=" * 70)
    print("MEDICINE MATCHER TEST")
    print("=" * 70)
    
    matcher = MedicineMatcher()
    
    print(f"\nAvailable regions: {matcher.get_regions()}")
    print(f"Total medicines: {matcher.get_medicine_count('All')}")
    
    # Test queries
    test_queries = [
        ("Paracetamol", "Karnataka"),
        ("Betaloc", "Karnataka"),
        ("Amoxicillin", "National"),
        ("Metformin", "All")
    ]
    
    for query, region in test_queries:
        print(f"\n\nSearching for '{query}' in region '{region}':")
        matches = matcher.find_matches(query, region=region, top_n=3)
        
        if matches:
            for i, match in enumerate(matches, 1):
                print(f"  {i}. {match['name']} ({match['brand']}) - {match['strength']}")
                print(f"     Score: {match['score']}%")
        else:
            print("  No matches found")
    
    print("\n" + "=" * 70)
