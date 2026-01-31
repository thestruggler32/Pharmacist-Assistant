import pandas as pd
import re

# Load full India dataset
print("Loading 400K+ medicines...")
df = pd.read_csv("india_medicines.csv")

# Karnataka indicators (manufacturers, cities, keywords)
karnataka_keywords = [
    'Karnataka', 'Bengaluru', 'Bangalore', 'Mysore', 'Mysuru',
    'Hubli', 'Belgaum', 'Belagavi', 'Mangalore', 'Dharwad',
    'Cipla', 'Sun Pharma', 'Dr. Reddy', 'Micro Labs',  # Big in Karnataka
    'KAPL', 'KSMSCL'  # Karnataka govt companies
]

# Filter by manufacturer or name containing Karnataka keywords
karnataka_mask = df['manufacturer'].str.contains('|'.join(karnataka_keywords), case=False, na=False) | \
                 df['name'].str.contains('|'.join(karnataka_keywords), case=False, na=False)

karnataka_meds = df[karnataka_mask].copy()
karnataka_meds['region'] = 'karnataka'

# Clean and deduplicate
karnataka_meds = karnataka_meds[['name', 'manufacturer', 'composition', 'pack_size', 'region']].drop_duplicates()

print(f"Found {len(karnataka_meds)} Karnataka medicines")
karnataka_meds.to_csv("karnataka_medicines.csv", index=False)
print("Saved to karnataka_medicines.csv")

# Also save top 500 most common for quick testing
top_500 = karnataka_meds.head(500)
top_500.to_csv("karnataka_top500.csv", index=False)
print("Saved top 500 to karnataka_top500.csv")