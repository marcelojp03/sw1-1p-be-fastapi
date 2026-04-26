# Instrucciones para GitHub Copilot — Backend IA (FastAPI)
## Configurable Workflow System · SW1 2026

> Este repositorio contiene los **servicios auxiliares de inteligencia artificial**.
> Solo es consumido por Spring Boot. Angular y Flutter **nunca** lo llaman directamente.

---

## Stack

- Python 3.11+
- FastAPI + Pydantic v2
- `async`/`await` en todos los endpoints
- LLM: OpenAI API o modelo local (configurable por variable de entorno)
- Sin base de datos propia (stateless; recibe contexto en cada petición)

## Prefijo de Rutas

```
/api/ai/
```

## Endpoints Principales

```
POST /api/ai/suggest-workflow        ← sugerencias de nodos/flujo al diseñar política
POST /api/ai/suggest-form-fields     ← sugerencias de campos para un formulario
POST /api/ai/analyze-bottlenecks     ← análisis de cuellos de botella en trámites
```

## Reglas Fundamentales

- **No implementar lógica del workflow aquí.** El motor vive en Spring Boot.
- **No conectarse a MongoDB** salvo autorización explícita posterior.
- Este servicio recibe contexto en el body de cada request y responde sugerencias.
- No guardar estado entre peticiones.
- Spring Boot es el único caller autorizado.

## Estructura

```
sw1-1p-be-fastapi/
├── main.py
├── app/
│   ├── routers/
│   │   ├── workflow.py      ← suggest-workflow, suggest-form-fields
│   │   └── analytics.py     ← analyze-bottlenecks
│   ├── services/
│   │   └── llm_service.py   ← abstracción del LLM
│   └── models/
│       └── schemas.py       ← Pydantic v2 schemas
├── .env.example
└── requirements.txt
```

## Variables de Entorno (`.env.example`)

```env
OPENAI_API_KEY=<tu_clave>
LLM_MODEL=gpt-4o-mini
LLM_PROVIDER=openai          # openai | local
PORT=8001
```

## Convenciones

- Usar Pydantic v2 (`BaseModel` con `model_validator`)
- Manejo de errores con `HTTPException`
- CORS: solo aceptar requests del host de Spring Boot
- No exponer este servicio al exterior (solo red interna o localhost)
