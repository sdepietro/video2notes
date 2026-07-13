"""Paso 2: transcribir el audio con la API de OpenAI (STT)."""

from __future__ import annotations

from pathlib import Path

from openai import OpenAI

from . import audio
from .config import Config

# Límite práctico de tamaño de archivo de la API de OpenAI (~25 MB).
MAX_BYTES = 25 * 1024 * 1024

# Algunos modelos limitan la DURACIÓN del audio (no solo el peso).
# gpt-4o-transcribe / gpt-4o-mini-transcribe cortan en 1400s (~23 min).
MAX_SECONDS_BY_MODEL = {
    "gpt-4o-transcribe": 1400,
    "gpt-4o-mini-transcribe": 1400,
}


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

    max_seconds = MAX_SECONDS_BY_MODEL.get(config.stt_model)
    if max_seconds is not None:
        duration = audio.get_duration_seconds(audio_path)
        if duration > max_seconds:
            raise RuntimeError(
                f"El audio dura {duration/60:.1f} min y el modelo "
                f"'{config.stt_model}' acepta como máximo {max_seconds/60:.0f} min.\n"
                "Usá STT_MODEL=whisper-1 (sin ese límite) o esperá el chunking (Fase 2)."
            )

    client = OpenAI(api_key=config.openai_api_key)
    with audio_path.open("rb") as f:
        result = client.audio.transcriptions.create(
            model=config.stt_model,
            file=f,
        )
    return result.text
