from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class Database:
    client: AsyncIOMotorClient = None

    def connect_to_database(self):
        self.client = AsyncIOMotorClient(settings.MONGO_URL)
        print("--- Conexão com MongoDB estabelecida ---")

    def close_database_connection(self):
        if self.client:
            self.client.close()
            print("--- Conexão com MongoDB encerrada ---")
    
    def get_db(self):
        return self.client[settings.DATABASE_NAME]

db = Database()
