from __future__ import annotations

import logging
import tempfile
import os

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class TranscribeResponse(BaseModel):
    text: str
    language: str
    duration: float


@router.post("/transcribe-audio", response_model=TranscribeResponse)
async def transcribe_audio(file: UploadFile = File(...)) -> TranscribeResponse:
    """Recibe un archivo de audio y retorna la transcripción de texto."""
    logger.info("[transcribe-audio] filename='%s'", file.filename)

    try:
        from faster_whisper import WhisperModel  # type: ignore
    except ImportError:
        raise HTTPException(status_code=503, detail="faster-whisper no está instalado")

    audio_bytes = await file.read()

    suffix = os.path.splitext(file.filename or "audio.wav")[1] or ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        audio_path = tmp.name

    try:
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, info = model.transcribe(audio_path, beam_size=5)

        text_parts: list[str] = []
        duration = 0.0
        for seg in segments:
            text_parts.append(seg.text.strip())
            duration = max(duration, seg.end)

        text = " ".join(text_parts)
        language = info.language
    except Exception as exc:
        logger.exception("[transcribe-audio] transcription failed")
        raise HTTPException(status_code=500, detail=f"Error de transcripción: {exc}") from exc
    finally:
        os.unlink(audio_path)

    logger.info("[transcribe-audio] OK — language=%s duration=%.1fs", language, duration)
    return TranscribeResponse(text=text, language=language, duration=duration)
