"""
Load all medicine datasets into SQLite database
"""

import sqlite3
import pandas as pd
import os

DB_PATH = 'database/pharmacy.db'

print("=" * 70)
print("LOADING MEDICINE DATABASES INTO SQLite")
print("=" * 70)

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Update schema to include region column
print("\n[1/3] Updating database schema...")
try:
    cursor.execute('''
        ALTER TABLE medicines ADD COLUMN region TEXT DEFAULT 'Karnataka'
    ''')
    print("✓ Added 'region' column to medicines table")
except sqlite3.OperationalError as e:
    if 'duplicate column' in str(e).lower():
        print("✓ 'region' column already exists")
    else:
        print(f"⚠ Schema update: {e}")

# Clear existing medicines
print("\n[2/3] Clearing existing medicines...")
cursor.execute('DELETE FROM medicines')
conn.commit()
print("✓ Cleared existing data")

# Load combined dataset
print("\n[3/3] Loading combined medicine dataset...")
try:
    if os.path.exists('database/medicines_all.csv'):
        df = pd.read_csv('database/medicines_all.csv')
        print(f"  Total medicines to load: {len(df)}")
        
        # Insert into database
        inserted = 0
        for _, row in df.iterrows():
            try:
                cursor.execute('''
                    INSERT INTO medicines (generic_name, brand_name, strength, region)
                    VALUES (?, ?, ?, ?)
                ''', (
                    str(row.get('name', '')),
                    str(row.get('manufacturer', '')),
                    str(row.get('strength', '')),
                    str(row.get('region', 'Karnataka'))
                ))
                inserted += 1
            except Exception as e:
                continue
        
        conn.commit()
        print(f"✓ Inserted {inserted} medicines into database")
        
        # Show regional breakdown
        print("\n  Regional breakdown:")
        cursor.execute('SELECT region, COUNT(*) FROM medicines GROUP BY region')
        for region, count in cursor.fetchall():
            print(f"    {region}: {count} medicines")
        
    else:
        print("✗ medicines_all.csv not found. Run download_medicines.py first.")
        
except Exception as e:
    print(f"✗ Error loading data: {e}")
    conn.rollback()

# Verify
print("\n" + "=" * 70)
cursor.execute('SELECT COUNT(*) FROM medicines')
total = cursor.fetchone()[0]
print(f"DATABASE LOADED: {total} total medicines")
print("=" * 70)

conn.close()
