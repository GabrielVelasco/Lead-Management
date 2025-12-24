# orquestrador para pingar o banco de dados (conecta e pinga)...

from app.core.database import db

class DatabaseConnectAndPing:
    # soh de teste...

    async def connect_and_ping(self):
        try:
            db.connect_to_database()
            await db.ping_db()
            
        except Exception as e:
            raise

database_connect_and_ping = DatabaseConnectAndPing()