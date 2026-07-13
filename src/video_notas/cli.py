"""CLI: video -> minuta + TODO."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from rich.console import Console

from . import audio, minutes, render, transcribe
from .config import load_config

console = Console()


def procesar(video: Path, out_dir: Path, keep_transcript: bool) -> Path:
    config = load_config()
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = video.stem

    with console.status("[1/4] Extrayendo audio con ffmpeg..."):
        audio_path = audio.extract_audio(video, out_dir / f"{stem}.mp3")

    with console.status("[2/4] Transcribiendo audio (OpenAI)..."):
        transcript = transcribe.transcribe(audio_path, config)
    if keep_transcript:
        (out_dir / f"{stem}.transcript.txt").write_text(transcript, encoding="utf-8")

    with console.status("[3/4] Generando minuta y TODO (OpenAI)..."):
        minuta = minutes.generate_minutes(transcript, config)

    console.print("[4/4] Renderizando Markdown...")
    md = render.to_markdown(minuta)
    out_path = out_dir / f"{date.today().isoformat()}_{stem}.md"
    out_path.write_text(md, encoding="utf-8")
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="video-notas",
        description="Genera una minuta y un TODO de una reunión a partir de un video.",
    )
    parser.add_argument("video", type=Path, help="Ruta al archivo de video")
    parser.add_argument(
        "-o", "--out", type=Path, default=Path("output"),
        help="Carpeta de salida (default: output/)",
    )
    parser.add_argument(
        "--keep-transcript", action="store_true",
        help="Guardar también la transcripción en texto",
    )
    args = parser.parse_args(argv)

    try:
        out_path = procesar(args.video, args.out, args.keep_transcript)
    except Exception as exc:  # noqa: BLE001 - mensaje amable en la CLI
        console.print(f"[red]Error:[/red] {exc}")
        return 1

    console.print(f"[green]Listo![/green] Minuta generada en: [bold]{out_path}[/bold]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
