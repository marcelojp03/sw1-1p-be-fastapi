from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.schemas.workflow_schemas import SuggestWorkflowRequest, SuggestWorkflowResponse
from app.services.llm_service import call_llm
from app.services.prompt_builder import build_suggest_workflow_prompts

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/suggest-workflow", response_model=SuggestWorkflowResponse)
async def suggest_workflow(req: SuggestWorkflowRequest) -> SuggestWorkflowResponse:
    logger.info(
        "[suggest-workflow] policy='%s' existingNodes=%d language=%s",
        req.policyName,
        len(req.existingNodes),
        req.language,
    )
    system_prompt, user_prompt = build_suggest_workflow_prompts(req)
    try:
        data = await call_llm(system_prompt, user_prompt, temperature=0)
    except Exception as exc:
        logger.exception("[suggest-workflow] LLM call failed — policy='%s'", req.policyName)
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}") from exc

    suggestions = data.get("suggestions", [])
    raw_transitions = data.get("suggestedTransitions", [])

    # Normalize "from" key (LLM may use "from_" or "from")
    transitions = []
    for t in raw_transitions:
        transitions.append(
            {
                "from_": t.get("from") or t.get("from_", ""),
                "to": t.get("to", ""),
                "condition": t.get("condition"),
            }
        )

    logger.info(
        "[suggest-workflow] OK — suggestions=%d transitions=%d",
        len(suggestions),
        len(transitions),
    )
    return SuggestWorkflowResponse(suggestions=suggestions, suggestedTransitions=transitions)
