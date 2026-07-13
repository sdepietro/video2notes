"""Paso 1: extraer y comprimir el audio de un video con ffmpeg."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def split_audio(audio_path: Path, chunk_seconds: int, out_dir: Path) -> list[Path]:
    """Parte un audio en trozos de `chunk_seconds` y devuelve las rutas ordenadas.

    Cortar en trozos evita el "loop de repetición" de whisper-1 en archivos largos
    y mantiene cada parte por debajo de los límites de la API.
    """
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg no está instalado o no está en el PATH.")
    out_dir.mkdir(parents=True, exist_ok=True)
    pattern = str(out_dir / f"{audio_path.stem}_chunk_%04d.mp3")
    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(audio_path),
        "-f", "segment",
        "-segment_time", str(chunk_seconds),
        "-c", "copy",
        pattern,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg (segment) falló:\n{result.stderr[-2000:]}")
    return sorted(out_dir.glob(f"{audio_path.stem}_chunk_*.mp3"))


def get_duration_seconds(video_path: Path) -> float:
    """Devuelve la duración del video en segundos usando ffprobe (no cuesta nada)."""
    if shutil.which("ffprobe") is None:
        raise RuntimeError("ffprobe no está instalado (viene con ffmpeg).")
    if not video_path.exists():
        raise FileNotFoundError(f"No existe el archivo: {video_path}")

    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe falló:\n{result.stderr[-2000:]}")
    try:
        return float(result.stdout.strip())
    except ValueError as exc:
        raise RuntimeError(f"No pude leer la duración: {result.stdout!r}") from exc


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
