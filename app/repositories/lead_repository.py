from bson import ObjectId
from app.core.database import db # instancia do bd (metodos para comunicacao com...)
from app.models.lead_model import LEAD_COLLECTION_NAME

class LeadRepository:
    """
    Conversa com MongoDB, sobre colecao Leads, unica responsabilidade... Nao sabe de mais nada.
    """
    
    @property
    def collection(self):
        """
        Helper para pegar a coleção correta do banco.
        """
        return db.get_db()[LEAD_COLLECTION_NAME] # retorna collection do MongoDB (com metodos para CRUD)

    async def create(self, lead_data: dict) -> dict:
        """
        Insere um novo lead no banco.
        :param lead_data: Dicionário com os dados já tratados (prontos para salvar) pelo Service (incluindo birth_date)
        """
        result = await self.collection.insert_one(lead_data)
        
        # Recupera o documento criado para retornar com o _id gerado
        created_lead = await self.collection.find_one({"_id": result.inserted_id})
        return created_lead

    async def get_all(self) -> list[dict]:
        """
        Retorna todos os leads.
        """
        leads = await self.collection.find().to_list(length=1000) # limita a 1000 por segurança (em producao, usar paginação)
        return leads

    async def get_by_id(self, id: str) -> dict | None:
        """
        Busca um lead pelo ID. Valida se o ID é um ObjectId válido antes de buscar.
        """
        if not ObjectId.is_valid(id):
            return None
            
        lead = await self.collection.find_one({"_id": ObjectId(id)})
        return lead