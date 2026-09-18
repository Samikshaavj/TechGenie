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
from ml_engine import get_ml_recommendations

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
async def recommend(req: RecommendationRequest):
    # Pass the request to the ML engine and return results
    results = get_ml_recommendations(req, DB_PATH)
    return results

# Serve React Frontend
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
