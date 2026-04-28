from __future__ import annotations

from pydantic import BaseModel


class GenerateDiagramRequest(BaseModel):
    organizationName: str
    policyName: str
    policyDescription: str
    areas: list[str]  # nombres de áreas/departamentos para usar como swimlanes
    language: str = "es"


class GenerateDiagramResponse(BaseModel):
    diagram: dict  # graph.toJSON() compatible — { "cells": [...] }
