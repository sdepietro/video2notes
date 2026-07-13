"""Carga de configuración desde el entorno / .env."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Carga el .env de la raíz del proyecto (si existe).
load_dotenv()


@dataclass(frozen=True)
class Config:
    openai_api_key: str
    stt_model: str
    llm_model: str


def load_config() -> Config:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "Falta OPENAI_API_KEY. Copiá .env.example a .env y completá tu key."
        )
    return Config(
        openai_api_key=key,
        stt_model=os.getenv("STT_MODEL", "whisper-1").strip(),
        llm_model=os.getenv("LLM_MODEL", "gpt-4o").strip(),
    )
