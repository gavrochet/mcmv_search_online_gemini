"""Escrita e leitura do catálogo JSONL, seguindo o schema da §7."""
from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from . import config


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class TakeupMatches:
    amostra_usada_tamanho: int = 0
    amostra_matches: int = 0
    universo_cidade_tamanho: int = 0
    universo_matches: int = 0


@dataclass
class CatalogRecord:
    doc_id: str
    url_primaria: str
    urls_alternativas: list[str]
    url_host: str
    fonte_tipo: str
    via_busca_reversa: bool
    caminho_local: str
    hash_sha256: str
    tamanho_bytes: int
    municipio: str
    uf: str
    ano_publicacao: str | None
    ano_sorteio: str | None
    numero_edital: str | None
    empreendimentos_citados: list[str]
    empreendimentos_match_dados_abertos: list[str]
    faixa_renda: str
    tipo_lista: list[str]
    identificadores_presentes: list[str]
    numero_aproximado_de_linhas: int | None
    formato: str
    takeup_matches: TakeupMatches
    confianca: str
    motivo_confianca: str
    observacoes: str
    documentos_relacionados: list[str] = field(default_factory=list)
    data_acesso: str = field(default_factory=_now_iso)
    data_catalogacao: str = field(default_factory=_now_iso)

    @staticmethod
    def new_id() -> str:
        return str(uuid.uuid4())


def append_record(record: CatalogRecord, *, catalog_path: Path = config.CATALOG_JSONL) -> None:
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    with catalog_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")


def load_all(catalog_path: Path = config.CATALOG_JSONL) -> list[dict]:
    if not catalog_path.exists():
        return []
    records = []
    with catalog_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def find_by_hash(sha256_hex: str, catalog_path: Path = config.CATALOG_JSONL) -> dict | None:
    for rec in load_all(catalog_path):
        if rec.get("hash_sha256") == sha256_hex:
            return rec
    return None


def log_search(entry: dict, *, log_path: Path = config.SEARCH_LOG_JSONL) -> None:
    """Grava uma entrada de search_log.jsonl. Caller deve redigir PII (ver §5.3/§12)."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def redact_identifier(identifier: str) -> str:
    """Hash truncado (16 chars) para uso em search_log.jsonl (§12)."""
    return hashlib.sha256(identifier.encode("utf-8")).hexdigest()[:16]
