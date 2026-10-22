"""Ontology modules and their ``owl:imports`` contract (design §8, R12.2, R14.3).

The module headers in ``ontology/*.ttl`` are generated from this table by
``aoc-dfo headers`` while a module has no content. Once a module has content, its header is
edited by hand and this table is only used to check it.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from rdflib import OWL, RDF, RDFS, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS

from . import BASE_IRI, DFO_NS, ONTOLOGY_DIR, __version__
from .pins import load_pins

DFO = Namespace(DFO_NS)

BFO = "bfo"
CCO = "cco"


@dataclass(frozen=True)
class Module:
    name: str
    title: str
    description: str
    imports: tuple[str, ...]  # other module names, or BFO / CCO
    in_top: bool = True  # imported by the top-level aoc-dfo module

    @property
    def iri(self) -> URIRef:
        return URIRef(BASE_IRI + self.name)

    @property
    def version_iri(self) -> URIRef:
        return URIRef(f"{BASE_IRI}{__version__}/{self.name}")

    @property
    def path(self) -> Path:
        return ONTOLOGY_DIR / f"{self.name}.ttl"


MODULES: tuple[Module, ...] = (
    Module("aoc-domain", "AOC-DFO domain entities",
           "What messages are about: aircraft, missions, targets, airspace, units, times, "
           "locations. Reuses CCO 2.2; adds only CQ-gated classes (design §3.4).",
           (BFO, CCO)),
    Module("aoc-msgstruct", "AOC-DFO message structure",
           "Message syntax only: sets, segments, fields, repeatable groups, format standards. "
           "No domain semantics (design §3.2, MR-6).",
           (BFO, CCO)),
    Module("aoc-messages", "AOC-DFO message types",
           "Message types (IBE) and their content (ICE), generated from catalog/messages.csv "
           "(design §3.3).",
           ("aoc-msgstruct", "aoc-domain")),
    Module("aoc-doctrine", "AOC-DFO doctrine layer",
           "C2 nodes, doctrine processes, decisions, the air tasking cycle and doctrinal "
           "products (design §3.1). ENSIM names reused.",
           ("aoc-domain",)),
    Module("aoc-flows", "AOC-DFO data flows",
           "Doctrinal data flows as acts of communication, with channels and implementing "
           "systems (design §3.5).",
           ("aoc-doctrine", "aoc-messages")),
    Module("aoc-threads", "AOC-DFO mission threads",
           "Design-time mission-thread layer: scenarios, transmission steps, channel types, "
           "endpoint roles (design §3.6, R13).",
           ("aoc-flows",)),
    Module("aoc-dfo", "AOC Data Flow Ontology",
           "Top-level module. Imports every core module (design §8).",
           ("aoc-domain", "aoc-msgstruct", "aoc-messages", "aoc-doctrine", "aoc-flows",
            "aoc-threads")),
    Module("aoc-align", "AOC-DFO alignment",
           "Alignment axioms to ENSIM, the KB ontology and GMNS. Not imported by any core "
           "module (design §3.7, R14.3).",
           ("aoc-dfo",), in_top=False),
)

BY_NAME = {m.name: m for m in MODULES}


def upper_import_iris() -> dict[str, URIRef]:
    """Import IRIs for BFO and CCO. CCO is imported by version IRI so the pin is explicit;
    BFO has only an undated version IRI, so it is imported by that PURL."""
    pins = {p.name: p for p in load_pins()}
    return {
        BFO: URIRef(pins["BFO 2020"].version_iri),
        CCO: URIRef(pins["CCO"].version_iri),
    }


def expected_imports(module: Module) -> set[URIRef]:
    upper = upper_import_iris()
    return {upper[i] if i in upper else BY_NAME[i].iri for i in module.imports}


def actual_imports(path: Path) -> set[URIRef]:
    g = Graph().parse(path, format="turtle")
    onts = list(g.subjects(RDF.type, OWL.Ontology))
    if len(onts) != 1:
        raise ValueError(f"{path.name}: expected exactly one owl:Ontology, found {len(onts)}")
    return {o for o in g.objects(onts[0], OWL.imports) if isinstance(o, URIRef)}


def header_graph(module: Module) -> Graph:
    g = Graph()
    g.bind("owl", OWL)
    g.bind("rdfs", RDFS)
    g.bind("dcterms", DCTERMS)
    g.bind("dfo", DFO)
    ont = module.iri
    g.add((ont, RDF.type, OWL.Ontology))
    g.add((ont, OWL.versionIRI, module.version_iri))
    g.add((ont, OWL.versionInfo, Literal(__version__)))
    g.add((ont, RDFS.label, Literal(module.title, lang="en")))
    g.add((ont, DCTERMS.title, Literal(module.title, lang="en")))
    g.add((ont, DCTERMS.description, Literal(module.description, lang="en")))
    g.add((ont, DCTERMS.license, URIRef("https://www.apache.org/licenses/LICENSE-2.0")))
    g.add((ont, DCTERMS.source, URIRef("https://github.com/semanticarchitectures/aoc-dfo")))
    g.add((ont, RDFS.comment, Literal(
        "Public, unclassified content only (HANDLING.md). Upper ontologies at the AKS shared "
        "pin: BFO 2020 release-2024-01-29, CCO v2.2.", lang="en")))
    for iri in sorted(expected_imports(module)):
        g.add((ont, OWL.imports, iri))
    return g
