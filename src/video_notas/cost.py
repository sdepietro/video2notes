"""Estimación de costo antes de procesar (transcripción + minuta).

⚠️ Los precios son APROXIMADOS y pueden cambiar. Revisá la lista oficial en
https://openai.com/api/pricing/ y ajustá las constantes de abajo.
La estimación asume una densidad de habla típica; el costo real puede variar.
"""

from __future__ import annotations

from dataclasses import dataclass

# --- Precios (USD). Editables. ---------------------------------------------

# Transcripción (STT): costo por minuto de audio.
STT_USD_PER_MINUTE = {
    "whisper-1": 0.006,
    "gpt-4o-transcribe": 0.006,        # aprox; el real es por tokens de audio
    "gpt-4o-mini-transcribe": 0.003,
}

# LLM para la minuta: USD por 1M de tokens (entrada / salida).
LLM_USD_PER_1M = {
    "gpt-4o": {"in": 2.50, "out": 10.00},
    "gpt-4o-mini": {"in": 0.15, "out": 0.60},
}

# --- Supuestos de estimación ------------------------------------------------

# Habla ~150 palabras/min; ~1.4 tokens por palabra en español.
TOKENS_PER_MINUTE = 150 * 1.4
# La minuta de salida es acotada; escala un poco con la duración.
OUTPUT_TOKENS_BASE = 800
OUTPUT_TOKENS_PER_MINUTE = 25
OUTPUT_TOKENS_MAX = 6000


@dataclass
class CostEstimate:
    minutes: float
    stt_usd: float
    llm_in_usd: float
    llm_out_usd: float
    stt_known: bool
    llm_known: bool

    @property
    def total_usd(self) -> float:
        return self.stt_usd + self.llm_in_usd + self.llm_out_usd


def estimate(duration_seconds: float, stt_model: str, llm_model: str) -> CostEstimate:
    minutes = duration_seconds / 60.0

    stt_rate = STT_USD_PER_MINUTE.get(stt_model)
    stt_known = stt_rate is not None
    stt_usd = minutes * (stt_rate or 0.0)

    llm_rates = LLM_USD_PER_1M.get(llm_model)
    llm_known = llm_rates is not None
    in_tokens = minutes * TOKENS_PER_MINUTE
    out_tokens = min(
        OUTPUT_TOKENS_MAX, OUTPUT_TOKENS_BASE + minutes * OUTPUT_TOKENS_PER_MINUTE
    )
    llm_in_usd = in_tokens / 1_000_000 * (llm_rates["in"] if llm_rates else 0.0)
    llm_out_usd = out_tokens / 1_000_000 * (llm_rates["out"] if llm_rates else 0.0)

    return CostEstimate(
        minutes=minutes,
        stt_usd=stt_usd,
        llm_in_usd=llm_in_usd,
        llm_out_usd=llm_out_usd,
        stt_known=stt_known,
        llm_known=llm_known,
    )
