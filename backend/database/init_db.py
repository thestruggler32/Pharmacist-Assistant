import sqlite3
import os
from werkzeug.security import generate_password_hash


def init_database(db_path='backend/database/pharmacy.db'):
    """Initialize SQLite database with required tables"""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('doctor', 'pharmacist', 'patient', 'admin')),
            license_number TEXT,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Prescriptions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            uploaded_by INTEGER NOT NULL,
            image_path TEXT NOT NULL,
            ocr_data TEXT,
            approved_data TEXT,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            approved_at TIMESTAMP,
            FOREIGN KEY (uploaded_by) REFERENCES users(id)
        )
    ''')
    
    # Medicines table (curated database)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            generic_name TEXT NOT NULL,
            brand_name TEXT NOT NULL,
            strength TEXT NOT NULL,
            region TEXT DEFAULT 'Karnataka',
            city TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Corrections table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS corrections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prescription_id INTEGER NOT NULL,
            original_text TEXT NOT NULL,
            corrected_text TEXT NOT NULL,
            pharmacist_id INTEGER NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (prescription_id) REFERENCES prescriptions(id),
            FOREIGN KEY (pharmacist_id) REFERENCES users(id)
        )
    ''')
    
    # Create default admin user
    try:
        cursor.execute('''
            INSERT INTO users (username, password_hash, role, status)
            VALUES (?, ?, ?, ?)
        ''', ('admin', generate_password_hash('admin123'), 'admin', 'approved'))
    except sqlite3.IntegrityError:
        pass
    
    conn.commit()
    conn.close()
    
    print(f"Database initialized at {db_path}")


if __name__ == '__main__':
    init_database()
