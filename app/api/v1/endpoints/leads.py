from fastapi import APIRouter, status, Depends, HTTPException
from typing import List

from app.schemas.lead_schema import LeadCreate, LeadResponse
from app.services.lead_service import LeadService

router = APIRouter()

# injecao FastAPI Dependency... facilita testes depois
def get_lead_service():
    return LeadService()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=LeadResponse)
async def create_lead(
    lead_in: LeadCreate, 
    service: LeadService = Depends(get_lead_service)
):
    """
    Cria um novo Lead.
    'lead_in' é validado pelo schema LeadCreate automaticamente...
    """
    return await service.create_new_lead(lead_in)

@router.get("/", status_code=status.HTTP_200_OK, response_model=List[LeadResponse])
async def get_leads(
    service: LeadService = Depends(get_lead_service)
):
    """
    Lista todos os leads cadastrados.
    """
    return await service.get_all_leads()

@router.get("/{lead_id}", status_code=status.HTTP_200_OK, response_model=LeadResponse)
async def get_lead_details(
    lead_id: str, 
    service: LeadService = Depends(get_lead_service)
):
    """
    Busca um lead específico pelo ID.
    Retorna 404 se o ID for inválido ou não existir.
    """
    lead = await service.get_lead_details(lead_id)
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Lead não encontrado"
        )
    
    return lead