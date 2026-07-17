FROM python:3.12-slim AS builder

RUN pip install --no-cache-dir --timeout=300 -i https://pypi.org/simple/ \
    fastapi>=0.115.5 uvicorn[standard]>=0.32.1 \
    pydantic>=2.11.0 pydantic-settings>=2.7.0 \
    openai>=1.57.4 python-dotenv>=1.0.1 httpx>=0.28.1 \
    python-multipart>=0.0.12

FROM python:3.12-slim

WORKDIR /app
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Heavy deps (whisper, pdf2docx) are NOT included for production
COPY app/ ./app/
RUN chown -R appuser:appgroup /app

USER appuser
EXPOSE 8001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
