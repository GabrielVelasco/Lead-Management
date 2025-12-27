# Blips Leads API

![Architecture Diagram](./architecture.png)

API RESTful assíncrona para gerenciamento de Leads.
O foco principal foi garantir **resiliência**, **organização de código** e **escalabilidade**.

---

## 🌐 Live Demo (Azure + React)

O projeto já está hospedado e funcional. Você pode testar os endpoints ou visualizar o frontend nos links:

* **API (Swagger UI):** [https://sua-api-no-azure.azurewebsites.net/docs](https://sua-api-no-azure.azurewebsites.net/docs)
* **Frontend (ReactJS):** [link_place_holder](link_place_holder)

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

## 🏗 Arquitetura e Decisões Técnicas

Para este desafio, optei por fugir do padrão "MVC básico" ou de colocar toda a lógica nas rotas. Adotei uma **Clean Architecture Simplificada**, dividindo o projeto em camadas de responsabilidade única.

A ideia aqui não foi criar complexidade desnecessária, mas sim deixar o código pronto para crescer e facilitar testes:

* **Controllers (Endpoints):** Só se preocupam com HTTP (Status codes, validação de entrada). Não sabem regra de negócio.
* **Service Layer:** Aqui vive a regra de negócio. É o "maestro" que chama a API externa, trata erros e pede para o repositório salvar.
* **Repository Layer:** Isola totalmente o MongoDB. Se amanhã quisermos trocar o Mongo por PostgreSQL, a mudança seria drástica apenas aqui, sem quebrar o resto da API.
* **Async/Await:** Como lidamos com I/O (Banco e API externa), usei `async` em tudo para não bloquear o Event Loop do Python, garantindo alta performance sob carga.

## 🛡 Integração Externa e Tolerância a Falhas

O desafio pedia uma integração com a API `dummyjson` para buscar a data de nascimento, com uma pegadinha sobre como lidar com falhas.

**Minha abordagem: Graceful Degradation.**

Em um contexto de Fintech/Negócios, um Lead é um ativo valioso (dinheiro potencial). Se a API de terceiros cair (Timeout ou Error 500), **não podemos impedir o cadastro do cliente**.

A lógica implementada no `ExternalLeadsService` é:
1.  Tenta buscar o dado com um **timeout de 5 segundos** (para não travar nossa API esperando eternamente).
2.  Se der sucesso: Salvamos o `birth_date`.
3.  Se der erro (API fora do ar, timeout, etc): Logamos o erro para monitoramento e salvamos o lead com `birth_date: null`.

Dessa forma, garantimos a conversão do lead e deixamos a correção do dado para um processo posterior (ou update manual), sem impactar a experiência do usuário.

## 📂 Estrutura de Pastas

```text
app/
├── api/            # Rotas e Endpoints
├── core/           # Configurações (Env vars, Conexão DB)
├── models/         # Definições da Coleção
├── repositories/   # Acesso direto ao Banco (CRUD)
├── schemas/        # Pydantic (Validação e Serialização)
└── services/       # Regra de Negócio e Integrações Externas