from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ExistingNode(BaseModel):
    nodeId: str
    type: str
    label: str


class SuggestWorkflowRequest(BaseModel):
    organizationName: str
    policyName: str
    policyDescription: str
    existingNodes: list[ExistingNode] = []
    language: str = "es"


class SuggestedNode(BaseModel):
    label: str
    type: str
    description: str
    suggestedArea: str
    suggestedFields: list[str] = []


class SuggestedTransition(BaseModel):
    from_: str
    to: str
    condition: Optional[str] = None

    model_config = {"populate_by_name": True}


class SuggestWorkflowResponse(BaseModel):
    suggestions: list[SuggestedNode]
    suggestedTransitions: list[SuggestedTransition] = []
