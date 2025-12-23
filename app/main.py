from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    db.connect_to_database()
    yield
    # Shutdown
    db.close_database_connection()

app = FastAPI(title="Leads API Fintech", version="1.0.0", lifespan=lifespan)

@app.get("/")
async def health_check():
    return {"status": "ok", "message": "API rodando de boa..."}
