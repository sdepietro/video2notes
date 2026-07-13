# Video → Minuta + TODO con IA

Herramienta que toma un archivo de video de una reunión y genera automáticamente
una **minuta** estructurada y una **lista de tareas (TODO)** usando IA.

## Decisiones tomadas

- **Lenguaje:** Python
- **Transcripción (STT):** API en la nube (no local)
- **Interfaz:** CLI primero → Web app después
- **LLM para minuta/TODO:** Claude (Anthropic)

---

## Arquitectura / Pipeline

```
video.mp4
   │
   ▼  [1] ffmpeg: extraer y comprimir audio
audio.mp3 / audio.m4a
   │
   ▼  [2] API STT (nube): audio → texto
transcript.txt  (idealmente con timestamps y speakers)
   │
   ▼  [3] Claude: texto → minuta + TODO (salida JSON estructurada)
{ resumen, decisiones, temas, tareas[...] }
   │
   ▼  [4] Render
reunion_2026-07-13.md  (+ opcional .pdf)
```

### Componentes y tecnología sugerida

| Paso | Qué hace | Tecnología |
|------|----------|------------|
| 1. Audio | Extrae audio del video, lo comprime (mono, 16kHz) | `ffmpeg` (CLI, vía `subprocess`) |
| 2. STT | Transcribe audio a texto | OpenAI `gpt-4o-transcribe` / `whisper-1`, o Deepgram / AssemblyAI |
| 3. IA | Genera minuta + TODO | Claude (`claude-sonnet-4-6`) vía SDK `anthropic` |
| 4. Salida | Formatea a Markdown | Jinja2 / f-strings; PDF opcional con `weasyprint` |

> **Nota clave sobre STT:** las APIs suelen tener límite de tamaño de archivo
> (p.ej. OpenAI ~25 MB). Por eso el paso 1 comprime el audio, y para reuniones
> largas hay que **partir el audio en trozos** (chunking) y unir las
> transcripciones. Eso está contemplado en la Fase 2.

---

## Estructura del proyecto (propuesta)

```
video_notas/
├── roadmap.md
├── README.md
├── requirements.txt
├── .env.example              # claves de API (no se commitea el .env real)
├── .gitignore
├── src/
│   └── video_notas/
│       ├── __init__.py
│       ├── cli.py            # punto de entrada de la CLI
│       ├── audio.py          # paso 1: extracción/compresión con ffmpeg
│       ├── transcribe.py     # paso 2: cliente STT + chunking
│       ├── minutes.py        # paso 3: prompt + llamada a Claude
│       ├── render.py         # paso 4: transcript → Markdown/PDF
│       └── config.py         # carga de claves y settings
├── prompts/
│   └── minuta.md             # prompt del sistema (editable sin tocar código)
├── output/                   # minutas generadas (gitignored)
└── tests/
```

---

## Roadmap por fases

### Fase 0 — Setup del proyecto
- [ ] Crear estructura de carpetas y `requirements.txt`
- [ ] `.gitignore`, `.env.example` y carga de config (`python-dotenv`)
- [ ] `git init` + primer commit
- [ ] Verificar que `ffmpeg` esté instalado en el sistema
- [ ] Conseguir las API keys (STT + Anthropic) y ponerlas en `.env`

### Fase 1 — MVP end-to-end (CLI, camino feliz)
- [ ] `audio.py`: extraer audio de un video corto con ffmpeg
- [ ] `transcribe.py`: transcribir un audio que **entre en el límite** de la API
- [ ] `minutes.py`: prompt + llamada a Claude → devuelve JSON con minuta y TODO
- [ ] `render.py`: volcar el resultado a un `.md` legible
- [ ] `cli.py`: `video-notas procesar video.mp4 -o output/`
- [ ] Probar con un video real de ~5 min

### Fase 2 — Robustez (reuniones reales)
- [ ] **Chunking** de audio: partir archivos largos y unir transcripciones
- [ ] Manejo de errores y reintentos (API caída, rate limits, timeouts)
- [ ] Barra de progreso (`rich`) — transcribir tarda
- [ ] Soportar varios formatos de entrada (mp4, mkv, mov, mp3, wav...)
- [ ] Cache: no re-transcribir si ya existe el transcript
- [ ] (Opcional) **Diarización**: identificar quién habla (Deepgram/AssemblyAI lo dan)

### Fase 3 — Calidad de la minuta
- [ ] Afinar el prompt: secciones (resumen, decisiones, temas, próximos pasos)
- [ ] TODO con responsable y fecha cuando se detecten en el audio
- [ ] Detección de idioma / salida en español
- [ ] Export a PDF
- [ ] (Opcional) Reducir costo: resumir con `claude-haiku-4-5` primero si es muy largo

### Fase 4 — Web app
- [ ] Backend con FastAPI reutilizando `src/video_notas`
- [ ] Subida de archivo + estado del procesamiento (async / cola)
- [ ] Frontend simple para subir video y ver/descargar la minuta
- [ ] (Opcional) Historial de reuniones procesadas

---

## Decisiones abiertas (a definir en el camino)

- **Proveedor de STT concreto:** OpenAI es lo más simple (un solo vendor con
  Anthropic aparte); Deepgram/AssemblyAI dan **diarización** (quién habla), que
  mejora mucho la minuta. → *Decidir en Fase 1.*
- **Costo esperado:** STT se cobra por minuto de audio; el LLM por tokens.
  Estimar con un video real antes de la Fase 2.
- **Privacidad:** con API en la nube, el audio sale de tu máquina. Si en algún
  momento importa, dejar la puerta a Whisper local como plugin de `transcribe.py`.
