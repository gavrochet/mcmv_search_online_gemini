"""Inspeciona data_train/ e imprime um resumo dos arquivos manualmente coletados.

Uso:
    python scripts/analyze_data_train.py

Output: por cidade, lista de documentos + tipo inferido (inscritos/sorteados/...)
+ ano, para servir de ground-truth na fase de treino.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_TRAIN = ROOT / "data_train"

TIPO_PATTERNS = [
    (re.compile(r"inscrit", re.I), "inscritos"),
    (re.compile(r"sorte|contempl", re.I), "sorteados"),
    (re.compile(r"suplen", re.I), "suplentes"),
    (re.compile(r"reserva", re.I), "cadastro_reserva"),
    (re.compile(r"\bata\b|resultad", re.I), "ata"),
    (re.compile(r"edital", re.I), "edital"),
]

YEAR_RE = re.compile(r"(?:19|20)\d{2}")


def infer_tipo(name: str) -> list[str]:
    tipos = []
    for pat, t in TIPO_PATTERNS:
        if pat.search(name):
            tipos.append(t)
    return tipos or ["desconhecido"]


def infer_year_from_path(path: Path) -> str | None:
    for part in reversed(path.parts):
        m = YEAR_RE.search(part)
        if m:
            return m.group(0)
    return None


def main() -> int:
    by_city: dict[str, list[dict]] = defaultdict(list)
    for p in DATA_TRAIN.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in {".pdf", ".xlsx", ".xls", ".csv", ".doc", ".docx", ".html", ".htm"}:
            continue
        # Ignora reexportações intermediárias
        rel = p.relative_to(DATA_TRAIN)
        parts = rel.parts
        if not parts:
            continue
        city_folder = parts[0]
        entry = {
            "arquivo": str(rel).replace("\\", "/"),
            "tamanho_bytes": p.stat().st_size,
            "extensao": p.suffix.lower().lstrip("."),
            "tipo_inferido": infer_tipo(p.name),
            "ano_inferido": infer_year_from_path(p),
        }
        by_city[city_folder].append(entry)

    summary = {}
    for city, items in sorted(by_city.items()):
        summary[city] = {
            "n_arquivos": len(items),
            "por_extensao": _count_by_key(items, "extensao"),
            "por_tipo": _count_nested(items, "tipo_inferido"),
            "por_ano": _count_by_key(items, "ano_inferido"),
            "arquivos": items,
        }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def _count_by_key(items: list[dict], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for it in items:
        v = it.get(key) or "?"
        counts[v] = counts.get(v, 0) + 1
    return dict(sorted(counts.items()))


def _count_nested(items: list[dict], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for it in items:
        for v in it.get(key, []):
            counts[v] = counts.get(v, 0) + 1
    return dict(sorted(counts.items()))


if __name__ == "__main__":
    raise SystemExit(main())
