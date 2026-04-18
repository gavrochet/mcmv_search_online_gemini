"""Orquestrador do agente.

NOTA sobre o motor de busca: este projeto é executado sob o agente Claude Code,
que tem acesso à ferramenta WebSearch do host. A estratégia é:

1. Este orquestrador imprime/emite as queries e os identificadores da amostra;
2. O agente (Claude) executa as queries via WebSearch, inspeciona cada resultado
   via WebFetch, e chama `downloader.download()` para o que for promissor;
3. Os registros são gravados no `catalog/` via `catalog.append_record()`.

Para uso puramente programático (sem Claude), implemente um `SearchEngine`
concreto em `search_engine.py`.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import config, ref_data
from .queries import CityTarget, general_queries
from .reverse_search import build_sample_for_city


def plan_city(municipio: str, uf: str, sample_size: int = 50) -> dict:
    """Monta um plano de busca para uma cidade: queries + amostra reversa."""
    takeup = ref_data.load_takeup()
    sample = build_sample_for_city(takeup, municipio=municipio, uf=uf, sample_size=sample_size)
    queries = general_queries(CityTarget(municipio=municipio, uf=uf))
    return {
        "municipio": municipio,
        "uf": uf,
        "universo_cidade_tamanho": sample.universo_cidade_tamanho,
        "amostra_tamanho": len(sample.cpfs_masked),
        "general_queries": queries,
        "reverse_identifiers": {
            "n_cpfs_masked": len(sample.cpfs_masked),
            "n_cpfs_unmasked": len(sample.cpfs_unmasked),
            "n_nis": len(sample.nis_values),
            "n_nomes": len(sample.nomes),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Orquestrador do agente MCMV search")
    parser.add_argument("--rodada", type=int, choices=(1, 2), default=1)
    parser.add_argument("--limit-cities", type=int, default=None,
                        help="Processar apenas as top-N cidades da rodada.")
    parser.add_argument("--city", type=str, default=None,
                        help="Processar apenas uma cidade específica (formato 'Cidade,UF').")
    parser.add_argument("--plan-only", action="store_true",
                        help="Emite o plano (queries + contagens) em JSON e sai.")
    args = parser.parse_args(argv)

    if args.city:
        municipio, uf = [p.strip() for p in args.city.split(",", 1)]
        plan = plan_city(municipio, uf)
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0

    if args.rodada == 1:
        df = ref_data.cities_in_takeup()
    else:
        takeup_cities = set(ref_data.cities_in_takeup().iloc[:, 0].str.upper())
        df = ref_data.cities_in_dados_abertos()
        mask = ~df.iloc[:, 0].str.upper().isin(takeup_cities)
        df = df[mask].reset_index(drop=True)

    if args.limit_cities:
        df = df.head(args.limit_cities)

    print(json.dumps({"rodada": args.rodada, "n_cidades": len(df), "head": df.head(10).to_dict("records")},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
