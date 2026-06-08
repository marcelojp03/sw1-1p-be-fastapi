from __future__ import annotations

import io
import logging

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import Response

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/convert-document", response_class=Response)
async def convert_document(file: UploadFile = File(...)) -> Response:
    """Recibe un PDF y retorna el DOCX convertido."""
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Solo se admiten archivos PDF")

    logger.info("[convert-document] filename='%s' size=%s", file.filename, file.size)

    try:
        from pdf2docx import Converter  # type: ignore
    except ImportError:
        raise HTTPException(status_code=503, detail="pdf2docx no está instalado")

    pdf_bytes = await file.read()

    try:
        import tempfile, os

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
            tmp_pdf.write(pdf_bytes)
            pdf_path = tmp_pdf.name

        docx_path = pdf_path.replace(".pdf", ".docx")
        cv = Converter(pdf_path)
        cv.convert(docx_path, start=0, end=None)
        cv.close()

        with open(docx_path, "rb") as f:
            docx_bytes = f.read()

        os.unlink(pdf_path)
        os.unlink(docx_path)
    except Exception as exc:
        logger.exception("[convert-document] conversion failed")
        raise HTTPException(status_code=500, detail=f"Error de conversión: {exc}") from exc

    original_name = (file.filename or "document.pdf").rsplit(".", 1)[0]
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{original_name}.docx"'},
    )
