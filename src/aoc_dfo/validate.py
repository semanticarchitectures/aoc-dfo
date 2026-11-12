"""SHACL validation of the ontology modules against the provenance shapes (R8.6, R1.6 gate)."""

from __future__ import annotations

from pathlib import Path

from pyshacl import validate
from rdflib import Dataset, Graph

from . import ONTOLOGY_DIR, REPO_ROOT
from .provenance import SOURCES_PATH

SHAPES_DIR = REPO_ROOT / "shapes"


def data_graph(extra: Graph | None = None, sources: Path = SOURCES_PATH) -> Graph:
    """All AOC-DFO modules (not the vendored imports) plus every source-version graph."""
    g = Graph()
    for path in sorted(ONTOLOGY_DIR.glob("*.ttl")):
        g.parse(path, format="turtle")
    ds = Dataset()
    ds.parse(sources, format="trig")
    for s, p, o, _ in ds.quads((None, None, None, None)):
        g.add((s, p, o))
    if extra is not None:
        g += extra
    return g


def run_shapes(data: Graph, shapes: str = "provenance.ttl") -> tuple[bool, Graph, str]:
    sg = Graph().parse(SHAPES_DIR / shapes, format="turtle")
    conforms, results, text = validate(data, shacl_graph=sg, inference="none",
                                       advanced=True, allow_warnings=False)
    return conforms, results, text
