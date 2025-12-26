from app.repositories.lead_repository import LeadRepository
from app.schemas.lead_schema import LeadCreate
from app.services.external_api import ExternalLeadsService

class LeadService:
    def __init__(self):
        self.repository = LeadRepository() # injeta instancia do repositorio que faz CRUD de Leads...

    async def create_new_lead(self, lead_in: LeadCreate) -> dict:
        """
        Orquestra a criação do Lead:
        1. Recebe dados do usuário (ja validado pelo schema/contrato).
        2. Tenta enriquecer com dados externos (birth_date).
        3. Salva no banco.
        """
        # Converte o Pydantic para dict Python
        lead_data = lead_in.model_dump()

        # Tenta pegar 'birth_date' de fonte externa, se falhar 'birth_date == None'
        # Este modulo nao sabe nada de HTTP req, entao pede pra quem sabe ExternalLeadsService...
        birth_date = await ExternalLeadsService.get_birth_date_from_external_source()
        
        # Adiciona ao dict que sera salvo
        lead_data["birth_date"] = birth_date

        # Chama respectivo repo para salvar...
        new_lead = await self.repository.create(lead_data)
        
        return new_lead

    async def get_all_leads(self):
        return await self.repository.get_all()

    async def get_lead_details(self, lead_id: str):
        return await self.repository.get_by_id(lead_id)