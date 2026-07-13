# 🎥 video2notes

Convertí la grabación de una reunión en una **minuta** (resumen + temas +
decisiones) y una **lista de tareas (TODO)**, automáticamente y con IA.

Le pasás un archivo de video (o audio) y te devuelve un documento `.md` listo
para leer o compartir.

```
video de la reunión  ──▶  🤖 IA  ──▶  minuta.md + lista de tareas
```

---

## ✨ ¿Qué hace, paso a paso?

1. **Extrae el audio** del video (con ffmpeg).
2. **Transcribe** ese audio a texto usando la IA de OpenAI (Whisper).
3. **Genera la minuta y el TODO** con un modelo GPT.
4. **Guarda** todo en un archivo Markdown en la carpeta `output/`.

Antes de gastar, te muestra la **duración del video y el costo estimado**, y te
pide confirmación. Una reunión de 45 minutos cuesta aproximadamente **US$ 0,30**.

---

## ✅ Antes de empezar necesitás 3 cosas

| # | Qué | Para qué |
|---|-----|----------|
| 1 | **Python 3.10 o superior** | Es el lenguaje en el que está hecho |
| 2 | **ffmpeg** | Programa que saca el audio del video |
| 3 | **Una API key de OpenAI** | La "llave" para usar la IA (tiene costo por uso) |

### 1) Instalar Python

- **Windows / Mac:** descargalo de [python.org/downloads](https://www.python.org/downloads/)
  y durante la instalación en Windows tildá *"Add Python to PATH"*.
- **Linux (Ubuntu/Debian):** `sudo apt install python3 python3-venv python3-pip`

Para comprobar que quedó instalado, abrí una terminal y escribí:
```bash
python3 --version
```

### 2) Instalar ffmpeg

- **Windows:** la forma más fácil es `winget install ffmpeg` (o descargarlo de
  [ffmpeg.org](https://ffmpeg.org/download.html)).
- **Mac:** `brew install ffmpeg` (necesitás [Homebrew](https://brew.sh/)).
- **Linux (Ubuntu/Debian):** `sudo apt install ffmpeg`

Comprobá con:
```bash
ffmpeg -version
```

### 3) Conseguir la API key de OpenAI

1. Entrá a [platform.openai.com/api-keys](https://platform.openai.com/api-keys).
2. Iniciá sesión y hacé clic en **"Create new secret key"**.
3. Copiá la clave (empieza con `sk-...`). ⚠️ **Guardala, no la vas a poder volver
   a ver.** Vas a necesitar tener saldo/tarjeta cargada en tu cuenta de OpenAI.

> 🔒 Esa clave es como una contraseña con costo asociado. **Nunca la compartas ni
> la subas a internet.** Este proyecto la guarda en un archivo `.env` que está
> configurado para *nunca* subirse a GitHub.

---

## 🚀 Instalación (una sola vez)

Abrí una terminal, ubicate en la carpeta del proyecto y ejecutá:

```bash
# 1. Descargar el proyecto
git clone https://github.com/sdepietro/video2notes.git
cd video2notes

# 2. Crear un entorno aislado de Python
python3 -m venv .venv

# 3. Activarlo
#    Mac / Linux:
source .venv/bin/activate
#    Windows (PowerShell):
#    .venv\Scripts\Activate.ps1

# 4. Instalar el proyecto y sus dependencias
pip install -e .

# 5. Configurar tu API key
cp .env.example .env      # en Windows: copy .env.example .env
```

Ahora abrí el archivo `.env` con cualquier editor de texto y pegá tu clave:
```
OPENAI_API_KEY=sk-tu-clave-aca
```

¡Listo! Ya se puede usar.

---

## ▶️ Cómo usarlo

Con el entorno activado (`source .venv/bin/activate`), corré:

```bash
video-notas mi_reunion.mp4
```

Te va a mostrar algo así y te va a pedir confirmación:

```
Duración del video: 45m 28s
           Estimación (aprox.)
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Concepto      ┃ Modelo    ┃ Costo USD ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━┩
│ Transcripción │ whisper-1 │    $0.273 │
│ Minuta (LLM)  │ gpt-4o    │    $0.043 │
│ TOTAL         │           │    $0.316 │
└───────────────┴───────────┴───────────┘
¿Continuar? [S/n]:
```

Al terminar, encontrás la minuta en la carpeta `output/`.

### Opciones

| Comando | Qué hace |
|---------|----------|
| `video-notas reunion.mp4` | Procesa y pregunta antes de gastar |
| `video-notas reunion.mp4 --estimate-only` | Solo muestra el costo, no procesa |
| `video-notas reunion.mp4 -y` | Procesa sin preguntar (para automatizar) |
| `video-notas reunion.mp4 -o minutas/` | Guarda la salida en otra carpeta |
| `video-notas reunion.mp4 --keep-transcript` | Guarda también la transcripción en texto |

Acepta formatos de video y audio comunes: `.mp4`, `.mkv`, `.mov`, `.mp3`, `.wav`, etc.

---

## 💲 ¿Cuánto cuesta?

El costo lo cobra OpenAI por uso (este programa es gratis). Lo domina la
transcripción, que se cobra por minuto de audio. Valores aproximados:

| Duración de la reunión | Costo estimado |
|------------------------|----------------|
| 10 minutos | ~US$ 0,08 |
| 45 minutos | ~US$ 0,32 |
| 3 horas | ~US$ 1,20 |

Siempre vas a ver el estimado antes de confirmar.

---

## 🧩 Problemas comunes

- **`command not found: video-notas`** → activá el entorno primero:
  `source .venv/bin/activate`.
- **`ffmpeg no está instalado`** → revisá el paso 2 de requisitos.
- **`Falta OPENAI_API_KEY`** → todavía no completaste tu clave en el archivo `.env`.
- **La transcripción salió en otro idioma o con frases repetidas** → asegurate de
  tener `LANGUAGE=es` (o el idioma que corresponda) en tu `.env`. Reuniones largas
  se cortan en trozos automáticamente para evitar que la IA se "cuelgue".

---

## ⚠️ Limitaciones actuales

- Las reuniones largas se procesan cortándolas en trozos automáticamente, así que
  no hay un tope práctico de duración; solo tardan proporcionalmente más.
- La minuta **no identifica quién dijo cada cosa** (por ahora).
- La calidad de la transcripción depende de la calidad del audio; en tramos de
  silencio la IA puede colar alguna frase suelta (ej. "Subtítulos de Amara.org").

---

## 🗺️ Roadmap

El plan de evolución del proyecto está en [`roadmap.md`](roadmap.md): soporte para
reuniones largas, más robustez y una futura versión web.

---

## 📄 Licencia

MIT — libre para usar y modificar.
