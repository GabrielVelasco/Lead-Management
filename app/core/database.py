from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.core.config import settings
import logging

logger = logging.getLogger("uvicorn")

class Database:
    client: AsyncIOMotorClient = None

    def connect_to_database(self):
        self.client = AsyncIOMotorClient(settings.MONGO_URL)
        logger.info("MongoDB client created.")

    def close_database_connection(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")
    
    def get_db(self):
        return self.client[settings.DATABASE_NAME]

    async def ping_db(self):
        try:
            await self.client.admin.command('ping')

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"MongoDB connection failed: {e}") # erro especifico de conexao/auth com o bd
            raise

        except Exception as e:
            logger.error(f"Unexpected error pinging MongoDB: {e}") # erro generico
            raise


db = Database() # instancia unica do bd