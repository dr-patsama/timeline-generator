#!/usr/bin/env python3
"""Convert the bilingual (TH default) LIFE by Dr. Pat site into an English-only site.

Source: /Users/DrPatsama/Documents/LIFEbydrpat WEBSITE/*.html
Destination: /Users/DrPatsama/Documents/LIFEbydrpat WEBSITE EN/

Per-file transforms (all regex-based and deterministic):
  1. <html lang="th">                            -> <html lang="en">
  2. <title data-bi data-en="X" data-th="Y">Z</title>
                                                 -> <title>X</title>
  3. <span class="lang-en">EN</span><span class="lang-th">TH</span>
                                                 -> EN
     (any order; also handles the standalone cases)
  4. Strip the <div class="lang-switch">…</div> button group from the nav.
  5. Strip the <li> wrapper that ONLY contains the lang-switch (cleans up footer / dropdowns).
  6. Replace Google Fonts link (drop Sarabun, add Playfair Display) and update the
     stylesheet link comment to point at the EN assets (path stays "assets/css/style.css").

The assets/ folder (css + js) is authored separately and not regenerated here.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

SRC = Path("/Users/DrPatsama/Documents/LIFEbydrpat WEBSITE")
DST = Path("/Users/DrPatsama/Documents/LIFEbydrpat WEBSITE EN")

# ---------- regex patterns ----------

# 1. <html lang="th"> -> <html lang="en">
RE_HTML_LANG = re.compile(r'<html\s+lang="th"', re.IGNORECASE)

# 2. <title data-bi data-en="…" data-th="…">…</title>
RE_TITLE_BI = re.compile(
    r'<title\b[^>]*\bdata-bi\b[^>]*\bdata-en="([^"]*)"[^>]*>[^<]*</title>',
    re.IGNORECASE | re.DOTALL,
)
# (data-en may come before data-th — pattern just captures data-en)
RE_TITLE_BI_ALT = re.compile(
    r'<title\b[^>]*\bdata-en="([^"]*)"[^>]*\bdata-bi\b[^>]*>[^<]*</title>',
    re.IGNORECASE | re.DOTALL,
)

# 3a. EN then TH: <span class="lang-en">EN</span><span class="lang-th">TH</span>
RE_EN_THEN_TH = re.compile(
    r'<span\s+class="lang-en">(?P<en>.*?)</span>\s*<span\s+class="lang-th">.*?</span>',
    re.IGNORECASE | re.DOTALL,
)
# 3b. TH then EN
RE_TH_THEN_EN = re.compile(
    r'<span\s+class="lang-th">.*?</span>\s*<span\s+class="lang-en">(?P<en>.*?)</span>',
    re.IGNORECASE | re.DOTALL,
)
# 3c. lone EN span — unwrap
RE_LONE_EN = re.compile(
    r'<span\s+class="lang-en">(?P<en>.*?)</span>',
    re.IGNORECASE | re.DOTALL,
)
# 3d. lone TH span — drop entirely
RE_LONE_TH = re.compile(
    r'<span\s+class="lang-th">.*?</span>',
    re.IGNORECASE | re.DOTALL,
)

# 4. <div class="lang-switch" …>…</div>
RE_LANG_SWITCH_DIV = re.compile(
    r'<div\s+class="lang-switch"[^>]*>.*?</div>',
    re.IGNORECASE | re.DOTALL,
)
# 5. The <li>…lang-switch…</li> wrapper (nav). Match the whole <li> with the empty div.
RE_LANG_SWITCH_LI = re.compile(
    r'<li>\s*(?:<div\s+class="lang-switch"[^>]*>\s*</div>\s*)?</li>',
    re.IGNORECASE | re.DOTALL,
)
# Also strip any now-empty <li></li>
RE_EMPTY_LI = re.compile(r'<li>\s*</li>', re.IGNORECASE)

# 6. Google Fonts link (drop Sarabun, add Playfair Display)
RE_GOOGLE_FONTS = re.compile(
    r'<link\s+href="https://fonts\.googleapis\.com/css2\?[^"]*"\s+rel="stylesheet"\s*/?>',
    re.IGNORECASE,
)
NEW_FONTS_LINK = (
    '<link href="https://fonts.googleapis.com/css2?'
    'family=Inter:wght@400;500;600;700&'
    'family=Playfair+Display:wght@500;600;700&display=swap" rel="stylesheet">'
)

# Title element (no data-bi) — leave alone for fallback. We only rewrite bilingual ones.


def transform_html(html: str) -> str:
    # 1. lang attribute
    html = RE_HTML_LANG.sub('<html lang="en"', html)

    # 2. bilingual title — try both attribute orderings
    def _title_sub(m: re.Match) -> str:
        return f'<title>{m.group(1)}</title>'

    html = RE_TITLE_BI.sub(_title_sub, html)
    html = RE_TITLE_BI_ALT.sub(_title_sub, html)

    # 3. lang spans — order matters: pair-patterns first, then lone-TH, then lone-EN
    html = RE_EN_THEN_TH.sub(lambda m: m.group("en"), html)
    html = RE_TH_THEN_EN.sub(lambda m: m.group("en"), html)
    html = RE_LONE_TH.sub("", html)
    html = RE_LONE_EN.sub(lambda m: m.group("en"), html)

    # 4 + 5. Strip language switcher
    html = RE_LANG_SWITCH_DIV.sub("", html)
    html = RE_LANG_SWITCH_LI.sub("", html)
    html = RE_EMPTY_LI.sub("", html)

    # 6. Fonts
    html = RE_GOOGLE_FONTS.sub(NEW_FONTS_LINK, html)

    return html


def convert_file(src: Path, dst: Path) -> None:
    text = src.read_text(encoding="utf-8")
    out = transform_html(text)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(out, encoding="utf-8")


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"Source folder missing: {SRC}")
    DST.mkdir(parents=True, exist_ok=True)

    # Convert all top-level .html files
    html_files = sorted(SRC.glob("*.html"))
    print(f"Found {len(html_files)} HTML files in source")

    for f in html_files:
        out_path = DST / f.name
        convert_file(f, out_path)
        print(f"  converted: {f.name}")

    # Convert any nested article/*.html files (currently empty but future-proof)
    for f in sorted(SRC.glob("article/*.html")):
        out_path = DST / "article" / f.name
        convert_file(f, out_path)
        print(f"  converted: article/{f.name}")

    print(f"\nDone. Output: {DST}")


if __name__ == "__main__":
    main()
