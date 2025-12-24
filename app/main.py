import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pymongo.errors import ConnectionFailure
from app.core.database import db

logger = logging.getLogger("uvicorn")

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        db.connect_to_database()
        await db.ping_db()
        logger.info("Database connection established.")

    except Exception as e:
        logger.error(f"Startup connection failed: {e}")
        db.close_database_connection() # so por via de seguranca...
        raise

    yield 

    db.close_database_connection()
    logger.info("Database connection closed.")

app = FastAPI(title="Leads API", version="1.0.0", lifespan=lifespan)

@app.get("/")
async def health_check():
    return {"status": "ok", "message": "API ok..."}

@app.get('/pinga')
async def ping():
    try:
        await db.ping_db()
        logger.info("Database ping successful.")
        return {"status": "ok", "message": "Ping no MongoDB ok"} # 200 OK
    
    except ConnectionFailure as e:
        logger.warning(f"Database ping failed: {e}")
        raise HTTPException(status_code=503, detail="Database unavailable") # falha conexao com o bd (auth, network, etc)
    
    except Exception as e:
        logger.error(f"Unexpected error during ping: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")