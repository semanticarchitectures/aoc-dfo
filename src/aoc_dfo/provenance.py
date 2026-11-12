"""Provenance pattern (R1, design §7 as amended by Amendment 002).

* Every registered source version is a ``prov:Entity`` in its own named graph in
  ``provenance/sources.trig``, generated from ``corpus/registry.yaml``.
* Its IRI is ``{BASE_IRI}source/<registry id>``; one registry entry is one edition.
* A class or property cites a source with ``dcterms:source <…/source/<id>#<anchor>>``. The
  fragment is the anchor (paragraph, figure, table or schema path), so each citation carries
  its own anchor. ``dcterms:source`` is an annotation property, which keeps the ontology in
  OWL 2 DL even when PROV-O is imported next to it.
* Individuals (mission-thread steps, instance data) cite with ``prov:wasDerivedFrom`` the same
  anchored IRI.
"""

from __future__ import annotations

import re
from pathlib import Path

from rdflib import OWL, RDF, RDFS, XSD, Dataset, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, PROV

from . import BASE_IRI, DFO_NS, REPO_ROOT, __version__
from .registry import load_registry

DFO = Namespace(DFO_NS)
SOURCE_BASE = BASE_IRI + "source/"
PROVENANCE_DIR = REPO_ROOT / "provenance"
SOURCES_PATH = PROVENANCE_DIR / "sources.trig"
ANCHOR = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._\-/]*$")

# Status values that mean the content of a source must never be cited (R1.3).
UNCITABLE = {"unavailable", "verify-availability"}


def source_iri(source_id: str) -> URIRef:
    return URIRef(SOURCE_BASE + source_id)


def split_citation(iri: str) -> tuple[str, str] | None:
    """``…/source/<id>#<anchor>`` → (id, anchor); None if it is not a source citation."""
    if not iri.startswith(SOURCE_BASE) or "#" not in iri:
        return None
    sid, anchor = iri[len(SOURCE_BASE):].split("#", 1)
    return (sid, anchor) if sid and anchor else None


def vocab_graph() -> Graph:
    """Content of ``ontology/aoc-prov.ttl`` besides its header."""
    g = Graph()
    g.bind("dfo", DFO)
    g.bind("prov", PROV)
    g.bind("dcterms", DCTERMS)
    spec = URIRef(SOURCE_BASE + "AOC-DFO-DES-1.1#sec-7")
    terms = [
        (DFO.sourceTier, OWL.DatatypeProperty, XSD.string,
         "source tier", "Access tier of a source version: 1a (public), 1b (unclassified but "
         "CAC-gated) or 2 (distribution-controlled)."),
        (DFO.availability, OWL.DatatypeProperty, XSD.string,
         "availability", "Registry status of a source version, e.g. verified, superseded, "
         "unavailable. Content of an unavailable source is never cited."),
        (DFO.edition, OWL.DatatypeProperty, XSD.string,
         "edition", "Edition or version of a source as its issuer states it."),
        (DFO.handlingCaveat, OWL.DatatypeProperty, XSD.string,
         "handling caveat", "Releasability statement for a source version."),
        (DFO.contentSha256, OWL.DatatypeProperty, XSD.string,
         "content SHA-256", "SHA-256 of the retrieved file the corpus text was extracted from."),
        (DFO.supersededBy, OWL.ObjectProperty, PROV.Entity,
         "superseded by", "Links a source version to the edition that supersedes it."),
    ]
    for term, kind, rng, label, comment in terms:
        g.add((term, RDF.type, kind))
        g.add((term, RDFS.label, Literal(label, lang="en")))
        g.add((term, RDFS.comment, Literal(comment, lang="en")))
        g.add((term, RDFS.domain, PROV.Entity))
        g.add((term, RDFS.range, rng))
        g.add((term, DCTERMS.source, spec))
    return g


def sources_dataset(registry: dict | None = None) -> Dataset:
    reg = registry if registry is not None else load_registry()
    default_caveat = reg.get("default_handling", "UNCLASSIFIED")
    ds = Dataset()
    for prefix, ns in (("prov", PROV), ("dcterms", DCTERMS), ("dfo", DFO), ("src", SOURCE_BASE)):
        ds.bind(prefix, ns)
    for s in reg["sources"]:
        iri = source_iri(s["id"])
        g = ds.graph(iri)
        g.add((iri, RDF.type, PROV.Entity))
        g.add((iri, DCTERMS.identifier, Literal(s["id"])))
        g.add((iri, DCTERMS.title, Literal(s["title"])))
        g.add((iri, DCTERMS.publisher, Literal(s["issuer"])))
        g.add((iri, DFO.edition, Literal(str(s["edition"]))))
        g.add((iri, DFO.sourceTier, Literal(str(s["tier"]))))
        g.add((iri, DFO.availability, Literal(s["status"])))
        g.add((iri, DFO.handlingCaveat, Literal(s.get("handling", default_caveat))))
        if s.get("url"):
            g.add((iri, PROV.atLocation, URIRef(s["url"])))
        if s.get("issued"):
            g.add((iri, DCTERMS.issued, Literal(s["issued"], datatype=XSD.date)))
        if s.get("retrieved"):
            g.add((iri, PROV.generatedAtTime, Literal(s["retrieved"], datatype=XSD.date)))
        if s.get("sha256"):
            g.add((iri, DFO.contentSha256, Literal(s["sha256"])))
        if s.get("superseded_by"):
            g.add((iri, DFO.supersededBy, source_iri(s["superseded_by"])))
    return ds


def render_sources(ds: Dataset) -> str:
    """Deterministic TriG: prefixes once, then one block per source version, sorted by IRI.
    rdflib's own TriG writer orders graphs differently from run to run."""
    prefixes = {"dcterms": DCTERMS, "dfo": DFO, "prov": PROV, "src": Namespace(SOURCE_BASE),
                "xsd": XSD}
    out = ["# AOC-DFO — public, unclassified content only (HANDLING.md).\n"
           "# Generated from corpus/registry.yaml by `uv run aoc-dfo prov`. Do not edit.\n\n"]
    out += [f"@prefix {k}: <{v}> .\n" for k, v in sorted(prefixes.items())]
    for ctx in sorted((c for c in ds.graphs() if len(c)), key=lambda c: str(c.identifier)):
        g = Graph()
        for k, v in prefixes.items():
            g.bind(k, v)
        g += ctx
        body = [ln for ln in g.serialize(format="turtle").splitlines()
                if ln.strip() and not ln.startswith("@prefix")]
        name = "src:" + str(ctx.identifier)[len(SOURCE_BASE):]
        out.append(f"\n{name} {{\n" + "\n".join("    " + ln for ln in body) + "\n}\n")
    return "".join(out)


def write_sources(path: Path = SOURCES_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_sources(sources_dataset()), encoding="utf-8")
    return path


__all__ = ["SOURCE_BASE", "UNCITABLE", "source_iri", "split_citation", "vocab_graph",
           "sources_dataset", "render_sources", "write_sources", "__version__"]
