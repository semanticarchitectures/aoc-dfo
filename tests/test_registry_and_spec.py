"""R1.1, R1.3, R1.6 (registry); MR-9 (every cco: shorthand in the spec exists in CCO 2.2)."""

from aoc_dfo import REPO_ROOT
from aoc_dfo.labelmap import render_markdown, resolve_tokens, spec_tokens
from aoc_dfo.registry import check_registry


def test_registry_is_valid():
    assert check_registry() == []


def test_registry_rejects_available_tier2():
    bad = {"sources": [{"id": "X", "title": "t", "issuer": "i", "edition": "e", "tier": "2",
                        "status": "verified", "url": "https://example.org", "role": "r"}]}
    assert any("OD-1" in p for p in check_registry(bad))


def _src(sid, url, **kw):
    return {"id": sid, "title": "t", "issuer": "i", "edition": "e", "tier": "1a",
            "status": "superseded", "url": url, "role": "r", **kw}


def test_r16_rejects_unofficial_host_without_amendment():
    """A003: a mirror is refused unless archive: true, and only JP-3-30-2019 may be an archive."""
    assert any("not an official host" in p
               for p in check_registry({"sources": [_src("JP-3-09-2019", "https://irp.fas.org/x.pdf")]}))
    assert any("allowed only for" in p for p in check_registry(
        {"sources": [_src("JP-3-09-2019", "https://irp.fas.org/x.pdf", archive=True)]}))
    assert any("not an official host" in p for p in check_registry(
        {"sources": [_src("JP-3-30-2014", "https://nsarchive.gwu.edu/x.pdf")]}))
    assert check_registry({"sources": [
        _src("JP-3-30-2019", "https://irp.fas.org/doddir/dod/jp3_30.pdf", archive=True),
        _src("JP-3-52-2014", "https://edocs.nps.edu/2014/December/jp3_52.pdf"),
        _src("JP-3-60-2018", "https://www.esd.whs.mil/x.pdf")]}) == []


def test_jp_3_30_archive_caveat_reaches_provenance():
    from rdflib import Literal, URIRef
    from aoc_dfo.provenance import DFO, sources_dataset, source_iri

    iri = source_iri("JP-3-30-2019")
    g = sources_dataset().graph(iri)
    caveat = str(g.value(iri, DFO.handlingCaveat))
    assert "archived copy" in caveat and "not an official host" in caveat
    assert g.value(iri, DFO.supersededBy) == source_iri("JP-3-30")


def test_every_cco_shorthand_in_spec_resolves():
    _, missing = resolve_tokens(spec_tokens())
    assert missing == [], "spec names CCO terms that are not in CCO 2.2: " + ", ".join(missing)


def test_label_map_is_current():
    found, _ = resolve_tokens(spec_tokens())
    committed = (REPO_ROOT / "docs" / "cco-label-map.md").read_text(encoding="utf-8")
    assert committed == render_markdown(found), "run `uv run aoc-dfo labelmap`"
