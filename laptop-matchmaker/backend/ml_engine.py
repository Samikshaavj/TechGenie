import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3

def get_ml_recommendations(user_req, db_path="data/laptops.db"):
    # 1. Load Data
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM laptops", conn)
    conn.close()
    
    # 2. Extract features
    df['Price'] = pd.to_numeric(df['current_price_inr'], errors='coerce')
    df['Price'] = df['Price'].fillna(df['Price'].median() if not df['Price'].isnull().all() else 80000)
    df['Ram_GB'] = pd.to_numeric(df['Ram'], errors='coerce').fillna(8)
    df['Storage_GB'] = pd.to_numeric(df['Storage_GB'], errors='coerce').fillna(256)
    df['Weight_kg'] = pd.to_numeric(df['Weight'], errors='coerce').fillna(2.0)
    
    # 3. Create Ideal Vector based on user_req
    ideal_ram = 8
    ideal_storage = 256
    ideal_price = 60000
    ideal_weight = 2.0
    
    if user_req.use in ['creative', 'gaming']:
        ideal_ram = 16
        ideal_storage = 512
        ideal_price = 120000
    elif user_req.use == 'coding':
        ideal_ram = 16
        ideal_storage = 256
        ideal_price = 90000
        
    if user_req.budget == 'budget':
        ideal_price = 45000
    elif user_req.budget == 'mid':
        ideal_price = 70000
    elif user_req.budget == 'premium':
        ideal_price = 95000
    elif user_req.budget == 'ultra':
        ideal_price = 150000
        
    if user_req.portability == 'ultralight':
        ideal_weight = 1.2
    elif user_req.portability == 'power':
        ideal_weight = 2.5
        
    # Scale features
    # We want features to have similar ranges so one doesn't dominate the cosine similarity
    features = df[['Price', 'Ram_GB', 'Storage_GB', 'Weight_kg']].copy()
    
    # Add ideal row at the end
    ideal_row = pd.DataFrame([{
        'Price': ideal_price, 
        'Ram_GB': ideal_ram, 
        'Storage_GB': ideal_storage, 
        'Weight_kg': ideal_weight
    }])
    features = pd.concat([features, ideal_row], ignore_index=True)
    
    scaler = MinMaxScaler()
    features_scaled = scaler.fit_transform(features)
    
    # Calculate cosine similarity of all rows against the ideal row (last row)
    ideal_vector = features_scaled[-1].reshape(1, -1)
    laptop_vectors = features_scaled[:-1]
    
    sim_scores = cosine_similarity(laptop_vectors, ideal_vector).flatten()
    df['ml_score'] = sim_scores * 100 # convert to percentage
    
    # 4. Enforce categorical preferences (OS)
    for idx, row in df.iterrows():
        if user_req.os == 'windows' and 'mac' in str(row['OpSys']).lower():
            df.at[idx, 'ml_score'] -= 40 # heavy penalty for wrong OS
        elif user_req.os == 'mac' and 'mac' not in str(row['OpSys']).lower():
            df.at[idx, 'ml_score'] -= 40
            
    # Sort and return top 3
    top_laptops = df.nlargest(3, 'ml_score')
    
    results = []
    for idx, row in top_laptops.iterrows():
        try:
            formatted_price = f"₹{int(row['current_price_inr']):,}"
        except:
            formatted_price = f"₹{row['current_price_inr']}"
            
        final_link = row['purchase_link']
        if 'mock-' in str(final_link):
            search_query = f"{row['Company']} {row['Product']}".replace(' ', '+')
            final_link = f"https://www.amazon.in/s?k={search_query}"
            
        results.append({
            "name": f"{row['Company']} {row['Product']}",
            "price": formatted_price,
            "specs": [f"{row['Ram']}GB RAM", f"{row['Memory']}", f"{row['Inches']}\" Screen", f"{row['Weight']}kg"],
            "why": f"This laptop is a {int(row['ml_score'])}% mathematical match to your ideal profile, balancing performance, budget, and portability requirements seamlessly.",
            "purchase_link": final_link,
            "score": int(row['ml_score'])
        })
        
    return results
