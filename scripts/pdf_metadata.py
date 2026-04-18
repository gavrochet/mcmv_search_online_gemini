"""Extrai metadata de PDFs (Producer, Creator, Title, /URL) para ajudar a inferir fonte.

Uso: python scripts/pdf_metadata.py <arquivo.pdf> [<arquivo2.pdf> ...]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from pypdf import PdfReader


def extract(path: Path) -> dict:
    out = {"path": str(path), "size_bytes": path.stat().st_size}
    try:
        reader = PdfReader(str(path))
        out["n_pages"] = len(reader.pages)
        meta = reader.metadata or {}
        out["metadata"] = {k.lstrip("/"): str(v) for k, v in dict(meta).items()}
        # First page text snippet (useful for identifying source)
        try:
            first = reader.pages[0].extract_text() or ""
            out["first_page_snippet"] = first[:800]
        except Exception as e:
            out["first_page_error"] = str(e)
        # /URI annotations anywhere
        urls: list[str] = []
        for page in reader.pages[:3]:
            if "/Annots" in page:
                for annot in page["/Annots"]:
                    try:
                        obj = annot.get_object()
                        a = obj.get("/A")
                        if a and "/URI" in a:
                            urls.append(str(a["/URI"]))
                    except Exception:
                        pass
        out["urls_in_annotations"] = urls[:20]
    except Exception as e:
        out["error"] = str(e)
    return out


def main(argv: list[str]) -> int:
    if not argv:
        print("uso: python scripts/pdf_metadata.py <arquivo.pdf> [<arquivo2.pdf> ...]", file=sys.stderr)
        return 1
    results = [extract(Path(p)) for p in argv]
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
