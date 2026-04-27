from __future__ import annotations

import json

from app.schemas.analysis_schemas import AnalyzeBottlenecksRequest
from app.schemas.diagram_schemas import GenerateDiagramRequest
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


def build_generate_diagram_prompts(req: GenerateDiagramRequest) -> tuple[str, str]:
    system_prompt = (
        "Eres un experto en modelado de procesos BPMN y en la librería JointJS/joint-plus. "
        "Genera diagramas de flujo de trabajo como JSON que pueda ser deserializado directamente por JointJS graph.fromJSON(). "
        "SIEMPRE responde con JSON válido, sin markdown, sin comentarios."
    )

    phases_str = ", ".join(req.areas) if req.areas else "Recepción, Evaluación, Resolución"
    phases_list = req.areas if req.areas else ["Recepción", "Evaluación", "Resolución"]
    num_phases = len(phases_list)
    pool_width = max(900, num_phases * 280 + 60)
    phase_width = (pool_width - 60) // num_phases

    # Build example with phases (vertical columns) — single lane, all nodes in it
    phase_cells = [
        {
            "type": "sw1.Pool",
            "id": "pool-1",
            "size": {"width": pool_width, "height": 300},
            "position": {"x": 0, "y": 0},
            "attrs": {"headerText": {"text": req.policyName or "Mi Proceso"}},
            "padding": {"top": 40, "left": 0},
            "headerSide": "top",
            "contentMargin": 20,
            "minimumLaneSize": 60,
            "embeds": ["lane-main"]
        },
        {
            "type": "sw1.Lane",
            "id": "lane-main",
            "parent": "pool-1",
            "size": {"width": pool_width - 30, "height": 260},
            "position": {"x": 30, "y": 40},
            "attrs": {"headerText": {"text": ""}},
            "headerSize": 0,
            "headerSide": "left",
            "contentMargin": 20,
            "embeds": ["start-1", "act-1", "act-2", "end-1"]
        }
    ]

    # Add phases as visual columns (sw1.Lane with headerSide='top', stacked horizontally)
    for i, phase in enumerate(phases_list):
        phase_cells.append({
            "type": "sw1.Lane",
            "id": f"phase-{i+1}",
            "parent": "pool-1",
            "size": {"width": phase_width, "height": 260},
            "position": {"x": 30 + i * phase_width, "y": 40},
            "attrs": {"headerText": {"text": phase}},
            "headerSize": 30,
            "headerSide": "top",
            "contentMargin": 10,
            "embeds": []
        })

    # Add sample activities spread across phases
    phase_cells += [
        {
            "type": "sw1.Event",
            "id": "start-1",
            "parent": "lane-main",
            "eventType": "start",
            "size": {"width": 40, "height": 40},
            "position": {"x": 50, "y": 140},
            "attrs": {"label": {"text": "Inicio"}, "background": {"fill": "#4caf50"}}
        },
        {
            "type": "sw1.Activity",
            "id": "act-1",
            "parent": "lane-main",
            "activityType": "task",
            "size": {"width": 120, "height": 60},
            "position": {"x": 150, "y": 130},
            "attrs": {"label": {"text": "Primera tarea"}},
            "data": {"nodeType": "MANUAL_FORM", "label": "Primera tarea", "assignedAreaId": None}
        },
        {
            "type": "sw1.Activity",
            "id": "act-2",
            "parent": "lane-main",
            "activityType": "task",
            "size": {"width": 120, "height": 60},
            "position": {"x": 400, "y": 130},
            "attrs": {"label": {"text": "Revisar"}},
            "data": {"nodeType": "MANUAL_ACTION", "label": "Revisar", "assignedAreaId": None}
        },
        {
            "type": "sw1.Event",
            "id": "end-1",
            "parent": "lane-main",
            "eventType": "end",
            "size": {"width": 40, "height": 40},
            "position": {"x": pool_width - 100, "y": 140},
            "attrs": {"label": {"text": "Fin"}, "background": {"fill": "#f44336"}}
        },
        {"type": "bpmn2.Flow", "id": "f-1", "source": {"id": "start-1"}, "target": {"id": "act-1"}, "attrs": {}},
        {"type": "bpmn2.Flow", "id": "f-2", "source": {"id": "act-1"}, "target": {"id": "act-2"}, "attrs": {}},
        {"type": "bpmn2.Flow", "id": "f-3", "source": {"id": "act-2"}, "target": {"id": "end-1"}, "attrs": {}}
    ]

    example = {"cells": phase_cells}

    user_prompt = (
        f"Organización: {req.organizationName}\n"
        f"Política/Proceso: {req.policyName}\n"
        f"Descripción: {req.policyDescription}\n"
        f"Fases del proceso (columnas verticales): {phases_str}\n"
        f"Idioma de etiquetas: {req.language}\n\n"
        "═══════════════════════════════════════════\n"
        "REGLAS OBLIGATORIAS — incumplirlas invalida el diagrama:\n"
        "═══════════════════════════════════════════\n"
        "1. ESTRUCTURA DE FASES (CRÍTICO):\n"
        "   - USA UN SOLO lane principal (lane-main) que ocupa todo el pool.\n"
        "   - Todos los nodos (Activity, Event, Gateway) son hijos de 'lane-main'.\n"
        "   - Las fases son sw1.Lane con headerSide='top' y headerSize=30, apiladas HORIZONTALMENTE.\n"
        f"  - Crea exactamente {num_phases} fase(s) con estos nombres: {phases_str}\n"
        "   - ❌ PROHIBIDO crear múltiples lanes horizontales como swimlanes (NO apiles lanes verticalmente).\n"
        "   - ✅ Las fases marcan etapas del tiempo (columnas), no responsables (filas).\n"
        "   - La responsabilidad del área va en data.assignedAreaId de cada nodo, NO en el lane.\n\n"
        "2. CONEXIONES COMPLETAS (CRÍTICO):\n"
        "   - El diagrama DEBE tener un camino continuo desde el evento START hasta el evento END.\n"
        "   - TODOS los nodos intermedios deben tener AL MENOS un flujo de entrada Y uno de salida.\n"
        "   - Genera un bpmn2.Flow por CADA par de nodos consecutivos.\n"
        "   - ❌ PROHIBIDO dejar nodos sin conectar (nodos huérfanos).\n"
        "   - Los flows de gateways DEBEN incluir attrs.label.text con la condición ('Sí'/'No', etc.).\n\n"
        "3. TIPOS DE ELEMENTOS (distingue mayúsculas/minúsculas):\n"
        "   - Pool: type='sw1.Pool', headerSide='top', padding={top:40,left:0}, embeds=['lane-main']\n"
        "   - Lane principal: type='sw1.Lane', id='lane-main', headerSize=0, parent=<poolId>\n"
        "   - Fase columna: type='sw1.Lane', headerSide='top', headerSize=30, parent=<poolId>, embeds=[]\n"
        "   - Evento inicio: type='sw1.Event', eventType='start', parent='lane-main'\n"
        "   - Evento fin: type='sw1.Event', eventType='end', parent='lane-main'\n"
        "   - Tarea formulario: type='sw1.Activity', activityType='task', data.nodeType='MANUAL_FORM', parent='lane-main'\n"
        "   - Tarea acción: type='sw1.Activity', activityType='task', data.nodeType='MANUAL_ACTION', parent='lane-main'\n"
        "   - Tarea cliente: type='sw1.Activity', activityType='task', data.nodeType='CLIENT_TASK', parent='lane-main'\n"
        "   - Notificación: type='sw1.Activity', activityType='task', data.nodeType='NOTIFICATION', parent='lane-main'\n"
        "   - Gateway exclusivo: type='sw1.Gateway', gatewayType='exclusive', parent='lane-main'\n"
        "   - Gateway paralelo: type='sw1.Gateway', gatewayType='parallel', parent='lane-main'\n"
        "   - Flujo: type='bpmn2.Flow', source={id:'...'}, target={id:'...'} — SIN parent\n\n"
        "4. IDs únicos. Usa prefijos: pool-, phase-, start-, end-, act-, gw-, f-\n"
        "5. POSICIONES horizontales:\n"
        f"   - Pool en (0,0), width={pool_width}px, height>=300px.\n"
        f"   - lane-main: x=30, y=40, width={pool_width-30}, height=pool.height-40.\n"
        f"   - Fases: ancho={phase_width}px cada una, x=30+(i*{phase_width}), y=40, height=pool.height-40.\n"
        "   - Distribuye los nodos horizontalmente de izquierda a derecha según la fase a la que pertenecen.\n"
        "   - Separa nodos al menos 140px horizontalmente. Y de nodos: centrado en la lane (~130-150px desde el top de la lane).\n"
        "6. TAMAÑOS: Activity {width:120,height:60}; Event {width:40,height:40}; Gateway {width:40,height:40}.\n"
        "7. data.assignedAreaId: dejar null (el diseñador lo asignará manualmente).\n\n"
        f"Ejemplo de estructura con {num_phases} fase(s):\n"
        f"{json.dumps(example, ensure_ascii=False, indent=2)}\n\n"
        "Devuelve SOLO el JSON con la clave 'diagram' que contiene el objeto con 'cells':\n"
        '{ "diagram": { "cells": [...] } }'
    )
    return system_prompt, user_prompt
