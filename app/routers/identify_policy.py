from __future__ import annotations

import json
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.llm_service import call_llm

logger = logging.getLogger(__name__)

router = APIRouter()

CONFIDENCE_THRESHOLD = 40.0


class IdentifyPolicyRequest(BaseModel):
    text: str
    organizationId: str
    availablePolicies: list[dict] = []  # [{policyKey, policyId, name, description}]


class IdentifyPolicyResponse(BaseModel):
    policyKey: str | None
    policyId: str | None
    confidence: float
    suggestion: str


@router.post("/identify-policy", response_model=IdentifyPolicyResponse)
async def identify_policy(req: IdentifyPolicyRequest) -> IdentifyPolicyResponse:
    """
    Analiza el texto del usuario y sugiere la política más adecuada.
    Si confidence < 40, Spring Boot debe crear un PolicyRequest(PENDING_REVIEW).
    La IA recomienda, el ADMIN decide.
    """
    logger.info(
        "[identify-policy] org='%s' policies=%d text_len=%d",
        req.organizationId,
        len(req.availablePolicies),
        len(req.text),
    )

    policies_json = json.dumps(req.availablePolicies, ensure_ascii=False)

    system_prompt = (
        "Eres un asistente que identifica qué política de negocio corresponde a la solicitud de un usuario. "
        "Responde SOLO con un JSON con los campos: policyKey (string o null), policyId (string o null), "
        "confidence (número 0-100), suggestion (explicación breve en español)."
    )
    user_prompt = (
        f"Políticas disponibles:\n{policies_json}\n\n"
        f"Solicitud del usuario:\n{req.text}\n\n"
        "Identifica la política más adecuada. Si ninguna es adecuada, retorna policyKey=null y confidence baja."
    )

    try:
        data = await call_llm(system_prompt, user_prompt, temperature=0)
    except Exception as exc:
        logger.exception("[identify-policy] LLM call failed")
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}") from exc

    confidence = float(data.get("confidence", 0))
    policy_key = data.get("policyKey")
    policy_id = data.get("policyId")
    suggestion = data.get("suggestion", "")

    logger.info(
        "[identify-policy] OK — policyKey=%s confidence=%.1f (threshold=%s)",
        policy_key,
        confidence,
        CONFIDENCE_THRESHOLD,
    )
    # Note: if confidence < CONFIDENCE_THRESHOLD, caller (Spring Boot) must create PolicyRequest
    return IdentifyPolicyResponse(
        policyKey=policy_key,
        policyId=policy_id,
        confidence=confidence,
        suggestion=suggestion,
    )
