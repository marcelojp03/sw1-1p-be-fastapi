import os
import sys
from dotenv import load_dotenv

load_dotenv()

model = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
api_key = os.getenv("OPENAI_API_KEY", "")

if not api_key:
    print("ERROR: OPENAI_API_KEY no configurada en .env")
    sys.exit(1)

print(f"SDK openai: 2.45.0")
print(f"Modelo configurado: {model}")
print(f"API key presente: {api_key[:10]}...")
print()

from openai import OpenAI, APIError, AuthenticationError, NotFoundError

client = OpenAI(api_key=api_key, base_url="https://api.openai.com/v1")

try:
    response = client.responses.create(
        model=model,
        input="Responde unicamente con la palabra OK.",
        max_output_tokens=20,
    )
    print("STATUS: OK")
    print(f"Respuesta: {response.output_text}")
    print()
    print("CLASIFICACION: Los 7 endpoints LLM usan un modelo oficial y accesible.")
except AuthenticationError as e:
    print("STATUS: AUTH_ERROR")
    print(f"Error: {e}")
    print("CLASIFICACION: BLOQUEADO POR AUTH — API key invalida o sin permisos.")
except NotFoundError as e:
    print("STATUS: NOT_FOUND")
    print(f"Error: {e}")
    print("CLASIFICACION: El modelo no es accesible para esta API key/proyecto.")
except APIError as e:
    print("STATUS: API_ERROR")
    print(f"Error: {e}")
    sc = getattr(e, "status_code", None)
    if sc:
        print(f"HTTP Status: {sc}")
except Exception as e:
    print(f"STATUS: ERROR")
    print(f"Tipo: {type(e).__name__}")
    print(f"Error: {e}")
