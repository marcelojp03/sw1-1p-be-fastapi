from __future__ import annotations

from pydantic import BaseModel


class NodeMetric(BaseModel):
    nodeId: str
    label: str
    avgDurationHours: float
    pendingTasks: int
    completedTasks: int
    cancelledTasks: int


class AnalyzeBottlenecksRequest(BaseModel):
    policyName: str
    metrics: list[NodeMetric]
    language: str = "es"


class Bottleneck(BaseModel):
    nodeId: str
    label: str
    severity: str
    issue: str
    recommendation: str


class AnalyzeBottlenecksResponse(BaseModel):
    bottlenecks: list[Bottleneck]
    generalRecommendations: list[str] = []
