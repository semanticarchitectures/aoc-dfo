"""Citation gate (task 1.6, R1.2): every citation must resolve to text that exists.

The SHACL shapes check that a citation is well formed and names a registered, citable source.
This gate goes further: the anchor must exist in the ingested source, so a citation cannot point
at a paragraph that is not there. It scans:

* ontology modules and RDF data (``dcterms:source``, ``prov:wasDerivedFrom``);
* catalog CSV rows with a ``citation`` column (message, element and flow catalogs, Phases 3–7).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from rdflib import Graph, URIRef
from rdflib.namespace import DCTERMS, PROV

from . import ONTOLOGY_DIR, REPO_ROOT
from . import corpus
from .provenance import SOURCE_BASE, split_citation

DATA_DIRS = (REPO_ROOT / "data",)
CATALOG_DIR = REPO_ROOT / "catalog"
CITING = (DCTERMS.source, PROV.wasDerivedFrom)


@dataclass(frozen=True)
class Citation:
    where: str      # file and subject or row
    iri: str


def rdf_citations() -> list[Citation]:
    out = []
    paths = sorted(ONTOLOGY_DIR.glob("*.ttl"))
    for d in DATA_DIRS:
        paths += sorted(d.rglob("*.ttl"))
    for path in paths:
        g = Graph().parse(path, format="turtle")
        for pred in CITING:
            for s, o in g.subject_objects(pred):
                if isinstance(o, URIRef) and str(o).startswith(SOURCE_BASE):
                    out.append(Citation(f"{path.relative_to(REPO_ROOT)} {s}", str(o)))
    return out


def catalog_citations(root: Path = CATALOG_DIR) -> list[Citation]:
    out = []
    for path in sorted(root.rglob("*.csv")):
        rel = path.relative_to(root)
        if "canonical" in rel.parts:  # reference tables are sources, not citing artifacts
            continue
        with path.open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or "citation" not in reader.fieldnames:
                continue
            for n, row in enumerate(reader, start=2):
                for iri in filter(None, (row["citation"] or "").split()):
                    out.append(Citation(f"{rel}:{n}", iri))
    return out


def check(citations: list[Citation] | None = None) -> list[str]:
    """Problems; empty means every citation resolves to an existing anchor."""
    citations = citations if citations is not None else rdf_citations() + catalog_citations()
    ingested = set(corpus.ingested_ids())
    problems = []
    for c in citations:
        parts = split_citation(c.iri)
        if parts is None:
            problems.append(f"{c.where}: {c.iri} is not <{SOURCE_BASE}<id>#<anchor>>")
            continue
        sid, anchor = parts
        if sid not in ingested:
            problems.append(f"{c.where}: {sid} is not ingested; cite only ingested sources")
            continue
        try:
            corpus.resolve(sid, anchor)
        except KeyError:
            problems.append(f"{c.where}: no anchor '{anchor}' in {sid}")
    return problems
