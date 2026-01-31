"""
Process and normalize all medicine datasets
"""

import pandas as pd
import os

print("=" * 70)
print("PROCESSING & NORMALIZING MEDICINE DATASETS")
print("=" * 70)

try:
    all_medicines = []
    
    # 1. Load original 30 medicines
    print("\n[1/5] Loading original medicines...")
    if os.path.exists('database/medicines.csv'):
        df = pd.read_csv('database/medicines.csv')
        df['region'] = 'Karnataka'
        # Normalize columns
        if 'generic_name' in df.columns:
            df = df.rename(columns={'generic_name': 'name', 'brand_name': 'manufacturer'})
        all_medicines.append(df[['name', 'manufacturer', 'strength', 'region']])
        print(f"  ✓ Original: {len(df)} medicines")
    
    # 2. Load India dataset (sample 10K)
    print("\n[2/5] Processing India dataset...")
    if os.path.exists('database/raw/india_medicines.csv'):
        df = pd.read_csv('database/raw/india_medicines.csv')
        # Take first 10K as sample
        df = df.head(10000)
        df_processed = pd.DataFrame({
            'name': df['name'].str.strip(),
            'manufacturer': df['manufacturer_name'].fillna('Generic'),
            'strength': df['pack_size_label'].fillna(''),
            'region': 'National'
        })
        all_medicines.append(df_processed)
        print(f"  ✓ India sample: {len(df_processed)} medicines")
    
    # 3. Load KSMSCL
    print("\n[3/5] Loading KSMSCL dataset...")
    if os.path.exists('database/processed/karnataka_ksmscl.csv'):
        df = pd.read_csv('database/processed/karnataka_ksmscl.csv')
        all_medicines.append(df[['name', 'manufacturer', 'strength', 'region']])
        print(f"  ✓ KSMSCL: {len(df)} medicines")
    
    # 4. Load NHM EML
    print("\n[4/5] Loading NHM EML dataset...")
    if os.path.exists('database/processed/nhm_eml.csv'):
        df = pd.read_csv('database/processed/nhm_eml.csv')
        all_medicines.append(df[['name', 'manufacturer', 'strength', 'region']])
        print(f"  ✓ NHM EML: {len(df)} medicines")
    
    # 5. Load SIMS Mysore
    print("\n[5/5] Loading SIMS Mysore dataset...")
    if os.path.exists('database/processed/mysore_sims.csv'):
        df = pd.read_csv('database/processed/mysore_sims.csv')
        all_medicines.append(df[['name', 'manufacturer', 'strength', 'region']])
        print(f"  ✓ SIMS Mysore: {len(df)} medicines")
    
    # Combine all
    print("\n" + "=" * 70)
    print("COMBINING DATASETS")
    print("=" * 70)
    
    combined_df = pd.concat(all_medicines, ignore_index=True)
    
    # Clean data
    combined_df['name'] = combined_df['name'].astype(str).str.strip()
    combined_df['manufacturer'] = combined_df['manufacturer'].astype(str).str.strip()
    combined_df['strength'] = combined_df['strength'].astype(str).str.strip()
    combined_df['region'] = combined_df['region'].astype(str).str.strip()
    
    # Remove empty names
    combined_df = combined_df[combined_df['name'] != '']
    combined_df = combined_df[combined_df['name'] != 'nan']
    
    # Remove duplicates
    combined_df = combined_df.drop_duplicates(subset=['name', 'strength', 'region'])
    
    # Save
    combined_df.to_csv('database/medicines_all.csv', index=False)
    
    print(f"\n✓ Total medicines: {len(combined_df)}")
    print("\n  Regional breakdown:")
    for region in combined_df['region'].unique():
        count = len(combined_df[combined_df['region'] == region])
        print(f"    {region}: {count} medicines")
    
    print(f"\n✓ Saved to: database/medicines_all.csv")
    print("=" * 70)
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
