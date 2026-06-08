from __future__ import annotations

import json
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.llm_service import call_llm

logger = logging.getLogger(__name__)

router = APIRouter()

# ──────────────────────────────────────────────
# SECURITY: Mandatory field whitelist for NL reports.
# ONLY these fields may be used to build MongoDB queries from natural language.
# This prevents injection attacks and unauthorized data exposure (OWASP A03).
# ──────────────────────────────────────────────
ALLOWED_FIELDS: set[str] = {
    # Procedure
    "status", "createdAt", "updatedAt", "policyKey", "organizationId",
    "currentNodeId", "startedAt", "completedAt",
    # Task
    "taskType", "assignedTo", "taskStatus", "dueDate",
    # Client
    "clientId",
    # Generic counts
    "count", "total",
}


def _validate_query_fields(query_plan: dict) -> None:
    """Verifica que el plan de consulta solo use campos de la whitelist."""
    raw = json.dumps(query_plan)
    # Extract potential field names — any string value that looks like a DB field
    # We check the keys used in $match, $group._id, $project
    def _check_keys(obj: object) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                # Skip MongoDB operators
                if k.startswith("$"):
                    _check_keys(v)
                    continue
                # Remove leading $ for field refs
                field = k.lstrip("$").split(".")[0]
                if field and field not in ALLOWED_FIELDS:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Campo no permitido en reporte: '{field}'. "
                               "Solo se permiten campos de la whitelist de seguridad.",
                    )
                _check_keys(v)
        elif isinstance(obj, list):
            for item in obj:
                _check_keys(item)

    _check_keys(query_plan)


class NlReportRequest(BaseModel):
    query: str
    organizationId: str


class NlReportResponse(BaseModel):
    results: list[dict]
    queryUsed: str


@router.post("/nl-report", response_model=NlReportResponse)
async def nl_report(req: NlReportRequest) -> NlReportResponse:
    """
    Genera un reporte a partir de lenguaje natural.
    SEGURIDAD: aplica whitelist de campos antes de construir cualquier consulta.
    """
    logger.info("[nl-report] org='%s' query='%s'", req.organizationId, req.query)

    system_prompt = (
        "Eres un asistente que genera planes de consulta MongoDB (aggregation pipeline) "
        "a partir de lenguaje natural. Responde SOLO con JSON: "
        '{"pipeline": [...], "collection": "procedures|tasks|clients", "description": "...", '
        '"fields": ["campo1", "campo2"]}. '
        f"Solo usa estos campos: {sorted(ALLOWED_FIELDS)}. "
        "Siempre agrega {$match: {organizationId: '<ORG>'}} como primer stage."
    )
    user_prompt = (
        f"Organización: {req.organizationId}\n"
        f"Consulta: {req.query}"
    )

    try:
        data = await call_llm(system_prompt, user_prompt, temperature=0)
    except Exception as exc:
        logger.exception("[nl-report] LLM call failed")
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}") from exc

    pipeline = data.get("pipeline", [])
    description = data.get("description", req.query)

    # ── SECURITY: validate fields before returning ──
    _validate_query_fields({"pipeline": pipeline})

    logger.info("[nl-report] OK — pipeline stages=%d", len(pipeline))

    # Return the pipeline as results (Spring Boot will execute it against MongoDB)
    return NlReportResponse(
        results=[{"pipeline": pipeline, "collection": data.get("collection", "procedures")}],
        queryUsed=description,
    )
