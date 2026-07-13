"""Paso 3: convertir la transcripción en minuta + TODO con un LLM."""

from __future__ import annotations

import json
from pathlib import Path

from openai import OpenAI

from .config import Config

PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "minuta.md"

# Un párrafo de resumen por cada tramo de ~5 min de reunión, acotado a un rango
# razonable (una reunión corta igual merece 2 párrafos; una muy larga no necesita
# un ensayo interminable).
MINUTES_PER_PARAGRAPH = 5
MIN_PARAGRAPHS = 2
MAX_PARAGRAPHS = 15


def target_summary_paragraphs(duration_seconds: float) -> int:
    """Cantidad de párrafos de resumen sugerida según la duración."""
    p = round(duration_seconds / 60 / MINUTES_PER_PARAGRAPH)
    return max(MIN_PARAGRAPHS, min(MAX_PARAGRAPHS, p))


def generate_minutes(
    transcript: str,
    config: Config,
    summary_paragraphs: int = MIN_PARAGRAPHS,
) -> dict:
    """Devuelve un dict con la minuta estructurada (ver prompts/minuta.md)."""
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    user_msg = (
        f"El campo \"resumen\" debe tener aproximadamente {summary_paragraphs} "
        "párrafos, separados por una línea en blanco, desarrollando en profundidad "
        "los temas y el contexto (no lo hagas escueto).\n\n"
        f"Transcripción de la reunión:\n\n{transcript}"
    )

    client = OpenAI(api_key=config.openai_api_key)
    response = client.chat.completions.create(
        model=config.llm_model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg},
        ],
    )
    content = response.choices[0].message.content or "{}"
    return json.loads(content)
