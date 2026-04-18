"""Amostragem de identificadores do takeup para busca reversa (§5.3).

O download e a contagem de matches são feitos pelo orquestrador; este módulo
só prepara a amostra e fornece utilitários para contar matches em um texto.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

import pandas as pd

from . import config


CPF_RE = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")
CPF_NO_MASK_RE = re.compile(r"\b\d{11}\b")
NIS_RE = re.compile(r"\b\d{11}\b")  # NIS colide em formato com CPF sem máscara


@dataclass
class ReverseSample:
    cpfs_masked: list[str]
    cpfs_unmasked: list[str]
    nis_values: list[str]
    nomes: list[str]
    universo_cidade_tamanho: int


def build_sample_for_city(
    takeup: pd.DataFrame,
    *,
    municipio: str,
    uf: str | None = None,
    sample_size: int = config.REVERSE_SEARCH_SAMPLE_MIN,
    seed: int = 42,
) -> ReverseSample:
    city_col = _first_col(takeup, ["Cidade", "Município", "Municipio", "Nome_Municipio"])
    uf_col = _first_col(takeup, ["UF", "Estado", "Sigla_UF"], required=False)
    mask = takeup[city_col].astype(str).str.strip().str.upper() == municipio.upper()
    if uf and uf_col:
        mask &= takeup[uf_col].astype(str).str.strip().str.upper() == uf.upper()
    df = takeup.loc[mask]
    universo = len(df)
    if universo == 0:
        return ReverseSample([], [], [], [], 0)

    n = min(sample_size, universo)
    sample = df.sample(n=n, random_state=seed)

    cpf_col = _first_col(sample, ["CPF", "Cpf", "Numero_CPF_Mutuario"], required=False)
    nis_col = _first_col(sample, ["NIS", "Nis", "PIS", "Numero_PIS_do_Mutuario"], required=False)
    nome_col = _first_col(sample, ["Nome", "Nome_Completo", "Nome Completo", "Nome_do_Mutuario"], required=False)

    cpfs_masked: list[str] = []
    cpfs_unmasked: list[str] = []
    if cpf_col:
        for v in sample[cpf_col].dropna().astype(str):
            digits = re.sub(r"\D", "", v)
            if len(digits) == 11:
                cpfs_unmasked.append(digits)
                cpfs_masked.append(f"{digits[0:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:11]}")

    nis_values: list[str] = []
    if nis_col:
        for v in sample[nis_col].dropna().astype(str):
            digits = re.sub(r"\D", "", v)
            if len(digits) == 11:
                nis_values.append(digits)

    nomes: list[str] = []
    if nome_col:
        nomes = sorted({str(n).strip() for n in sample[nome_col].dropna() if str(n).strip()})

    return ReverseSample(
        cpfs_masked=cpfs_masked,
        cpfs_unmasked=cpfs_unmasked,
        nis_values=nis_values,
        nomes=nomes,
        universo_cidade_tamanho=universo,
    )


def count_matches_in_text(
    text: str,
    *,
    cpfs_masked: Iterable[str] = (),
    cpfs_unmasked: Iterable[str] = (),
    nis_values: Iterable[str] = (),
    nomes: Iterable[str] = (),
) -> int:
    """Conta identificadores da amostra que aparecem em `text`."""
    hits = 0
    for c in cpfs_masked:
        if c in text:
            hits += 1
    for c in cpfs_unmasked:
        if c in text:
            hits += 1
    for n in nis_values:
        if n in text:
            hits += 1
    for nome in nomes:
        if nome.upper() in text.upper():
            hits += 1
    return hits


def _first_col(df: pd.DataFrame, candidates: list[str], required: bool = True) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    if required:
        raise KeyError(f"Nenhuma coluna de {candidates} em {list(df.columns)}")
    return None
