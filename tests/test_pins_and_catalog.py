"""R6.1, R6.7, NFR-4: vendored upper ontologies match the shared pin and every import resolves locally."""

from rdflib import OWL, RDF, Graph, URIRef

from aoc_dfo import BASE_IRI, IMPORTS_DIR
from aoc_dfo.modules import MODULES, actual_imports
from aoc_dfo.pins import load_catalog, load_pins, verify_pins


def test_vendored_files_match_pinned_hashes():
    assert verify_pins() == []


def test_pins_cover_bfo_and_cco():
    assert {p.name for p in load_pins()} == {"BFO 2020", "CCO"}


def test_catalog_maps_both_iris_of_each_pin():
    catalog = load_catalog()
    for pin in load_pins():
        for iri in (pin.ontology_iri, pin.version_iri):
            assert catalog.get(iri) == pin.path.resolve(), iri


def test_catalog_targets_exist():
    missing = [iri for iri, path in load_catalog().items() if not path.exists()]
    assert missing == []


def test_every_module_import_resolves_through_catalog():
    catalog = load_catalog()
    unresolved = {
        (m.name, str(iri))
        for m in MODULES
        for iri in actual_imports(m.path)
        if str(iri) not in catalog
    }
    assert unresolved == set()


def test_catalog_module_entries_use_base_iri():
    module_iris = {k for k in load_catalog() if not k.startswith(("http://purl.obolibrary.org",
                                                                   "https://www.commoncoreontologies"))}
    assert module_iris == {BASE_IRI + m.name for m in MODULES}


def test_pinned_version_iris_are_declared_in_vendored_files():
    for pin in load_pins():
        g = Graph().parse(pin.path, format="turtle")
        ont = URIRef(pin.ontology_iri)
        assert (ont, RDF.type, OWL.Ontology) in g
        assert (ont, OWL.versionIRI, URIRef(pin.version_iri)) in g


def test_only_pinned_files_are_vendored():
    vendored = {p.name for p in IMPORTS_DIR.glob("*.ttl")}
    assert vendored == {p.file for p in load_pins()}
