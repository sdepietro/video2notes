"""CLI: video -> minuta + TODO."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

from . import audio, cost, minutes, render, transcribe
from .config import Config, load_config

console = Console()


def _fmt_hms(seconds: float) -> str:
    total = int(round(seconds))
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h}h {m:02d}m {s:02d}s" if h else f"{m}m {s:02d}s"


def mostrar_estimacion(duration: float, est: cost.CostEstimate, config: Config) -> None:
    table = Table(title="Estimación (aprox.)", show_header=True, header_style="bold")
    table.add_column("Concepto")
    table.add_column("Modelo")
    table.add_column("Costo USD", justify="right")

    stt_cost = f"${est.stt_usd:.3f}" if est.stt_known else "?"
    llm_cost = (
        f"${est.llm_in_usd + est.llm_out_usd:.3f}" if est.llm_known else "?"
    )
    table.add_row("Transcripción", config.stt_model, stt_cost)
    table.add_row("Minuta (LLM)", config.llm_model, llm_cost)
    total = f"${est.total_usd:.3f}" if (est.stt_known and est.llm_known) else "?"
    table.add_row("[bold]TOTAL[/bold]", "", f"[bold]{total}[/bold]")

    console.print(f"Duración del video: [bold]{_fmt_hms(duration)}[/bold]")
    console.print(table)
    if not (est.stt_known and est.llm_known):
        console.print(
            "[yellow]Aviso:[/yellow] no tengo precio cargado para algún modelo; "
            "revisá cost.py."
        )
    console.print("[dim]Precios aproximados; el costo real puede variar.[/dim]")


def procesar(video: Path, out_dir: Path, keep_transcript: bool) -> Path:
    config = load_config()
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = video.stem

    with console.status("[1/4] Extrayendo audio con ffmpeg..."):
        audio_path = audio.extract_audio(video, out_dir / f"{stem}.mp3")

    with console.status("[2/4] Transcribiendo audio (OpenAI)...") as status:
        def _prog(i: int, total: int) -> None:
            if total > 1:
                status.update(f"[2/4] Transcribiendo audio (trozo {i}/{total})...")
        transcript = transcribe.transcribe(audio_path, config, on_progress=_prog)
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
    parser.add_argument(
        "-y", "--yes", action="store_true",
        help="No pedir confirmación del costo estimado",
    )
    parser.add_argument(
        "--estimate-only", action="store_true",
        help="Mostrar solo la estimación de costo y salir (no procesa)",
    )
    args = parser.parse_args(argv)

    try:
        config = load_config()

        # Duración + estimación de costo ANTES de gastar nada.
        duration = audio.get_duration_seconds(args.video)
        est = cost.estimate(duration, config.stt_model, config.llm_model)
        mostrar_estimacion(duration, est, config)

        if args.estimate_only:
            return 0

        if not args.yes and not Confirm.ask("¿Continuar?", default=True):
            console.print("Cancelado.")
            return 0

        out_path = procesar(args.video, args.out, args.keep_transcript)
    except Exception as exc:  # noqa: BLE001 - mensaje amable en la CLI
        console.print(f"[red]Error:[/red] {exc}")
        return 1

    console.print(f"[green]Listo![/green] Minuta generada en: [bold]{out_path}[/bold]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
