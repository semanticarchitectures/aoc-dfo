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


def test_every_cco_shorthand_in_spec_resolves():
    _, missing = resolve_tokens(spec_tokens())
    assert missing == [], "spec names CCO terms that are not in CCO 2.2: " + ", ".join(missing)


def test_label_map_is_current():
    found, _ = resolve_tokens(spec_tokens())
    committed = (REPO_ROOT / "docs" / "cco-label-map.md").read_text(encoding="utf-8")
    assert committed == render_markdown(found), "run `uv run aoc-dfo labelmap`"
