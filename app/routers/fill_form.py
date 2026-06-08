from __future__ import annotations

import json
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.llm_service import call_llm

logger = logging.getLogger(__name__)

router = APIRouter()


class FormField(BaseModel):
    fieldId: str
    label: str
    type: str  # text, number, date, select, boolean
    options: list[str] = []


class FillFormRequest(BaseModel):
    text: str
    formDefinition: list[FormField]


class FillFormResponse(BaseModel):
    fieldValues: dict[str, str | int | float | bool | None]


@router.post("/fill-form", response_model=FillFormResponse)
async def fill_form(req: FillFormRequest) -> FillFormResponse:
    """
    Dado un texto libre y la definición del formulario, extrae los valores para cada campo.
    """
    logger.info(
        "[fill-form] fields=%d text_len=%d",
        len(req.formDefinition),
        len(req.text),
    )

    fields_json = json.dumps(
        [f.model_dump() for f in req.formDefinition], ensure_ascii=False
    )

    system_prompt = (
        "Eres un asistente que extrae datos de texto libre para completar formularios. "
        "Responde SOLO con un JSON: {fieldValues: {fieldId: value, ...}}. "
        "Si no puedes determinar el valor de un campo, usa null."
    )
    user_prompt = (
        f"Definición del formulario:\n{fields_json}\n\n"
        f"Texto del usuario:\n{req.text}\n\n"
        "Extrae los valores para cada campo del formulario."
    )

    try:
        data = await call_llm(system_prompt, user_prompt, temperature=0)
    except Exception as exc:
        logger.exception("[fill-form] LLM call failed")
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}") from exc

    field_values = data.get("fieldValues", {})
    if not isinstance(field_values, dict):
        field_values = {}

    logger.info("[fill-form] OK — filled=%d", sum(1 for v in field_values.values() if v is not None))
    return FillFormResponse(fieldValues=field_values)
