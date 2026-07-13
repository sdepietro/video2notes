"""Paso 4: renderizar la minuta estructurada a Markdown."""

from __future__ import annotations


def to_markdown(minuta: dict) -> str:
    """Convierte el dict de la minuta en un documento Markdown."""
    lines: list[str] = []

    titulo = minuta.get("titulo") or "Minuta de reunión"
    lines.append(f"# {titulo}\n")

    resumen = minuta.get("resumen")
    if resumen:
        lines.append("## Resumen\n")
        lines.append(f"{resumen}\n")

    temas = minuta.get("temas") or []
    if temas:
        lines.append("## Temas tratados\n")
        for t in temas:
            lines.append(f"### {t.get('tema', 'Tema')}\n")
            for punto in t.get("puntos", []):
                lines.append(f"- {punto}")
            lines.append("")

    decisiones = minuta.get("decisiones") or []
    if decisiones:
        lines.append("## Decisiones\n")
        for d in decisiones:
            lines.append(f"- {d}")
        lines.append("")

    tareas = minuta.get("tareas") or []
    lines.append("## TODO / Tareas\n")
    if tareas:
        for tarea in tareas:
            desc = tarea.get("descripcion", "")
            resp = tarea.get("responsable")
            fecha = tarea.get("fecha_limite")
            extra = []
            if resp:
                extra.append(f"**{resp}**")
            if fecha:
                extra.append(f"_{fecha}_")
            suffix = f" ({' · '.join(extra)})" if extra else ""
            lines.append(f"- [ ] {desc}{suffix}")
    else:
        lines.append("_No se detectaron tareas._")
    lines.append("")

    return "\n".join(lines)
