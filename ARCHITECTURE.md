## Diagrama de Fluxo

### POST /leads

```
┌──────────────────┐
│  Client Request  │ {"name": "...", "email": "...", "phone": "..."}
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────┐
│  FastAPI Route Handler           │
│  create_lead()                   │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Pydantic Schema Validation      │
│  LeadCreate (auto-validated)     │  ✓ name, email, phone validation
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Dependency Injection            │
│  get_lead_service()              │  Returns LeadService instance
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────┐
│  LeadService.create_new_lead()                       │
│  1. Convert Pydantic to dict                         │
│  2. Call ExternalLeadsService for enrichment        │
└────────┬───────────────────────┬────────────────────┘
         │                       │
    ┌────▼──────────┐      ┌─────▼──────────────────┐
    │ Repository    │      │ External API Call      │
    │ .create()     │      │ dummyjson (timeout 5s) │
    │               │      │ Returns birthDate/None │
    └────┬──────────┘      └────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────┐
│  MongoDB insert_one()                                │
│  • Inserts enriched lead_data                        │
│  • MongoDB generates _id (ObjectId)                  │
└────────┬───────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────┐
│  Repository retrieves inserted document              │
│  • find_one() with inserted ObjectId                 │
└────────┬───────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────┐
│  Pydantic Response Schema Transformation             │
│  LeadResponse (with _id → id mapping)                │
└────────┬───────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────┐
│  FastAPI Returns 201 Created                         │
│  JSON Response to Client                             │
└──────────────────────────────────────────────────────┘
```

---

## Matriz Responsabilidades

| Component | Responsibility | Technology |
|-----------|-----------------|------------|
| **main.py** | App initialization, lifespan, routes setup | FastAPI, Uvicorn |
| **leads.py (Routes)** | HTTP endpoint definitions, dependency injection | FastAPI Router |
| **lead_service.py** | Business logic orchestration, data enrichment | Python |
| **lead_repository.py** | Database CRUD operations, ObjectId handling | Motor (Async MongoDB) |
| **lead_schema.py** | Request/response validation, serialization | Pydantic v2 |
| **lead_model.py** | Collection name constant | Python |
| **database.py** | MongoDB connection lifecycle | Motor AsyncIOMotorClient |
| **config.py** | Environment configuration loading | Pydantic-Settings |
| **external_api.py** | External API communication, error handling | httpx (async) |
| **logger.py** | Structured logging to stdout | Python logging |

---

## API Endpoints

| Method | Endpoint | Status | Request Model | Response Model |
|--------|----------|--------|---------------|----------------|
| POST | `/leads` | 201 | LeadCreate | LeadResponse |
| GET | `/leads` | 200 | - | List[LeadResponse] |
| GET | `/leads/{lead_id}` | 200/404 | - | LeadResponse |
| GET | `/` | 200 | - | {"status": "ok", "message": "..."} |
| GET | `/pinga` | 200/503 | - | {"status": "ok"/"error", "message": "..."} |

---

## Configuration Flow

```
.env file
  │
  ├─ MONGO_URL (mongodb://localhost:27017)
  └─ DATABASE_NAME (leads_db)
         │
         ▼
pydantic_settings.BaseSettings
         │
         ▼
Settings singleton
         │
         ▼
Database.connect_to_database() during app startup
```

---

## Error Handling Strategy

| Error Type | Source | Handling | User Impact |
|-----------|--------|----------|-------------|
| Validation Error (422) | Pydantic Schema | Auto-rejected | Clear error message |
| Invalid ObjectId | Repository | Returns None | 404 Not Found |
| External API Timeout/Error | ExternalLeadsService | Logged, birth_date=None | Lead still created |
| MongoDB Connection | Database lifespan | Logged, app fails to start | Startup error |
| Database During Ping | /pinga endpoint | Caught, returns 503 | Service unavailable signal |

---

## Environment Isolation

- **Local (docker-compose)**: Hot-reload enabled, volumes mounted
- **Production (Azure)**: CI/CD via GitHub Actions, environment secrets managed
- **Logging**: All logs to stdout (Azure App Service compatible)
