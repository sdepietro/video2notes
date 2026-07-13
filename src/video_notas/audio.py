"""Paso 1: extraer y comprimir el audio de un video con ffmpeg."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def extract_audio(video_path: Path, out_path: Path) -> Path:
    """Extrae el audio del video a mono 16kHz mp3 (liviano para la API de STT).

    Devuelve la ruta del audio generado.
    """
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg no está instalado o no está en el PATH.")
    if not video_path.exists():
        raise FileNotFoundError(f"No existe el archivo: {video_path}")

    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",                 # sobrescribir sin preguntar
        "-i", str(video_path),
        "-vn",                # sin video
        "-ac", "1",           # mono
        "-ar", "16000",       # 16 kHz
        "-b:a", "64k",        # bitrate bajo -> archivo chico
        str(out_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg falló:\n{result.stderr[-2000:]}")
    return out_path
