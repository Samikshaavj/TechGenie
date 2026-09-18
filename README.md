# TechGenie: AI-Powered Laptop Matchmaker 💻✨

TechGenie is a modern, full-stack web application designed to help users find their perfect laptop. Instead of making users manually filter through confusing technical specifications, TechGenie asks a series of simple lifestyle questions and uses a Machine Learning recommendation engine to calculate the mathematical best fit.

## 🚀 Architecture

TechGenie is built with a decoupled frontend/backend architecture, optimized for unified deployment on platforms like Render.

### Frontend (Client)
- **Framework:** React + Vite
- **Styling:** Vanilla CSS + TailwindCSS (for utility classes)
- **Design:** Features a futuristic "dark mode" aesthetic with dynamic glowing cards, responsive flexbox grids, and animated SVG elements.

### Backend (Server)
- **Framework:** Python FastAPI
- **Database:** SQLite (managed via Pandas)
- **Machine Learning Engine:** Scikit-Learn
- **Algorithm:** Uses **Content-Based Filtering** with **Cosine Similarity**. The engine vectorizes 1,300+ laptops into a multi-dimensional matrix (Price, RAM, Storage, Weight) and compares them against a dynamically generated "Ideal Laptop Vector" based on the user's quiz answers.
- **Scraper:** A background `APScheduler` task scrapes live pricing from Amazon India to ensure recommendations fit the user's budget accurately.

## 🛠️ Local Development Setup

To run the project locally, you will need Node.js (v18+) and Python (v3.10+).

### 1. Start the Backend
```bash
cd laptop-matchmaker/backend
python -m venv venv
.\venv\Scripts\activate  # (Windows)
# source venv/bin/activate (Mac/Linux)

pip install -r requirements.txt
python setup_db.py  # Initializes the SQLite database
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Start the Frontend
In a new terminal window:
```bash
cd laptop-matchmaker/frontend
npm install
npm run dev
```

## 🌍 Production Deployment (Render)

This repository is pre-configured for a **unified one-click deployment** on Render.com as a single Web Service. 

1. Go to Render Dashboard -> **New Web Service**.
2. Connect this repository.
3. Set the **Build Command** to: `./render-build.sh`
4. Set the **Start Command** to: `cd laptop-matchmaker/backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables**:
   - `PYTHON_VERSION`: `3.10.0`
   - `NODE_VERSION`: `20`
6. Deploy! The `render-build.sh` script will automatically compile the React frontend into static files and the FastAPI backend will serve them seamlessly alongside the API.
