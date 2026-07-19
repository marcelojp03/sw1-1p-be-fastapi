# SI2 G2 — Servicio IA FastAPI

[![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.x-009688.svg)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT-412991.svg)](https://openai.com/)

Asistencia inteligente para identificación de políticas y generación de workflows — UAGRM Sistemas de Información 2, Grupo 2.

---

## Stack

| Capa | Tecnología |
|---|---|
| Framework | FastAPI |
| Lenguaje | Python 3.12 |
| IA/LLM | OpenAI API (GPT) |
| WHL | faster-whisper |
| Testing | pytest |

---

## Requisitos previos

- Python 3.12 (`python --version`)
- Virtual environment configurado
- OpenAI API key con créditos disponibles

---

## Levantar el proyecto

```bash
cd sw1-1p-be-fastapi

# Crear/activar entorno virtual
python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar tests (3 tests)
pytest

# Levantar servidor (puerto 8000)
uvicorn app.main:app --reload
```

---

## Configuración

El archivo `.env` en la raíz contiene:

```env
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
```

Usar `OPENAI_BASE_URL` explícita para evitar conflictos con proxies de entorno.

---

## Estructura del proyecto

```
app/
├── main.py              — punto de entrada, routers
├── config.py             — configuración (OpenAI, CORS)
├── routers/
│   ├── ai_router.py      — endpoints de IA (identificar política, generar formulario)
│   └── document_router.py — conversión de documentos
├── services/
│   ├── llm_service.py    — cliente OpenAI
│   └── gemini_service.py — generación de formularios
└── models/
    ├── request_models.py
    └── response_models.py
```

---

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/ia/identify-policy` | Identifica política desde descripción del cliente |
| POST | `/api/ia/generate-form` | Genera estructura de formulario |
| POST | `/api/ia/suggest-fields` | Sugiere campos para un nodo |
| POST | `/api/documents/convert` | Conversión de documentos |
