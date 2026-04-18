"""Gera variantes de query de busca para uma cidade.

Cobre as listas da §5.2 (termos gerais) e as combinações sugeridas da §5.5.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product


PROGRAMA_TERMOS = (
    '"minha casa minha vida"',
    '"MCMV"',
    '"PMCMV"',
    '"Programa Minha Casa Minha Vida"',
    '"habitação de interesse social" "sorteio"',
    '"Faixa 1"',
    '"Faixa I"',
)

DOCUMENTO_TERMOS = (
    '"edital"',
    '"edital de convocação"',
    '"edital de chamamento público"',
    '"edital de seleção"',
    '"ata de sorteio"',
    '"resultado do sorteio"',
    '"lista de sorteados"',
    '"lista de contemplados"',
    '"lista de beneficiários"',
    '"lista de habilitados"',
    '"lista de classificados"',
    '"relação de sorteados"',
    '"relação de inscritos"',
    '"homologação do sorteio"',
    '"cadastro reserva"',
    '"lista de suplentes"',
    '"lista de espera"',
)

PROCESSO_TERMOS = (
    '"sorteio público"',
    '"sorteio eletrônico"',
    '"seleção pública"',
    '"audiência pública de sorteio"',
    '"demanda aberta"',
    '"demanda fechada"',
)

ATORES = (
    "COHAB",
    "SEHAB",
    "SMH",
    '"Secretaria de Habitação"',
    '"Caixa Econômica Federal"',
    "CEF",
    '"fundação habitacional"',
    '"companhia habitacional"',
)

FILETYPE_HINTS = ("filetype:pdf", "filetype:xlsx", "filetype:xls", "")


@dataclass(frozen=True)
class CityTarget:
    municipio: str
    uf: str


def general_queries(city: CityTarget, limit: int | None = 40) -> list[str]:
    cidade_quoted = f'"{city.municipio}"'
    cidade_uf = f'"{city.municipio} {city.uf}"' if city.uf else cidade_quoted

    base_pairs = [
        # padrão mais específico — MCMV + tipo de documento + cidade + UF
        (prog, doc, cidade_uf)
        for prog in PROGRAMA_TERMOS
        for doc in DOCUMENTO_TERMOS[:8]  # top tipos de documento
    ]
    queries: list[str] = []
    for prog, doc, city_q in base_pairs:
        queries.append(f"{prog} {doc} {city_q}")
        queries.append(f"{prog} {doc} {city_q} filetype:pdf")

    # site: gov.br — priorizar documentos oficiais
    for prog in PROGRAMA_TERMOS[:3]:
        for doc in ('"lista de sorteados"', '"lista de contemplados"', '"ata de sorteio"', '"edital"'):
            queries.append(f"site:gov.br {prog} {doc} {city.municipio}")

    # wayback
    if city.uf:
        queries.append(f'site:web.archive.org "minha casa minha vida" "{city.municipio}" "sorteio"')

    # portal do diário oficial
    queries.append(f'"diário oficial" "{city.municipio}" "minha casa minha vida" "sorteio"')

    # processo
    for proc in PROCESSO_TERMOS[:3]:
        queries.append(f'"minha casa minha vida" {proc} "{city.municipio}" filetype:pdf')

    # dedup preservando ordem
    seen = set()
    out: list[str] = []
    for q in queries:
        if q not in seen:
            seen.add(q)
            out.append(q)
    return out[:limit] if limit else out


def reverse_cpf_queries(cpf_masked: str) -> list[str]:
    """Queries dirigidas a um CPF no formato XXX.XXX.XXX-XX."""
    return [
        f'"{cpf_masked}" "minha casa minha vida"',
        f'"{cpf_masked}" site:gov.br',
        f'"{cpf_masked}" "sorteado" OR "contemplado" OR "habilitado"',
    ]


def reverse_nis_queries(nis: str) -> list[str]:
    return [
        f'"{nis}" "minha casa minha vida"',
        f'"{nis}" "MCMV" OR "habitação"',
        f'"{nis}" site:gov.br',
    ]


def reverse_name_queries(nome: str) -> list[str]:
    return [
        f'"{nome}" "sorteado" OR "contemplado"',
        f'"{nome}" "minha casa minha vida"',
    ]


def empreendimento_queries(nome_empreendimento: str, municipio: str) -> list[str]:
    e = f'"{nome_empreendimento}"'
    c = f'"{municipio}"'
    return [
        f'{e} "sorteados" OR "contemplados" {c}',
        f'{e} "edital" "minha casa minha vida"',
        f'{e} "ata de sorteio"',
        f'{e} filetype:pdf',
    ]
