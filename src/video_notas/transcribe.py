"""Paso 2: transcribir el audio con la API de OpenAI (STT).

Para reuniones largas parte el audio en trozos y transcribe cada uno por
separado. Esto es imprescindible: `whisper-1` sobre un archivo largo se engancha
en un "loop de repetición" y alucina; cortarlo en trozos lo evita y además
mantiene cada parte por debajo de los límites de la API (25 MB / duración).
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Callable

from openai import OpenAI

from . import audio
from .config import Config

# Límite práctico de tamaño de archivo de la API de OpenAI (~25 MB).
MAX_BYTES = 25 * 1024 * 1024

# Duración de cada trozo. 5 min es corto para evitar loops y suficiente para
# mantener contexto de puntuación. Un archivo más largo que esto se parte.
CHUNK_SECONDS = 300

ProgressFn = Callable[[int, int], None]


def _transcribe_file(
    client: OpenAI, path: Path, model: str, language: str | None
) -> str:
    params = {"model": model}
    if language:
        params["language"] = language
    with path.open("rb") as f:
        return client.audio.transcriptions.create(file=f, **params).text


def transcribe(
    audio_path: Path,
    config: Config,
    on_progress: ProgressFn | None = None,
) -> str:
    """Transcribe un audio (partiéndolo en trozos si es largo) y devuelve el texto."""
    client = OpenAI(api_key=config.openai_api_key)
    duration = audio.get_duration_seconds(audio_path)

    # Audio corto: una sola llamada.
    if duration <= CHUNK_SECONDS and audio_path.stat().st_size <= MAX_BYTES:
        if on_progress:
            on_progress(1, 1)
        return _transcribe_file(client, audio_path, config.stt_model, config.language)

    # Audio largo: partir en trozos y transcribir cada uno.
    with tempfile.TemporaryDirectory(prefix="video_notas_") as tmp:
        chunks = audio.split_audio(audio_path, CHUNK_SECONDS, Path(tmp))
        total = len(chunks)
        partes: list[str] = []
        for i, chunk in enumerate(chunks, start=1):
            partes.append(
                _transcribe_file(client, chunk, config.stt_model, config.language)
            )
            if on_progress:
                on_progress(i, total)
        return "\n".join(partes).strip()
