"""Tasks 1.5 and 1.6: the corpus interface, the citation gate, and the corpus MCP server."""

import asyncio
import json
import sys

import pytest

from aoc_dfo import corpus
from aoc_dfo.citations import Citation, catalog_citations, check, rdf_citations
from aoc_dfo.provenance import SOURCE_BASE
from aoc_dfo import mcp_server


# --- corpus ---------------------------------------------------------------------------------

def test_ingested_sources_include_design_and_niem():
    ids = corpus.ingested_ids()
    assert ids[:2] == ["AOC-DFO-DES-1.1", "NIEM-6.0"]


def test_resolve_returns_exact_text_or_fails():
    seg = corpus.resolve("NIEM-6.0", "usmtf:AirTaskingOrderNumberType")
    assert "Air Tasking Order" in seg.text
    with pytest.raises(KeyError):
        corpus.resolve("NIEM-6.0", "usmtf:NoSuchThing")
    with pytest.raises(KeyError):
        corpus.resolve("AFMAN-13-1AOCV3-NOT-INGESTED", "para-1.1")


def test_search_requires_every_word():
    hits = corpus.search("air tasking order number", limit=50)
    assert hits and all(all(w in (h.anchor + h.text).lower() for w in ("air", "tasking", "order"))
                        for h in hits)
    assert corpus.search("") == []


# --- citation gate (1.6) --------------------------------------------------------------------

def test_every_citation_in_the_repo_resolves():
    cites = rdf_citations() + catalog_citations()
    assert cites, "aoc-prov terms cite the design"
    assert check(cites) == []


@pytest.mark.parametrize("iri,why", [
    (SOURCE_BASE + "AOC-DFO-DES-1.1#sec-99", "no anchor"),
    (SOURCE_BASE + "NIEM-6.0#usmtf:Invented", "no anchor"),
    (SOURCE_BASE + "AFMAN-13-1AOCV3#para-1.1", "not ingested"),
    (SOURCE_BASE + "AOC-DFO-DES-1.1", "is not <"),
    ("https://example.org/doc#p1", "is not <"),
])
def test_gate_rejects_unresolvable_citations(iri, why):
    problems = check([Citation("probe", iri)])
    assert len(problems) == 1 and why in problems[0]


def test_gate_reads_catalog_rows(tmp_path):
    (tmp_path / "flows.csv").write_text(
        "id,citation\nF1," + SOURCE_BASE + "NIEM-6.0#mo:SortieType\nF2,"
        + SOURCE_BASE + "NIEM-6.0#mo:Nope\n", encoding="utf-8")
    problems = check(catalog_citations(tmp_path))
    assert len(problems) == 1 and "flows.csv:3" in problems[0]


# --- MCP server (1.5) -----------------------------------------------------------------------

def test_tools_in_process():
    srcs = mcp_server.list_sources()
    by_id = {s["id"]: s for s in srcs}
    assert by_id["NIEM-6.0"]["ingested"] and not by_id["MIL-STD-6040"]["ingested"]
    assert all(s["status"] == "unavailable" for s in mcp_server.list_sources(tier="2"))
    hit = mcp_server.fetch("NIEM-6.0", "mo:SortieType")
    assert hit["citation"] == SOURCE_BASE + "NIEM-6.0#mo:SortieType"
    assert mcp_server.search("sortie", source_id="NIEM-6.0", limit=5)


def test_stdio_round_trip():
    """Start the real server over stdio and call each tool through an MCP client."""
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    async def run():
        params = StdioServerParameters(command=sys.executable, args=["-m", "aoc_dfo.mcp_server"])
        async with stdio_client(params) as (r, w), ClientSession(r, w) as session:
            await session.initialize()
            names = {t.name for t in (await session.list_tools()).tools}
            assert names == {"list_sources", "search", "fetch"}
            res = await session.call_tool("fetch", {"source_id": "AOC-DFO-DES-1.1", "anchor": "sec-7"})
            body = json.loads(res.content[0].text)
            assert body["anchor"] == "sec-7" and "Provenance" in body["text"]
            bad = await session.call_tool("fetch", {"source_id": "NIEM-6.0", "anchor": "mo:Nope"})
            assert bad.isError

    asyncio.run(run())
