import sqlite3
import pandas as pd
import re
import os

DB_PATH = 'data/laptops.db'
CSV_PATH = 'data/laptop_price - dataset.csv'

def setup_db():
    print(f"Reading {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH, encoding='latin-1')
    
    # Pre-process columns exactly like main.py did
    
    # 1. Price
    df['current_price_inr'] = (df['Price (Euro)'] * 90).astype(int)
    
    # 2. Weight
    if 'Weight (kg)' in df.columns:
        if df['Weight (kg)'].dtype == object:
            df['Weight'] = df['Weight (kg)'].astype(str).str.replace('kg', '', regex=False).astype(float)
        else:
            df['Weight'] = df['Weight (kg)']
    else:
        df['Weight'] = 2.0
        
    # 3. RAM
    if 'RAM (GB)' in df.columns:
        if df['RAM (GB)'].dtype == object:
            df['Ram'] = df['RAM (GB)'].astype(str).str.replace('GB', '', regex=False).astype(int)
        else:
            df['Ram'] = df['RAM (GB)']
    elif 'Ram' in df.columns:
        if df['Ram'].dtype == object:
            df['Ram'] = df['Ram'].astype(str).str.replace('GB', '', regex=False).astype(int)
            
    # 4. Storage
    def extract_storage(mem_str):
        mem_str = str(mem_str).lower()
        if 'tb' in mem_str:
            match = re.search(r'(\d+)\s*tb', mem_str)
            if match:
                return int(match.group(1)) * 1024
        if 'gb' in mem_str:
            match = re.search(r'(\d+)\s*gb', mem_str)
            if match:
                return int(match.group(1))
        return 256
        
    df['Storage_GB'] = df['Memory'].apply(extract_storage)
    
    # 5. Purchase Link
    # Generate a dummy purchase link
    df['purchase_link'] = df.apply(lambda row: f"https://amazon.in/dp/mock-{str(row.name).zfill(4)}", axis=1)
    
    # Keep only columns we need for simplicity or just dump the whole thing
    # Let's dump the whole thing, it's easier.
    
    print(f"Connecting to {DB_PATH}...")
    # Delete existing db if it exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    conn = sqlite3.connect(DB_PATH)
    df.to_sql('laptops', conn, index=True, index_label='id', if_exists='replace')
    conn.close()
    
    print("Database populated successfully.")

if __name__ == "__main__":
    setup_db()
