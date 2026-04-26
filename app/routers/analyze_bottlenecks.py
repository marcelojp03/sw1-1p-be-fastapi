from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.schemas.analysis_schemas import AnalyzeBottlenecksRequest, AnalyzeBottlenecksResponse
from app.services.llm_service import call_llm
from app.services.prompt_builder import build_analyze_bottlenecks_prompts

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze-bottlenecks", response_model=AnalyzeBottlenecksResponse)
async def analyze_bottlenecks(req: AnalyzeBottlenecksRequest) -> AnalyzeBottlenecksResponse:
    system_prompt, user_prompt = build_analyze_bottlenecks_prompts(req)
    try:
        data = await call_llm(system_prompt, user_prompt, temperature=0)
    except Exception as exc:
        logger.exception("analyze_bottlenecks: LLM call failed")
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}") from exc

    return AnalyzeBottlenecksResponse(
        bottlenecks=data.get("bottlenecks", []),
        generalRecommendations=data.get("generalRecommendations", []),
    )
