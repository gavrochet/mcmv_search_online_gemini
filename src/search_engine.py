"""Interface abstrata para motor de busca web.

Implementações concretas podem delegar para (a) ferramenta WebSearch da plataforma,
(b) APIs como Serper/Bing, ou (c) scraping direto. Aqui definimos o contrato.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence


@dataclass(frozen=True)
class SearchHit:
    title: str
    url: str
    snippet: str
    rank: int


class SearchEngine(Protocol):
    def search(self, query: str, *, limit: int = 10) -> Sequence[SearchHit]: ...


class NullSearchEngine:
    """Stub que não faz nada — útil para testes unitários.

    Em produção, a busca real é conduzida pelo agente Claude via WebSearch
    (ver src/main.py docstring).
    """

    def search(self, query: str, *, limit: int = 10) -> Sequence[SearchHit]:  # pragma: no cover
        return []
