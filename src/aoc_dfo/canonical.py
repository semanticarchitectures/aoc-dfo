"""Canonical Turtle serialization (NFR-2): one deterministic form so diffs show real changes."""

from __future__ import annotations

from pathlib import Path

from rdflib import Graph

HEADER = (
    "# AOC-DFO — public, unclassified content only (HANDLING.md).\n"
    "# Canonical Turtle: format with `uv run aoc-dfo fmt`; CI rejects other layouts.\n"
)


def canonical_turtle(graph: Graph) -> str:
    body = graph.serialize(format="turtle")
    return HEADER + "\n" + body.strip() + "\n"


def canonicalize_file(path: Path) -> str:
    return canonical_turtle(Graph().parse(path, format="turtle"))


def is_canonical(path: Path) -> bool:
    return path.read_text(encoding="utf-8") == canonicalize_file(path)
