import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock

from app.main import app
from app.api.v1.endpoints.leads import get_lead_service
from app.schemas.lead_schema import LeadResponse

# Teste simples, apenas do Controller (valida input, confere se devolve resposta certa)
# Mockar a camada de serviço para isolar o teste (não eh teste integracao com BD)

# --- configs (fixtures) ---

@pytest.fixture
def mock_service():
    """
    Cria um Mock do LeadService.
    Engana API que vai achar que esta usando o serviço real, mas na verdade é um mock.
    """
    return AsyncMock()

@pytest.fixture
def client(mock_service):
    """
    Cliente HTTP assíncrono para fazer as requisições.
    Substituimos a dependência real (em 'leads.get_lead_service') pelo mock.
    """
    app.dependency_overrides[get_lead_service] = lambda: mock_service
    
    # ASGITransport é necessário para testar a app FastAPI diretamente sem subir servidor
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")

# --- Testes ---

@pytest.mark.asyncio
async def test_create_lead_success(client, mock_service):
    # arrange...
    payload = {
        "name": "Teste Neymar",
        "email": "teste@exemplo.com",
        "phone": "+55 11 99999-0000"
    }
    
    # simulamos o retorno que o Service daria (com ID e birth_date preenchidos)
    mock_response_data = {
        "_id": "65b9f1a2c8f6e4b2d8e4f1a2",
        "birth_date": "1990-01-01",
        **payload
    }
    mock_service.create_new_lead.return_value = mock_response_data

    # act...
    response = await client.post("/leads/", json=payload)

    # assert...
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["birth_date"] == "1990-01-01"
    assert "_id" in data
    
    # verificar se o método do serviço foi chamado corretamente
    mock_service.create_new_lead.assert_called_once()

@pytest.mark.asyncio
async def test_create_lead_invalid_email(client):
    # teste de validação (Pydantic) - nem chega no Service

    # arrange...
    payload = {
        "name": "Teste",
        "email": "email-invalido", # sem @, etc.
        "phone": "+55 11 99999-0000"
    }

    # act...
    response = await client.post("/leads/", json=payload)

    # assert...
    assert response.status_code == 422 # Unprocessable Entity

@pytest.mark.asyncio
async def test_get_lead_not_found(client, mock_service):
    # arrange...
    fake_id = "507f1f77bcf86cd799439011"
    # simulamos que o serviço retornou None (não achou)
    mock_service.get_lead_details.return_value = None

    # act...
    response = await client.get(f"/leads/{fake_id}")

    # assert...
    assert response.status_code == 404
    assert response.json()["detail"] == "Lead não encontrado"