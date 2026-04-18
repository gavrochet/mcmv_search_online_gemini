"""Carrega e normaliza os dados de referência do pesquisador."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import pandas as pd
from slugify import slugify

from . import config


@dataclass(frozen=True)
class CityKey:
    municipio: str
    uf: str

    @property
    def slug(self) -> str:
        return slugify(self.municipio, separator="_", lowercase=True)

    @property
    def folder_name(self) -> str:
        return f"{self.uf}_{self.slug}"


@lru_cache(maxsize=1)
def load_dados_abertos() -> pd.DataFrame:
    """Empreendimentos MCMV Faixa 1 por cidade + data de aprovação."""
    df = pd.read_csv(config.REFERENCE_DADOS_ABERTOS)
    df.columns = [c.strip() for c in df.columns]
    return df


@lru_cache(maxsize=1)
def load_takeup() -> pd.DataFrame:
    """Contratos assinados até dez/2017 — Nome, NIS, CPF, Cidade, Empreendimento."""
    df = pd.read_excel(config.REFERENCE_TAKEUP)
    df.columns = [c.strip() for c in df.columns]
    return df


def cities_in_takeup() -> pd.DataFrame:
    """Cidades em takeup, ordenadas por contagem de contratos (desc)."""
    df = load_takeup()
    city_col = _first_matching_column(df, ["Cidade", "Município", "Municipio"])
    uf_col = _first_matching_column(df, ["UF", "Estado", "Sigla_UF"], required=False)
    group_cols = [city_col] + ([uf_col] if uf_col else [])
    counts = df.groupby(group_cols).size().reset_index(name="n_contratos")
    return counts.sort_values("n_contratos", ascending=False).reset_index(drop=True)


def cities_in_dados_abertos() -> pd.DataFrame:
    """Cidades em dados_abertos, ordenadas por contagem de empreendimentos (desc)."""
    df = load_dados_abertos()
    city_col = _first_matching_column(df, ["Cidade", "Município", "Municipio"])
    uf_col = _first_matching_column(df, ["UF", "Estado", "Sigla_UF"], required=False)
    group_cols = [city_col] + ([uf_col] if uf_col else [])
    counts = df.groupby(group_cols).size().reset_index(name="n_empreendimentos")
    return counts.sort_values("n_empreendimentos", ascending=False).reset_index(drop=True)


def _first_matching_column(df: pd.DataFrame, candidates: list[str], required: bool = True) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    if required:
        raise KeyError(f"Nenhuma coluna de {candidates} encontrada em {list(df.columns)}")
    return None
