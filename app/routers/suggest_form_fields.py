from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.schemas.form_schemas import SuggestFormFieldsRequest, SuggestFormFieldsResponse
from app.services.llm_service import call_llm
from app.services.prompt_builder import build_suggest_form_fields_prompts

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/suggest-form-fields", response_model=SuggestFormFieldsResponse)
async def suggest_form_fields(req: SuggestFormFieldsRequest) -> SuggestFormFieldsResponse:
    system_prompt, user_prompt = build_suggest_form_fields_prompts(req)
    try:
        data = await call_llm(system_prompt, user_prompt, temperature=0.3)
    except Exception as exc:
        logger.exception("suggest_form_fields: LLM call failed")
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}") from exc

    return SuggestFormFieldsResponse(suggestions=data.get("suggestions", []))
