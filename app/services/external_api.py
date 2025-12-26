import httpx
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ExternalLeadsService:
    """
    Serviço responsável apenas pela comunicação com APIs de terceiros.
    Isola a complexidade de HTTP, Timeouts e Parsing.
    """
    
    BASE_URL = "https://dummyjson.com/users/1"

    @staticmethod
    async def get_birth_date_from_external_source() -> str | None:
        """
        Busca a data de nascimento na API externa.
        
        Regra de Negócio:
        - Em caso de sucesso: Retorna a string da data.
        - Em caso de qualquer erro (Timeout, 404, 500): Retorna None (Graceful Degradation).
          O erro é logado para debug, mas não quebra o fluxo do usuário.
        """
        async with httpx.AsyncClient() as client:
            try:
                # Timeout de 5 segundos é uma boa prática. 
                # APIs externas podem travar e não queremos prender nossa thread.
                response = await client.get(ExternalLeadsService.BASE_URL, timeout=5.0)
                
                # Levanta exceção se o status não for 2xx
                response.raise_for_status()
                
                data = response.json()
                
                # Extrai o campo birthDate. Se não existir, retorna None.
                return data.get("birthDate")

            except httpx.HTTPStatusError as e:
                # Erro de resposta da API (404, 500, etc)
                logger.error(f"Erro na API Externa (Status): {e}")
                return None
                
            except httpx.RequestError as e:
                # Erro de conexão (Timeout, DNS, Sem internet)
                logger.error(f"Erro de Conexão na API Externa: {e}")
                return None
            
            except Exception as e:
                # Qualquer outro erro imprevisto de parsing
                logger.error(f"Erro genérico ao processar dados externos: {e}")
                return None