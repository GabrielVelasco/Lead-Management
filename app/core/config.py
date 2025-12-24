# usa pydantic (contratos, python type annotation, validacao dados...) para carregar configurações do ambiente de forma segura

from pydantic_settings import BaseSettings

# Dada class para configs da aplicação do MongoDB (carrega do .env)
class Settings(BaseSettings):
    MONGO_URL: str
    DATABASE_NAME: str

    class Config:
        env_file = ".env"

settings = Settings()
