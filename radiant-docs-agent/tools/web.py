"""Keyless web tools: DuckDuckGo search and page fetch."""

import re

import httpx
from bs4 import BeautifulSoup
from ddgs import DDGS
from langchain_core.tools import tool

MAX_PAGE_CHARS = 12000


@tool(parse_docstring=True)
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web and return titles, URLs and snippets.

    Args:
        query: Search query, e.g. "RadiantOne IDDM custom connector".
        max_results: Number of results to return (1-10).
    """
    max_results = max(1, min(max_results, 10))
    results = DDGS().text(query, max_results=max_results)
    if not results:
        return "No results."
    return "\n\n".join(
        f"{r.get('title', '')}\n{r.get('href', '')}\n{r.get('body', '')}" for r in results
    )


@tool(parse_docstring=True)
def fetch_page(url: str) -> str:
    """Download a web page and return its readable text.

    Args:
        url: Full http(s) URL returned by web_search.
    """
    response = httpx.get(
        url,
        follow_redirects=True,
        timeout=20,
        headers={"User-Agent": "Mozilla/5.0 (radiant-docs-agent)"},
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()
    text = re.sub(r"\n\s*\n+", "\n\n", soup.get_text("\n")).strip()
    return text[:MAX_PAGE_CHARS]
