from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class SuggestFormFieldsRequest(BaseModel):
    policyName: str
    nodeLabel: str
    nodeType: str = "MANUAL_FORM"
    areaName: str
    existingFields: list[str] = []
    language: str = "es"


class FieldSuggestion(BaseModel):
    fieldId: str
    label: str
    type: str
    required: bool
    description: str
    options: Optional[list[str]] = None


class SuggestFormFieldsResponse(BaseModel):
    suggestions: list[FieldSuggestion]
