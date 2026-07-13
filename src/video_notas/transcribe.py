"""Paso 2: transcribir el audio con la API de OpenAI (STT)."""

from __future__ import annotations

from pathlib import Path

from openai import OpenAI

from .config import Config

# Límite práctico de tamaño de archivo de la API de OpenAI (~25 MB).
MAX_BYTES = 25 * 1024 * 1024


def transcribe(audio_path: Path, config: Config) -> str:
    """Transcribe un archivo de audio y devuelve el texto plano.

    Fase 1: asume que el archivo entra dentro del límite de la API.
    TODO (Fase 2): partir en trozos (chunking) los audios largos y unir
    las transcripciones.
    """
    size = audio_path.stat().st_size
    if size > MAX_BYTES:
        mb = size / 1024 / 1024
        raise RuntimeError(
            f"El audio pesa {mb:.1f} MB y supera el límite de ~25 MB de la API.\n"
            "Para reuniones largas hace falta chunking (pendiente, Fase 2)."
        )

    client = OpenAI(api_key=config.openai_api_key)
    with audio_path.open("rb") as f:
        result = client.audio.transcriptions.create(
            model=config.stt_model,
            file=f,
        )
    return result.text
