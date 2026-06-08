from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class RoutingPredictRequest(BaseModel):
    procedureId: str
    currentNodeId: str
    formData: dict[str, Any] = {}
    policySnapshot: dict[str, Any] = {}


class RoutingPredictResponse(BaseModel):
    transitionId: str | None
    confidence: float
    riskScore: float
    features: dict[str, Any]


@router.post("/routing-predict", response_model=RoutingPredictResponse)
async def routing_predict(req: RoutingPredictRequest) -> RoutingPredictResponse:
    """
    Predice la próxima transición del workflow usando el modelo TensorFlow/Keras.
    La IA recomienda, el motor de workflow (Spring Boot) decide.
    """
    logger.info(
        "[routing-predict] procedure='%s' node='%s'",
        req.procedureId,
        req.currentNodeId,
    )

    try:
        result = await _predict_with_model(req)
    except Exception as exc:
        logger.exception("[routing-predict] prediction failed — falling back to heuristic")
        result = _heuristic_fallback(req)

    logger.info(
        "[routing-predict] OK — transition=%s confidence=%.2f risk=%.2f",
        result["transitionId"],
        result["confidence"],
        result["riskScore"],
    )
    return RoutingPredictResponse(**result)


async def _predict_with_model(req: RoutingPredictRequest) -> dict:
    """
    Intenta usar el modelo TensorFlow/Keras para predecir la transición.
    El modelo espera features extraídas del snapshot de la política y formData.
    """
    try:
        import numpy as np  # type: ignore
        import tensorflow as tf  # type: ignore  # noqa: F401
    except ImportError:
        raise RuntimeError("TensorFlow/numpy no está instalado")

    # Extract numeric features from formData
    features = _extract_features(req.formData, req.policySnapshot)
    feature_vector = np.array([[v for v in features.values()]], dtype=np.float32)

    # Determine available transitions from policySnapshot
    transitions = _get_transitions(req.currentNodeId, req.policySnapshot)
    if not transitions:
        return {
            "transitionId": None,
            "confidence": 0.0,
            "riskScore": 0.0,
            "features": features,
        }

    # Simple dense model inference (expects pre-trained model at /app/models/routing_model.h5)
    import os

    model_path = os.environ.get("ROUTING_MODEL_PATH", "/app/models/routing_model.h5")
    if not os.path.exists(model_path):
        raise RuntimeError(f"Modelo no encontrado en {model_path}")

    model = tf.keras.models.load_model(model_path)
    scores = model.predict(feature_vector, verbose=0)[0]

    best_idx = int(np.argmax(scores[: len(transitions)]))
    confidence = float(scores[best_idx])
    risk_score = float(1.0 - confidence)

    return {
        "transitionId": transitions[best_idx].get("id"),
        "confidence": round(confidence, 4),
        "riskScore": round(risk_score, 4),
        "features": features,
    }


def _heuristic_fallback(req: RoutingPredictRequest) -> dict:
    """Fallback cuando TensorFlow no está disponible: devuelve la primera transición con baja confianza."""
    transitions = _get_transitions(req.currentNodeId, req.policySnapshot)
    transition_id = transitions[0].get("id") if transitions else None
    return {
        "transitionId": transition_id,
        "confidence": 0.5,
        "riskScore": 0.5,
        "features": {},
    }


def _extract_features(form_data: dict, policy_snapshot: dict) -> dict[str, float]:
    """Convierte formData y policySnapshot a un vector de features numéricas."""
    features: dict[str, float] = {}
    for k, v in form_data.items():
        try:
            features[f"form_{k}"] = float(v)
        except (TypeError, ValueError):
            features[f"form_{k}"] = 1.0 if v else 0.0
    # Node count as context
    nodes = policy_snapshot.get("nodes", [])
    features["node_count"] = float(len(nodes))
    return features


def _get_transitions(current_node_id: str, policy_snapshot: dict) -> list[dict]:
    """Extrae las transiciones disponibles desde el nodo actual del policySnapshot."""
    transitions = policy_snapshot.get("transitions", [])
    return [t for t in transitions if t.get("fromNodeId") == current_node_id]
