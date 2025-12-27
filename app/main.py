from app.utils.logger import get_logger
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo.errors import ConnectionFailure
from app.core.database import db
from app.api.v1.endpoints import leads

# logging to stdout for Azure
logger = get_logger(__name__)

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

# Add CORS middleware - MUST be before route includes
# This configuration allows requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicit HTTP methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],  # Expose all headers to client
    max_age=3600,  # Cache preflight requests for 1 hour
)

app.router.include_router(leads.router, prefix="/leads", tags=["leads"])

@app.get("/")
async def health_check():
    return {"status": "ok", "message": "NEW MSG YEAH (testing github actions)..."}

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