"""Paso 3: convertir la transcripción en minuta + TODO con un LLM."""

from __future__ import annotations

import json
from pathlib import Path

from openai import OpenAI

from .config import Config

PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "minuta.md"


def generate_minutes(transcript: str, config: Config) -> dict:
    """Devuelve un dict con la minuta estructurada (ver prompts/minuta.md)."""
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    client = OpenAI(api_key=config.openai_api_key)
    response = client.chat.completions.create(
        model=config.llm_model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Transcripción de la reunión:\n\n{transcript}"},
        ],
    )
    content = response.choices[0].message.content or "{}"
    return json.loads(content)
