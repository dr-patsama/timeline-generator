#!/usr/bin/env python3
"""Remove Google Fonts preconnect + stylesheet links from EN site HTML files.

The EN site now self-hosts the Cloud font (Typomancer) via @font-face in
assets/css/style.css, so the Google Fonts CSS is no longer needed.

Idempotent: safe to re-run.
"""
from __future__ import annotations
import re
from pathlib import Path

DST = Path("/Users/DrPatsama/Documents/LIFEbydrpat WEBSITE EN")

# Match the 3 lines: 2 preconnects + the css2 stylesheet link (any css2 url).
RE_PRECONNECT_GOOGLE = re.compile(
    r'<link\s+rel="preconnect"\s+href="https://fonts\.googleapis\.com"[^>]*>\s*\n?',
    re.IGNORECASE,
)
RE_PRECONNECT_GSTATIC = re.compile(
    r'<link\s+rel="preconnect"\s+href="https://fonts\.gstatic\.com"[^>]*>\s*\n?',
    re.IGNORECASE,
)
RE_GOOGLE_FONTS_CSS = re.compile(
    r'<link\s+href="https://fonts\.googleapis\.com/css2\?[^"]*"\s+rel="stylesheet"\s*/?>\s*\n?',
    re.IGNORECASE,
)

def transform(html: str) -> str:
    html = RE_PRECONNECT_GOOGLE.sub("", html)
    html = RE_PRECONNECT_GSTATIC.sub("", html)
    html = RE_GOOGLE_FONTS_CSS.sub("", html)
    return html

def main() -> None:
    files = list(DST.glob("*.html")) + list(DST.glob("article/*.html"))
    for f in files:
        out = transform(f.read_text(encoding="utf-8"))
        f.write_text(out, encoding="utf-8")
    print(f"Stripped Google Fonts from {len(files)} files")

if __name__ == "__main__":
    main()
