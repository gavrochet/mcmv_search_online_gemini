"""Resumo COMPACTO de data_train/ — uma linha por cidade com totais e padrões."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_TRAIN = ROOT / "data_train"

TIPO_PATTERNS = [
    (re.compile(r"inscrit", re.I), "inscritos"),
    (re.compile(r"sorte|contempl", re.I), "sorteados"),
    (re.compile(r"suplen", re.I), "suplentes"),
    (re.compile(r"reserva", re.I), "cadastro_reserva"),
    (re.compile(r"\bata\b", re.I), "ata"),
    (re.compile(r"edital", re.I), "edital"),
]

YEAR_RE = re.compile(r"(?:19|20)\d{2}")
SKIP_DIRS = {"Output", "extracted_texts", "og", "not_used", "Old", "old", "all_files", "diario_oficial"}


def classify(name: str) -> list[str]:
    return [t for pat, t in TIPO_PATTERNS if pat.search(name)] or ["?"]


def main() -> int:
    result = {}
    for city_dir in sorted(DATA_TRAIN.iterdir()):
        if not city_dir.is_dir():
            continue
        files = [p for p in city_dir.rglob("*")
                 if p.is_file() and p.suffix.lower() in {".pdf", ".xlsx", ".xls", ".csv", ".doc", ".docx", ".html"}]
        # Exclude files living inside intermediate folders (output/extracted/og)
        primary = [p for p in files if not any(part in SKIP_DIRS for part in p.relative_to(city_dir).parts[:-1])]
        ext_counts = Counter(p.suffix.lower().lstrip(".") for p in primary)
        tipo_counts = Counter()
        year_counts = Counter()
        for p in primary:
            for t in classify(p.name):
                tipo_counts[t] += 1
            # Year from path or filename
            for part in reversed(p.relative_to(city_dir).parts):
                m = YEAR_RE.search(part)
                if m:
                    year_counts[m.group(0)] += 1
                    break
        sample = sorted({p.name for p in primary})[:8]
        result[city_dir.name] = {
            "total_primary": len(primary),
            "total_including_intermediate": len(files),
            "por_extensao": dict(ext_counts),
            "por_tipo": dict(tipo_counts),
            "por_ano": dict(sorted(year_counts.items())),
            "amostra_nomes": sample,
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
