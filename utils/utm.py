# utils/utm.py
from __future__ import annotations

import re
from typing import Any, Dict, Optional
from urllib.parse import urlencode, urljoin

__all__ = ["slugify", "build_final_url"]

def slugify(text: Optional[str]) -> str:
    s = (text or "").lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")

def build_final_url(base: Any, path: Optional[str], utm: Dict[str, str]) -> str:
    """
    Construye una URL final con UTMs.
    - Acepta base como str o HttpUrl (Pydantic v2) -> se castea a str.
    - path puede venir con o sin '/' inicial.
    - Sólo incluye UTMs con valor truthy.
    """
    base_str = (str(base).rstrip("/") if base else "https://example.com")
    if path:
        base_str = urljoin(base_str + "/", str(path).lstrip("/"))
    qs = urlencode({k: v for k, v in (utm or {}).items() if v})
    return f"{base_str}?{qs}" if qs else base_str
