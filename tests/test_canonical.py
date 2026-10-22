"""NFR-2: committed ontology files are in canonical Turtle, and serialization is stable."""

import pytest
from rdflib import Graph

from aoc_dfo import ONTOLOGY_DIR
from aoc_dfo.canonical import canonical_turtle, canonicalize_file, is_canonical

FILES = sorted(ONTOLOGY_DIR.glob("*.ttl"))


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.name)
def test_file_is_canonical(path):
    assert is_canonical(path), f"{path.name} is not canonical; run `uv run aoc-dfo fmt`"


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.name)
def test_serialization_is_idempotent(path):
    once = canonicalize_file(path)
    twice = canonical_turtle(Graph().parse(data=once, format="turtle"))
    assert once == twice
