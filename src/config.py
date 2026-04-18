"""Caminhos, constantes e convenções de nomenclatura."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REFERENCE_DIR = ROOT / "reference_data"
DATA_TRAIN_DIR = ROOT / "data_train"
DOWNLOADS_DIR = ROOT / "downloads"
CATALOG_DIR = ROOT / "catalog"
TMP_DIR = ROOT / "tmp"

REFERENCE_DADOS_ABERTOS = REFERENCE_DIR / "dados_abertos_filtrado.csv"
REFERENCE_TAKEUP = REFERENCE_DIR / "takeup_far_dec17.xlsx"

CATALOG_JSONL = CATALOG_DIR / "catalog.jsonl"
SEARCH_LOG_JSONL = CATALOG_DIR / "search_log.jsonl"
CATALOG_REPORT_MD = CATALOG_DIR / "catalog_report.md"
COVERAGE_GAPS_MD = CATALOG_DIR / "coverage_gaps.md"

TIPO_LISTA = (
    "inscritos",
    "sorteados",
    "suplentes",
    "cadastro_reserva",
    "ata",
    "misto",
)

FAIXA_VALUES = (
    "Faixa 1",
    "Faixa 1 (inferida)",
    "mista_com_faixa_1",
    "nao_especificado",
)

CONFIANCA_VALUES = ("alta", "media", "baixa")

# Rate limiting (§12)
REQUESTS_PER_SECOND_PER_HOST = 1.5
BACKOFF_BASE_SECONDS = 2.0
BACKOFF_MAX_SECONDS = 60.0

# Limiar de retenção da busca reversa (§5.3 — "mais de 10 matches")
REVERSE_SEARCH_MATCH_THRESHOLD = 10

# Amostra da busca reversa
REVERSE_SEARCH_SAMPLE_MIN = 50
REVERSE_SEARCH_SAMPLE_MAX = 100

# Período de interesse
PERIODO_ANO_MIN = 2009
PERIODO_ANO_MAX = 2020
