from __future__ import annotations

import json

from app.schemas.analysis_schemas import AnalyzeBottlenecksRequest
from app.schemas.form_schemas import SuggestFormFieldsRequest
from app.schemas.workflow_schemas import SuggestWorkflowRequest


def build_suggest_workflow_prompts(req: SuggestWorkflowRequest) -> tuple[str, str]:
    system_prompt = (
        "Eres un experto en diseño de flujos de trabajo y procesos organizacionales. "
        "Analiza la política descrita y sugiere nodos adicionales para completar el flujo. "
        "Responde SOLO con JSON válido siguiendo exactamente el esquema solicitado."
    )

    existing = json.dumps(
        [n.model_dump() for n in req.existingNodes],
        ensure_ascii=False,
    )

    node_types = "MANUAL_FORM | MANUAL_ACTION | CONDITION | CLIENT_TASK | NOTIFICATION | AUTOMATIC | END"

    user_prompt = (
        f"Organización: {req.organizationName}\n"
        f"Política: {req.policyName}\n"
        f"Descripción: {req.policyDescription}\n"
        f"Nodos existentes: {existing}\n"
        f"Idioma de respuesta: {req.language}\n\n"
        f"Tipos de nodo disponibles: {node_types}\n\n"
        "Devuelve un objeto JSON con esta estructura exacta:\n"
        "{\n"
        '  "suggestions": [\n'
        '    {\n'
        '      "label": "string",\n'
        '      "type": "MANUAL_FORM|MANUAL_ACTION|CONDITION|CLIENT_TASK|NOTIFICATION|AUTOMATIC|END",\n'
        '      "description": "string",\n'
        '      "suggestedArea": "string",\n'
        '      "suggestedFields": ["string"]\n'
        "    }\n"
        "  ],\n"
        '  "suggestedTransitions": [\n'
        '    { "from": "string", "to": "string", "condition": "string o null" }\n'
        "  ]\n"
        "}"
    )
    return system_prompt, user_prompt


def build_suggest_form_fields_prompts(req: SuggestFormFieldsRequest) -> tuple[str, str]:
    system_prompt = (
        "Eres un experto en diseño de formularios para flujos de trabajo empresariales. "
        "Sugiere campos útiles para el formulario descrito. "
        "Responde SOLO con JSON válido siguiendo exactamente el esquema solicitado."
    )

    field_types = "TEXT | TEXTAREA | NUMBER | DATE | BOOLEAN | SELECT | FILE"

    user_prompt = (
        f"Política: {req.policyName}\n"
        f"Nodo: {req.nodeLabel} (tipo: {req.nodeType})\n"
        f"Área: {req.areaName}\n"
        f"Campos existentes: {req.existingFields}\n"
        f"Idioma de respuesta: {req.language}\n\n"
        f"Tipos de campo disponibles: {field_types}\n\n"
        "Devuelve un objeto JSON con esta estructura exacta:\n"
        "{\n"
        '  "suggestions": [\n'
        '    {\n'
        '      "fieldId": "string (camelCase sin espacios)",\n'
        '      "label": "string",\n'
        '      "type": "TEXT|TEXTAREA|NUMBER|DATE|BOOLEAN|SELECT|FILE",\n'
        '      "required": true|false,\n'
        '      "description": "string",\n'
        '      "options": ["string"] o null\n'
        "    }\n"
        "  ]\n"
        "}"
    )
    return system_prompt, user_prompt


def build_analyze_bottlenecks_prompts(req: AnalyzeBottlenecksRequest) -> tuple[str, str]:
    system_prompt = (
        "Eres un experto en análisis de procesos y mejora continua. "
        "Analiza las métricas de los nodos del flujo e identifica cuellos de botella. "
        "Responde SOLO con JSON válido siguiendo exactamente el esquema solicitado."
    )

    metrics_json = json.dumps(
        [m.model_dump() for m in req.metrics],
        ensure_ascii=False,
    )

    severity_levels = "LOW | MEDIUM | HIGH | CRITICAL"

    user_prompt = (
        f"Política: {req.policyName}\n"
        f"Métricas de nodos:\n{metrics_json}\n"
        f"Idioma de respuesta: {req.language}\n\n"
        f"Niveles de severidad disponibles: {severity_levels}\n\n"
        "Devuelve un objeto JSON con esta estructura exacta:\n"
        "{\n"
        '  "bottlenecks": [\n'
        '    {\n'
        '      "nodeId": "string",\n'
        '      "label": "string",\n'
        '      "severity": "LOW|MEDIUM|HIGH|CRITICAL",\n'
        '      "issue": "string",\n'
        '      "recommendation": "string"\n'
        "    }\n"
        "  ],\n"
        '  "generalRecommendations": ["string"]\n'
        "}"
    )
    return system_prompt, user_prompt
