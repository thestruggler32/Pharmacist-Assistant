import sqlite3
import csv
import os


import json
import random

import csv
import random

def load_medicines_from_csv_big(db_path='backend/database/pharmacy.db', csv_path='backend/database/india_medicines.csv'):
    """Load REAL medicines from the big CSV into database with Hub City logic"""
    if not os.path.exists(csv_path):
        print(f"Big CSV file not found: {csv_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if table exists (it should, from init_db)
    cursor.execute('DELETE FROM medicines')
    
    print("Loading FULL medicines database (this WILL take a minute)...")
    
    count = 0
    # No Limit - Full Load
    
    # Hubs available
    hubs = {
        'Karnataka': 'Bangalore',
        'Maharashtra': 'Mumbai',
        'Tamil Nadu': 'Chennai',
        'Delhi': 'Delhi',
        'West Bengal': 'Kolkata'
    }
    regions_list = list(hubs.keys())
    
    try:
        with open(csv_path, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Map CSV columns to DB schema
                brand_name = row.get('name', '').strip()
                generic_name = row.get('short_composition1', '').strip()
                strength = row.get('pack_size_label', '').strip()
                
                # Skip invalid rows
                if not brand_name or not generic_name:
                    continue
                    
                # Randomly assign a region/hub for distribution
                # In a real app, this would come from a supplier inventory feed
                region = random.choice(regions_list)
                city = hubs[region]
                
                cursor.execute('''
                    INSERT INTO medicines (generic_name, brand_name, strength, region, city)
                    VALUES (?, ?, ?, ?, ?)
                ''', (generic_name, brand_name, strength, region, city))
                
                count += 1
                
        conn.commit()
        print(f"✓ Successfully loaded {count} real medicines from {csv_path}")
        
    except Exception as e:
        print(f"Error loading CSV: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    load_medicines_from_csv_big()
