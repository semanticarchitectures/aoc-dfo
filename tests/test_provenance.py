"""R1.2, R1.3, R1.7, R8.6: the provenance pattern (Amendment 002) and its SHACL shapes."""

import re

import pytest
from rdflib import OWL, RDF, Dataset, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, PROV

from aoc_dfo import DFO_NS
from aoc_dfo.modules import BY_NAME, header_graph
from aoc_dfo.canonical import canonical_turtle
from aoc_dfo.provenance import (SOURCE_BASE, SOURCES_PATH, render_sources, sources_dataset,
                                split_citation, vocab_graph)
from aoc_dfo.registry import load_registry
from aoc_dfo.validate import data_graph, run_shapes

DFO = Namespace(DFO_NS)
SPEC = SOURCE_BASE + "AOC-DFO-DES-1.1"


def cite(term, iri):
    g = Graph()
    g.add((term, RDF.type, OWL.Class))
    if iri is not None:
        g.add((term, DCTERMS.source, URIRef(iri)))
    return g


def messages(extra):
    conforms, results, text = run_shapes(data_graph(extra))
    return conforms, text


# --- generated files are current and deterministic ------------------------------------------

def test_sources_trig_is_current():
    assert SOURCES_PATH.read_text(encoding="utf-8") == render_sources(sources_dataset()), \
        "run `uv run aoc-dfo prov`"


def test_aoc_prov_module_is_current():
    m = BY_NAME["aoc-prov"]
    g = header_graph(m) + vocab_graph()
    for prefix, ns in vocab_graph().namespaces():
        g.bind(prefix, ns)
    assert m.path.read_text(encoding="utf-8") == canonical_turtle(g), "run `uv run aoc-dfo prov`"


def test_one_named_graph_per_registry_entry():
    ds = Dataset()
    ds.parse(SOURCES_PATH, format="trig")
    names = {str(g.identifier) for g in ds.graphs() if len(g)}
    assert names == {SOURCE_BASE + s["id"] for s in load_registry()["sources"]}
    for g in ds.graphs():
        if len(g):  # each graph describes only its own source version
            assert set(g.subjects()) == {g.identifier}


# --- the real ontology conforms ------------------------------------------------------------

def test_ontology_modules_conform():
    conforms, text = messages(None)
    assert conforms, text


def test_design_section_anchors_exist():
    """Citations of the design spec point at real section numbers."""
    from aoc_dfo import SPEC_DIR
    sections = {f"sec-{m}" for m in re.findall(r"^#{2,3} (\d+(?:\.\d+)?)\.? ",
                                                 (SPEC_DIR / "design.md").read_text(), re.M)}
    cited = {split_citation(str(o))[1] for o in data_graph().objects(None, DCTERMS.source)
             if split_citation(str(o)) and split_citation(str(o))[0] == "AOC-DFO-DES-1.1"}
    assert cited and cited <= sections, cited - sections


# --- the shapes reject what they must ------------------------------------------------------

def test_class_with_anchored_citation_passes():
    conforms, text = messages(cite(DFO.ProbeClass, SPEC + "#sec-7"))
    assert conforms, text


@pytest.mark.parametrize("iri,why", [
    (None, "no anchored source citation"),
    (SPEC, "no anchored source citation"),                       # no anchor
    (SPEC + "#", "no anchored source citation"),                 # empty anchor
    (SOURCE_BASE + "NO-SUCH-SOURCE#p1", "not in the corpus registry"),
    (SOURCE_BASE + "MIL-STD-6040#field-1", "not available"),     # tier 2, unavailable
    (SOURCE_BASE + "JP-3-30#para-1", "not available"),           # tier 1b, unavailable
    (SOURCE_BASE + "NATO-STANAG-5516#p1", "not available"),      # verify-availability
])
def test_bad_citations_are_rejected(iri, why):
    conforms, text = messages(cite(DFO.ProbeClass, iri))
    assert not conforms and why in text, text


def test_terms_outside_the_dfo_namespace_are_ignored():
    g = Graph()
    g.add((URIRef("https://example.org/Other"), RDF.type, OWL.Class))
    conforms, text = messages(g)
    assert conforms, text


def test_individual_needs_citation_unless_synthetic():
    ind = URIRef("https://w3id.org/aoc-dfo/data/step-1")
    g = Graph()
    g.add((ind, RDF.type, OWL.NamedIndividual))
    g.add((ind, RDF.type, DFO.ProbeClass))
    g += cite(DFO.ProbeClass, SPEC + "#sec-3.6")
    conforms, text = messages(g)
    assert not conforms and "prov:wasDerivedFrom" in text
    g.add((ind, DFO.isSynthetic, Literal(True)))
    assert messages(g)[0]
    g.remove((ind, DFO.isSynthetic, Literal(True)))
    g.add((ind, PROV.wasDerivedFrom, URIRef(SPEC + "#sec-3.6")))
    assert messages(g)[0]


def test_incomplete_source_version_is_rejected():
    bad = URIRef(SOURCE_BASE + "BROKEN")
    g = Graph()
    g.add((bad, RDF.type, PROV.Entity))
    g.add((bad, DCTERMS.identifier, Literal("BROKEN")))
    g.add((bad, DFO.sourceTier, Literal("3")))
    conforms, text = messages(g)
    assert not conforms
    for missing in ("title", "edition", "availability", "handlingCaveat"):
        assert missing in text
