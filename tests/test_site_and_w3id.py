"""The Pages site has every document the w3id rules can redirect to (R14.4: stable IRIs)."""

import re

import pytest
from rdflib import OWL, RDF, Graph, URIRef

from aoc_dfo import BASE_IRI, REPO_ROOT, __version__
from aoc_dfo.modules import MODULES
from aoc_dfo.site import TERMS_DOC, build_site

HTACCESS = REPO_ROOT / "docs" / "w3id" / ".htaccess"
PAGES = "https://semanticarchitectures.github.io/aoc-dfo/"


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    out = tmp_path_factory.mktemp("site")
    build_site(out)
    return out


def test_root_and_version_have_every_document(site):
    docs = [TERMS_DOC] + [m.name for m in MODULES]
    for base in (site, site / __version__):
        missing = [d for d in docs if not (base / f"{d}.ttl").exists()]
        assert missing == [], f"{base}: {missing}"
        assert (base / "index.html").exists()
    assert (site / ".nojekyll").exists()


def test_terms_document_is_the_dfo_namespace_ontology(site):
    g = Graph().parse(site / f"{TERMS_DOC}.ttl", format="turtle")
    ont = URIRef(BASE_IRI + TERMS_DOC)
    assert (ont, RDF.type, OWL.Ontology) in g
    assert (ont, OWL.versionIRI, URIRef(f"{BASE_IRI}{__version__}/{TERMS_DOC}")) in g
    assert len(list(g.subjects(RDF.type, OWL.Ontology))) == 1  # module headers removed


def test_every_module_name_matches_the_w3id_pattern():
    assert all(re.fullmatch(r"aoc-[a-z]+", m.name) for m in MODULES)


def test_htaccess_targets_pages_over_https_only():
    targets = re.findall(r"\s(https?://\S+)\s\[", HTACCESS.read_text(encoding="utf-8"))
    assert targets and all(t.startswith(PAGES) for t in targets)


def test_htaccess_flags_are_well_formed():
    text = HTACCESS.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("RewriteRule"):
            assert re.search(r" \[[A-Z0-9=,]+\]$", line), line
    assert "R=301" not in text
