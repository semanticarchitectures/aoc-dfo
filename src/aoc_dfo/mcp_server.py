"""Corpus MCP server (task 1.5, R5.4): read-only access for extraction agents.

Run: ``uv run aoc-dfo-mcp`` (stdio). Tools:

* ``list_sources``: every registered source with tier, status, and whether it is ingested.
* ``search``: anchored segments matching every query word, optionally in one source.
* ``fetch``: the exact text at ``<source_id>#<anchor>``, with the citation IRI to use.

Nothing here writes. Every result carries the citation IRI an extractor must attach, so an
agent cannot produce a row without an anchor that the CI gate (task 1.6) can check.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import corpus
from .provenance import SOURCE_BASE
from .registry import load_registry

server = FastMCP("aoc-dfo-corpus")


def _seg(s: corpus.Segment) -> dict:
    return {"source_id": s.source_id, "anchor": s.anchor, "kind": s.kind, "page": s.page,
            "text": s.text, "citation": f"{SOURCE_BASE}{s.source_id}#{s.anchor}"}


@server.tool()
def list_sources(tier: str | None = None, status: str | None = None) -> list[dict]:
    """Registered sources. Filter by tier (1a, 1b, 2) or status (verified, unavailable, ...).
    Only sources with ingested=true can be cited."""
    ingested = set(corpus.ingested_ids())
    out = []
    for s in load_registry()["sources"]:
        if (tier and str(s["tier"]) != tier) or (status and s["status"] != status):
            continue
        out.append({"id": s["id"], "title": s["title"], "edition": str(s["edition"]),
                    "tier": str(s["tier"]), "status": s["status"],
                    "ingested": s["id"] in ingested})
    return out


@server.tool()
def search(query: str, source_id: str | None = None, limit: int = 20) -> list[dict]:
    """Anchored segments containing every word of the query (case-insensitive)."""
    return [_seg(s) for s in corpus.search(query, source_id, max(1, min(limit, 100)))]


@server.tool()
def fetch(source_id: str, anchor: str) -> dict:
    """The exact text at one anchor. Errors if the source is not ingested or the anchor
    does not exist, rather than returning anything approximate."""
    return _seg(corpus.resolve(source_id, anchor))


def main() -> None:
    server.run()


if __name__ == "__main__":
    main()
