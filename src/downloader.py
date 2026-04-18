"""Download atômico com hashing SHA-256, guardando primeiro em tmp/."""
from __future__ import annotations

import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from . import config


@dataclass
class DownloadResult:
    url: str
    content_type: str | None
    sha256_hex: str
    size_bytes: int
    local_path: Path
    status_code: int


USER_AGENT = "mcmv_search_online/0.1 (academic research; contact: researcher@example.org)"


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=config.BACKOFF_BASE_SECONDS, max=config.BACKOFF_MAX_SECONDS),
)
def _http_get(url: str, timeout: float = 60.0) -> httpx.Response:
    headers = {"User-Agent": USER_AGENT}
    with httpx.Client(follow_redirects=True, timeout=timeout, headers=headers) as client:
        response = client.get(url)
    response.raise_for_status()
    return response


def _ext_from_url_or_ct(url: str, content_type: str | None) -> str:
    path_ext = Path(urlparse(url).path).suffix.lower().lstrip(".")
    known = {"pdf", "xlsx", "xls", "csv", "doc", "docx", "html", "htm", "odt", "ods", "png", "jpg", "jpeg", "zip"}
    if path_ext in known:
        return path_ext
    if content_type:
        ct = content_type.lower().split(";", 1)[0].strip()
        mapping = {
            "application/pdf": "pdf",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
            "application/vnd.ms-excel": "xls",
            "text/csv": "csv",
            "text/html": "html",
            "application/msword": "doc",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        }
        if ct in mapping:
            return mapping[ct]
    return "bin"


def download(url: str, *, target_dir: Path, base_filename: str) -> DownloadResult:
    """Baixa uma URL para target_dir com nomenclatura {base_filename}_{hash8}.{ext}.

    Fluxo atômico: escreve em tmp/, calcula hash, renomeia.
    """
    config.TMP_DIR.mkdir(parents=True, exist_ok=True)
    target_dir.mkdir(parents=True, exist_ok=True)

    response = _http_get(url)
    content = response.content
    sha256_hex = hashlib.sha256(content).hexdigest()
    hash8 = sha256_hex[:8]
    ext = _ext_from_url_or_ct(url, response.headers.get("content-type"))

    filename = f"{base_filename}_{hash8}.{ext}"
    tmp_path = config.TMP_DIR / filename
    tmp_path.write_bytes(content)

    final_path = target_dir / filename
    shutil.move(str(tmp_path), str(final_path))

    return DownloadResult(
        url=url,
        content_type=response.headers.get("content-type"),
        sha256_hex=sha256_hex,
        size_bytes=len(content),
        local_path=final_path,
        status_code=response.status_code,
    )
