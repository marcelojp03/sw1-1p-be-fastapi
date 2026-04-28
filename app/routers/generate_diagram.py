from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.schemas.diagram_schemas import GenerateDiagramRequest, GenerateDiagramResponse
from app.services.llm_service import call_llm
from app.services.prompt_builder import build_generate_diagram_prompts

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate-diagram", response_model=GenerateDiagramResponse)
async def generate_diagram(req: GenerateDiagramRequest) -> GenerateDiagramResponse:
    logger.info(
        "[generate-diagram] policy='%s' areas=%s language=%s",
        req.policyName,
        req.areas,
        req.language,
    )
    system_prompt, user_prompt = build_generate_diagram_prompts(req)
    try:
        data = await call_llm(system_prompt, user_prompt, temperature=0.2)
    except Exception as exc:
        logger.exception("[generate-diagram] LLM call failed — policy='%s'", req.policyName)
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}") from exc

    diagram = data.get("diagram")
    if not isinstance(diagram, dict) or "cells" not in diagram:
        logger.error(
            "[generate-diagram] unexpected LLM response shape: %s — policy='%s'",
            list(data.keys()),
            req.policyName,
        )
        raise HTTPException(status_code=502, detail="La IA no devolvió un diagrama válido")

    cells = diagram.get("cells", [])
    node_count = sum(1 for c in cells if c.get("type", "") != "bpmn2.Flow")
    flow_count = sum(1 for c in cells if c.get("type", "") == "bpmn2.Flow")
    logger.info(
        "[generate-diagram] OK — cells=%d nodes=%d flows=%d — policy='%s'",
        len(cells),
        node_count,
        flow_count,
        req.policyName,
    )
    return GenerateDiagramResponse(diagram=diagram)
