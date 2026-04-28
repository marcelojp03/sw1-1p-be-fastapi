FROM python:3.13-slim

WORKDIR /app

# Usuario sin privilegios
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Fuentes
COPY app/ ./app/

RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
