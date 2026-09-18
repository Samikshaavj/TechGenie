from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
import sqlite3
import random
from apscheduler.schedulers.background import BackgroundScheduler
import contextlib
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = 'data/laptops.db'

class RecommendationRequest(BaseModel):
    use: str = "everyday"
    budget: str = "budget"
    os: str = "either"
    portability: str = "balanced"
    graphics: str = "no"
    screen_size: str = "no_pref"
    refurbished: str = "no"

scheduler = BackgroundScheduler()

import scraper

def update_prices():
    """Background job that fetches live prices using the web scraper."""
    if not os.path.exists(DB_PATH): return
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Pick 2 random laptops to scrape to avoid getting rate limited quickly
        cursor.execute("SELECT id, Company, Product FROM laptops ORDER BY RANDOM() LIMIT 2")
        laptops = cursor.fetchall()
        
        for lid, company, product in laptops:
            laptop_name = f"{company} {product}"
            print(f"[Background Worker] Scraping live price for: {laptop_name}...")
            price_inr, purchase_link = scraper.scrape_amazon_price(laptop_name)
            
            if price_inr and purchase_link:
                cursor.execute("UPDATE laptops SET current_price_inr = ?, purchase_link = ? WHERE id = ?", 
                               (price_inr, purchase_link, lid))
                print(f"[Background Worker] SUCCESS -> {laptop_name} is now ₹{price_inr}")
            else:
                print(f"[Background Worker] FAILED -> Could not fetch price for {laptop_name}")
                
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Background Worker Error] {e}")

@app.on_event("startup")
def start_scheduler():
    scheduler.add_job(update_prices, 'interval', minutes=1)
    scheduler.start()

@app.on_event("shutdown")
def stop_scheduler():
    scheduler.shutdown()

@app.post("/api/recommend")
def recommend(req: RecommendationRequest):
    if not os.path.exists(DB_PATH):
        return {"error": "Database not found."}
        
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM laptops", conn)
    conn.close()
        
    def score_laptop(row):
        score = 0
        price_inr = row['current_price_inr']
        
        # 1. Budget
        if req.budget == 'budget':
            target = 45000
        elif req.budget == 'mid':
            target = 85000
        elif req.budget == 'premium':
            target = 100000
        elif req.budget == 'ultra':
            target = 180000
        else:
            target = 500000
            
        if price_inr <= target:
            score += 20
        else:
            score -= (price_inr - target) / 5000
            
        # 2. OS
        if req.os != 'either':
            os_map = {'windows': 'Windows', 'mac': 'macOS', 'chromeos': 'Chrome OS'}
            target_os = os_map.get(req.os, '')
            if target_os and target_os.lower() in str(row['OpSys']).lower():
                score += 30
            else:
                score -= 30
                
        # 3. Graphics
        gpu_str = str(row.get('Gpu', '')).lower()
        if req.graphics == 'yes':
            if 'nvidia' in gpu_str or 'amd' in gpu_str or 'radeon' in gpu_str or 'geforce' in gpu_str:
                score += 15
        elif req.graphics == 'no':
            if 'intel' in gpu_str or 'hd graphics' in gpu_str:
                score += 5
                
        # 4. Screen Size
        inches = float(row['Inches']) if pd.notnull(row['Inches']) else 15.6
        if req.screen_size == '13-14':
            if 13 <= inches <= 14.5:
                score += 10
        elif req.screen_size == '15-16':
            if 15 <= inches <= 16.5:
                score += 10
                
        # 5. Use Case (RAM/Storage)
        ideal_ram, ideal_storage = 8, 256
        if req.use in ['creative', 'gaming']:
            ideal_ram, ideal_storage = 16, 512
        elif req.use == 'coding':
            ideal_ram, ideal_storage = 16, 256
            
        if row['Ram'] >= ideal_ram:
            score += 10
        if row['Storage_GB'] >= ideal_storage:
            score += 10
            
        # 6. Portability
        weight = row['Weight']
        if req.portability == 'ultralight':
            if weight <= 1.4:
                score += 15
            elif weight > 1.8:
                score -= 10
        elif req.portability == 'power':
            if weight >= 2.0:
                score += 5
                
        return score

    df['MatchScore'] = df.apply(score_laptop, axis=1)
    top_laptops = df.nlargest(3, 'MatchScore')
    
    results = []
    for idx, row in top_laptops.iterrows():
        formatted_price = f"₹{row['current_price_inr']:,}"
        # Fallback to an Amazon search link if the scraper hasn't updated the mock link yet
        final_link = row['purchase_link']
        if 'mock-' in str(final_link):
            search_query = f"{row['Company']} {row['Product']}".replace(' ', '+')
            final_link = f"https://www.amazon.in/s?k={search_query}"
            
        results.append({
            "name": f"{row['Company']} {row['Product']}",
            "price": formatted_price,
            "specs": [f"{row['Ram']}GB RAM", f"{row['Memory']}", f"{row['Inches']}\" Screen", f"{row['Weight']}kg"],
            "why": f"This laptop scored {int(row['MatchScore'])} points matching your preferences, featuring a {row['CPU_Company']} {row['CPU_Type']} processor and {row['OpSys']}.",
            "purchase_link": final_link,
            "score": int(row['MatchScore'])
        })
        
    return results

# Serve React Frontend
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
