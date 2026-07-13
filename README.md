# video-notas

Toma un archivo de video de una reunión y genera con IA una **minuta** y una
**lista de tareas (TODO)** en Markdown.

Pipeline: `ffmpeg` extrae el audio → OpenAI lo transcribe → un modelo GPT arma la
minuta → se renderiza a Markdown. Ver [`roadmap.md`](roadmap.md) para el plan.

## Requisitos

- Python 3.10+
- [`ffmpeg`](https://ffmpeg.org/) instalado en el sistema
- Una API key de OpenAI

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

cp .env.example .env   # y completá OPENAI_API_KEY en .env
```

## Uso

```bash
video-notas reunion.mp4                 # genera output/AAAA-MM-DD_reunion.md
video-notas reunion.mp4 -o minutas/     # elegir carpeta de salida
video-notas reunion.mp4 --keep-transcript
```

## Estado

- **Fase 1 (MVP):** funcional para videos cuyo audio comprimido entre en ~25 MB.
- **Fase 2 (pendiente):** chunking para reuniones largas, reintentos, más formatos.

## Limitaciones actuales

- Reuniones largas: la API de OpenAI limita el archivo a ~25 MB. El chunking está
  planificado en la Fase 2 del roadmap.
- La minuta no identifica quién habló (se puede inferir del texto).
