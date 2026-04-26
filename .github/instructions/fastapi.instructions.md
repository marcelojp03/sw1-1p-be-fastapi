---
applyTo: "**"
---

# Instrucciones del Agente — FastAPI Backend IA

---

## Rol en la arquitectura

FastAPI es el backend **auxiliar de inteligencia artificial**. Solo recibe peticiones de Spring Boot — **nunca del frontend directamente**.

```
Angular → Spring Boot → FastAPI → LLM
```

---

## Fuente de verdad de la API de Spring Boot

**Antes de implementar cualquier integración**, lee `.github/API.md` del workspace raíz (o `API.md` en la raíz de este repo si estás en workspace solo).

Revisa qué datos envía Spring Boot en cada llamada y qué espera recibir como respuesta.

Si Spring Boot cambia un contrato — busca entradas con ⚠️ **Cambio** en `API.md` — actualiza los schemas Pydantic correspondientes en `app/schemas/`.

---

## Regla de finalización — OBLIGATORIA

Antes de declarar cualquier tarea como completada:

### 1. Verificar sintaxis

```bash
ruff check .
```

O si ruff no está disponible:

```bash
python -m py_compile app/main.py
```

### 2. Hacer commit y push a Git

```bash
git add .
git commit -m "feat(ai): <descripción breve de lo implementado>"
git push
```

---

## Reglas de arquitectura

- Python 3.11+, FastAPI, Pydantic v2.
- Prefijo de rutas: `/api/ai/`.
- Usar `async/await` siempre.
- Validar clave interna (`FASTAPI_INTERNAL_KEY`) en cada request.
- No persistir datos propios.
- LLM configurable por env var.

---

## Referencias

- Plan general: `.github/PLANNING.md` (workspace raíz)
- Detalles técnicos FastAPI: `.github/FASTAPI.md` (workspace raíz)
- **Contrato de Spring Boot (leer siempre):** `.github/API.md` (workspace raíz)
