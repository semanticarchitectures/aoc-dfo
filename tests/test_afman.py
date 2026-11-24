"""Task 1.3: AFMAN 13-1AOC Vol 3 ingested as anchored text (R1.4)."""

import json
import shutil

import pytest
import yaml

from aoc_dfo import corpus
from aoc_dfo.ingest import afman
from aoc_dfo.registry import load_registry

SEGS = afman.OUT_DIR / "segments.jsonl"


def _segs():
    return [json.loads(line) for line in SEGS.read_text(encoding="utf-8").splitlines()]


def test_pinned_hash_matches_registry_and_manifest():
    entry = {s["id"]: s for s in load_registry()["sources"]}[afman.SOURCE_ID]
    manifest = yaml.safe_load((afman.OUT_DIR / "MANIFEST.yaml").read_text(encoding="utf-8"))
    assert entry["sha256"] == afman.SHA256 == manifest["sha256"]
    assert entry["url"] == afman.URL == manifest["url"]


def test_anchors_unique_and_pages_in_order():
    segs = _segs()
    anchors = [s["anchor"] for s in segs]
    assert len(anchors) == len(set(anchors))
    pages = [s["page"] for s in segs]
    assert pages == sorted(pages) and 1 <= pages[0] and pages[-1] <= 185


def test_paragraph_numbers_follow_the_manual():
    paras = [tuple(int(x) for x in s["anchor"][5:].split("."))
             for s in _segs() if s["kind"] == "paragraph"]
    assert paras[0] == (1, 1) and len(paras) > 1800
    for a, b in zip(paras, paras[1:]):
        assert afman._next_ok(a, b) or b == (a[0] + 1, 1) or b[0] > a[0], (a, b)


@pytest.mark.parametrize("anchor,kind,needle", [
    ("chap-2", "heading", "AIR OPERATIONS CENTER"),
    ("para-2.3", "paragraph", "five divisions"),
    ("fig-4.1", "figure", "Combat Plans Division"),
    ("abbr-ATO", "abbreviation", "Air Tasking Order"),
    ("term-Cyberspace", "term", "global domain"),
    ("att1-refs", "reference-list", "JP 3-30, Joint Air Operations, 25 July 2019"),
])
def test_known_anchors_resolve(anchor, kind, needle):
    seg = corpus.resolve(afman.SOURCE_ID, anchor)
    assert seg.kind == kind and needle in seg.text


def test_next_ok():
    assert afman._next_ok((2, 3), (2, 3, 1))
    assert afman._next_ok((2, 3, 1, 4), (2, 4))
    assert afman._next_ok((2, 3, 1), (2, 3, 2))
    assert not afman._next_ok((5, 5), (5, 1))         # a wrapped "Figure\n5.1." reference
    assert not afman._next_ok((2, 3), (2, 5))


def test_segmenter_on_synthetic_pages():
    page1 = ["AFMAN13-1AOCV3 25 JUNE 2024    3", "Title page text",
             "Chapter 1—INTRODUCTION   6", "   1.1.   General. .... 6"]
    page2 = ["                Chapter 1", "", "           INTRODUCTION",
             "1.1. General. Text that refers to", "1.1. again in a wrapped line.",
             "   1.1.1. Child. (See", "Figure 1.1. Thing).",
             "Figure 1.1. Thing.", "  inside figure text",
             "1.2. Next. More.", "                Attachment 1", "  GLOSSARY",
             "Abbreviations and Acronyms", "ATO—Air Tasking", "Order continued",
             "Terms", "Cyberspace—A domain."]
    segs, notes = afman.segment([page1, page2])
    by = {s.anchor: s for s in segs}
    assert list(by) == ["front", "chap-1", "para-1.1", "para-1.1.1", "fig-1.1", "para-1.2",
                        "att-1", "abbr-ATO", "term-Cyberspace"]
    assert "1.1. again" in by["para-1.1"].text
    assert by["para-1.1.1"].text == "1.1.1. Child. (See Figure 1.1. Thing)."
    assert by["fig-1.1"].text == "Figure 1.1. Thing. inside figure text"
    assert by["abbr-ATO"].text == "ATO—Air Tasking Order continued"
    assert by["chap-1"].text == "Chapter 1 — INTRODUCTION"
    assert notes["rejected_paragraph_numbers"] == ["p2: 1.1"]


@pytest.mark.skipif(not afman.RAW_PATH.exists() or not shutil.which("pdftotext"),
                    reason="pinned PDF not present (corpus/raw is not committed)")
def test_rebuild_reproduces_committed_segments(tmp_path):
    afman.build(afman.fetch(), tmp_path)
    assert (tmp_path / "segments.jsonl").read_bytes() == SEGS.read_bytes()
