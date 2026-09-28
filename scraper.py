"""Scrape national-focus (and other) icons from Yard1's HoI4 GFX Search site.

The site is a generated static page: each category is an <h6>, and each icon
is a .icon div wrapping an <img>. We keep the remote URLs (no bulk download)
and store them in SQLite for the in-app picker.
"""

from __future__ import annotations

import re
from urllib.parse import quote
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

GFX_SEARCH_URL = "https://yard1.github.io/HoI4-GFX-Search/"
USER_AGENT = "FocusTreeLifeGoals/1.0 (personal life-goal tracker)"


def _abs_url(src: str) -> str:
    path = src.replace("\\", "/").lstrip("/")
    return GFX_SEARCH_URL + quote(path, safe="/")


def _pretty_name(raw: str) -> str:
    text = (raw or "").strip()
    text = re.sub(r"^GFX_", "", text)
    text = re.sub(r"_ccp_2d_sov_compatibility$", "", text, flags=re.I)
    text = text.replace("_", " ").replace("-", " ")
    return re.sub(r"\s+", " ", text).strip() or "Untitled icon"


def scrape_icons(html: str | None = None) -> list[tuple[str, str, str, str]]:
    if html is None:
        request = Request(GFX_SEARCH_URL, headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=60) as response:
            html = response.read().decode("utf-8", "replace")

    soup = BeautifulSoup(html, "html.parser")
    seen = set()
    icons: list[tuple[str, str, str, str]] = []

    for heading in soup.select("h6"):
        category = heading.get_text(" ", strip=True)
        category = re.sub(r"\s*\(\d+\)\s*$", "", category).strip()
        container = heading.find_next("div", class_="icon-container")
        if not container:
            continue
        for icon_div in container.find_all("div", class_="icon", recursive=False):
            img = icon_div.find("img")
            if not img or not img.get("src"):
                continue
            url = _abs_url(img["src"])
            if url in seen:
                continue
            seen.add(url)
            raw = (
                icon_div.get("data-search-text")
                or icon_div.get("title")
                or img.get("alt")
                or ""
            )
            name = _pretty_name(raw)
            search_text = f"{raw} {name} {category}".lower()
            icons.append((name, category, url, search_text))

    return icons
