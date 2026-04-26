from __future__ import annotations

import json
import logging
import re

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


def _extract_json(text: str) -> dict:
    """Extract JSON from an LLM response that may contain markdown fences."""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON found in response: {text[:200]}")
    return json.loads(cleaned[start : end + 1])


async def call_llm(
    system_prompt: str,
    user_prompt: str,
    temperature: float = settings.TEMPERATURE,
    max_tokens: int = settings.MAX_TOKENS,
) -> dict:
    """Call the LLM and return the parsed JSON response."""
    logger.info("call_llm: model=%s temperature=%s", settings.OPENAI_MODEL, temperature)
    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=temperature,
        max_tokens=max_tokens,
    )
    raw = response.choices[0].message.content or ""
    logger.debug("call_llm: raw response: %s", raw[:300])
    return _extract_json(raw)
