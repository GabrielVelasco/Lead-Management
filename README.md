# Leads API

![Architecture Diagram](./architecture.png)

API RESTful assíncrona para gerenciamento de Leads.
O foco principal foi garantir **resiliência**, **organização de código** e **escalabilidade**.

---

## 🌐 Live Demo (Azure + React)

O projeto já está hospedado e funcional. Você pode testar os endpoints ou visualizar o frontend nos links:

* **API (Swagger UI):** [https://leads-mng-fadxajdpe2hfajg3.brazilsouth-01.azurewebsites.net/docs](https://leads-mng-fadxajdpe2hfajg3.brazilsouth-01.azurewebsites.net/docs)
* **Frontend (ReactJS):** [https://gabrielvelasco.github.io/Leads-front/](https://gabrielvelasco.github.io/Leads-front/)

---

## 🛠 Tech Stack

* **Linguagem:** Python 3.11 (moderna e bem compatível com as libs/framework)
* **Framework Web:** FastAPI (Alta performance, validação automática e documentacao)
* **Banco de Dados:** MongoDB (via **Motor** para driver assíncrono)
* **Containerização:** Docker & Docker Compose
* **Validação:** Pydantic v2
* **Cliente HTTP:** HTTPX (Async)
* **Testes dos Endpoints:** Pytest 

## 🚀 Como Rodar Localmente

A aplicação foi totalmente "dockerizada" para garantir que rode em qualquer máquina sem dependências locais de Python ou Mongo.

### Pré-requisitos
* Docker e Docker Compose instalados.

### Passo a Passo

1.  Clone o repositório e entre na pasta:
    ```bash
    git clone [https://github.com/seu-usuario/seu-repo.git](https://github.com/seu-usuario/seu-repo.git)
    cd seu-repo
    ```

2.  Suba os containers (API + Banco):
    ```bash
    docker-compose up --build
    ```

3.  Aguarde alguns segundos. Assim que aparecer a mensagem `--- Conexão com MongoDB estabelecida ---` nos logs, a API está pronta.

## 🧪 Testando Manualmente

O FastAPI gera automaticamente uma documentação interativa (Swagger UI).

1.  Acesse: **[http://localhost:8000/docs](http://localhost:8000/docs)**
2.  Utilize o endpoint `POST /leads` para criar um cadastro.
    * *Exemplo de Payload:*
        ```json
        {
          "name": "Dev Pleno",
          "email": "dev@fintech.com",
          "phone": "+55 11 99999-9999"
        }
        ```
3.  Utilize `GET /leads` e `GET /leads/{id}` para consultar os dados salvos.

## Testes

Execute os testes localmente usando pytest (env vars aqui sao obrigatorias por causa do Pydantic):

```bash
MONGO_URL=qqlrcoisa DATABASE_NAME=qqlrcoisa pytest -v
```

Execute este comando a partir do diretório raiz do projeto. Os testes são isolados usando mocks para validar a camada de API sem exigir uma conexão com o banco de dados.

**Integração CI/CD**: Os testes são executados automaticamente como parte do pipeline do GitHub Actions a cada push na branch `main`. Se os testes falharem, a implantação no Azure Web App é bloqueada, garantindo qualidade e confiabilidade do código.

## 🏗 Arquitetura e Decisões Técnicas

Para este desafio, optei por fugir do padrão "MVC básico" ou de colocar toda a lógica nas rotas. Adotei uma **Clean Architecture Simplificada**, dividindo o projeto em camadas de responsabilidade única.

A ideia aqui não foi criar complexidade desnecessária, mas sim deixar o código pronto para crescer e facilitar testes:

* **Controllers (Endpoints):** Só se preocupam com HTTP (Status codes, validação de entrada). Não sabem regra de negócio.
* **Service Layer:** Aqui vive a regra de negócio. É o "maestro" que chama a API externa, trata erros e pede para o repositório salvar.
* **Repository Layer:** Isola totalmente o MongoDB. Se amanhã quisermos trocar o Mongo por PostgreSQL, a mudança seria drástica apenas aqui, sem quebrar o resto da API.
* **Async/Await:** Como lidamos com I/O (Banco e API externa), usei `async` em tudo para não bloquear o Event Loop do Python, garantindo alta performance sob carga.

## 🛡 Integração Externa e Tolerância a Falhas

O desafio pedia uma integração com a API `dummyjson` para buscar a data de nascimento, com uma possível pegadinha sobre como lidar com falhas.

**Minha abordagem: Graceful Degradation.**

Em um contexto de Fintech/Negócios, um Lead é um ativo valioso (dinheiro potencial). Se a API de terceiros cair (Timeout ou Error 500), **não podemos impedir o cadastro do cliente**.

A lógica implementada no `ExternalLeadsService` é:
1.  Tenta buscar o dado com um **timeout de 5 segundos** (para não travar nossa API esperando eternamente).
2.  Se der sucesso: Salvamos o `birth_date`.
3.  Se der erro (API fora do ar, timeout, etc): Logamos o erro para monitoramento e salvamos o lead com `birth_date: null`.

Dessa forma, garantimos a conversão do lead e deixamos a correção do dado para um processo posterior (ou update manual), sem impactar a experiência do usuário.

## Matriz Responsabilidades

| Component | Responsabilidade | Tech |
|-----------|-----------------|------------|
| **main.py** | Inicializacao instancia FastAPI, lifespan, routes setup | FastAPI, Uvicorn |
| **leads.py (Routes)** | HTTP endpoint, dependency injection | FastAPI Router |
| **lead_service.py** | Logica do negocio e dados API externa | Python |
| **lead_repository.py** | CRUD na collection Leads no MongoDB | Motor (Async MongoDB) |
| **lead_schema.py** | Validacao contratos Request/response | Pydantic v2 |
| **lead_model.py** | Constante guarda nome da Leads collection no DB | Python |
| **database.py** | Instancia MongoDB | Motor AsyncIOMotorClient |
| **config.py** | Carrega env vars de forma segura | Pydantic-Settings |
| **external_api.py** | Comunicacao API externa | httpx (async) |
| **logger.py** | Logger estruturado para stout Azure | Python logging |

## 📂 Estrutura de Pastas

```text
app/
├── core/
│   ├── config.py          # Variáveis de ambiente (Pydantic Settings)
│   └── database.py        # Conexão com Mongo (Motor - Async)
│   
├── models/
│   └── lead_model.py      # Como o dado é salvo no Mongo
├── schemas/
│   └── lead_schema.py     # Pydantic (Input/Output validação)
├── repositories/
│   └── lead_repository.py # CRUD puro no Mongo
├── services/
│   ├── lead_service.py    # Lógica (Chama Repo + API Externa)
│   └── external_api.py    # Cliente HTTP para dummyjson
├── api/
│   └── v1/
│       └── endpoints/
│           └── leads.py   # Rotas (GET, POST)
└── main.py                # Entrada da aplicação
Dockerfile
docker-compose.yml
requirements.txt
README.md
