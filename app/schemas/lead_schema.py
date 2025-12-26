from typing import Optional, Annotated
from pydantic import BaseModel, EmailStr, Field, BeforeValidator, ConfigDict

# usando pydantic para schemas (contratos) de validação
# converte o ObjectId para string para facilitar o uso no frontend (type annotation)
PyObjectId = Annotated[str, BeforeValidator(str)]

# Schema base commum a todos
class LeadBase(BaseModel):
    name: str = Field(..., min_length=3, example="Lionel Messi")
    email: EmailStr = Field(..., example="lionel@messi.com")
    phone: str = Field(..., min_length=8, pattern=r"^\+?[0-9\s\-\(\)]+$", example="+55 11 99999-9999")

# schema de entrada (POST /leads) vem do user...
class LeadCreate(LeadBase):
    pass
    # birth_date vem da API externa, nao do user

# schema de resposta (GET /leads/{id}) vai pro user no frontend...
class LeadResponse(LeadBase):
    # Mapeia o _id do Mongo para id string
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    birth_date: Optional[str] = None

    # Configuração necessária para aceitar tanto 'id' quanto '_id' (gemini q fez...)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "id": "65b9f... (ObjectId)",
                "name": "Lionel Messi",
                "email": "lionel@messi.com",
                "phone": "+55 11 99999-9999",
                "birth_date": "1998-02-05"
            }
        }
    )

# schema de como o dado fica no banco
class LeadInDB(LeadBase):
    birth_date: Optional[str] = None