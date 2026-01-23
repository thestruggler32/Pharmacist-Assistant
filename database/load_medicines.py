import sqlite3
import csv
import os


def load_medicines_from_csv(db_path='database/pharmacy.db', csv_path='database/medicines.csv'):
    """Load medicines from CSV into database"""
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Clear existing medicines
    cursor.execute('DELETE FROM medicines')
    
    # Load from CSV
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute('''
                INSERT INTO medicines (generic_name, brand_name, strength, region)
                VALUES (?, ?, ?, ?)
            ''', (row['generic_name'], row['brand_name'], row['strength'], row['region']))
    
    conn.commit()
    conn.close()
    
    print(f"Loaded medicines from {csv_path}")


if __name__ == '__main__':
    load_medicines_from_csv()
