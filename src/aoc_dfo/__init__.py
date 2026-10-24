"""AOC-DFO: BFO/CCO ontology of USAF Air Operations Center data flows.

Build, pin and validation tooling. The ontology itself lives in ``ontology/``.
Spec: ``.kiro/specs/aoc-dfo/`` (v1.1, Amendment 001).
"""

from pathlib import Path

__version__ = "0.1.0"

#: Base IRI for every AOC-DFO term and module (chosen 2026-10-24). Resolved by w3id.org rules in
#: docs/w3id/.htaccess, which redirect to the GitHub Pages site built by `aoc-dfo site`. Besides this
#: constant, only ontology/catalog-v001.xml repeats it, and a test checks the two agree.
BASE_IRI = "https://w3id.org/aoc-dfo/"

#: Namespace for classes and properties (``dfo:``).
DFO_NS = BASE_IRI + "ontology#"

REPO_ROOT = Path(__file__).resolve().parents[2]
ONTOLOGY_DIR = REPO_ROOT / "ontology"
IMPORTS_DIR = ONTOLOGY_DIR / "imports"
CATALOG_PATH = ONTOLOGY_DIR / "catalog-v001.xml"
PINS_PATH = IMPORTS_DIR / "PINS.yaml"
SPEC_DIR = REPO_ROOT / ".kiro" / "specs" / "aoc-dfo"
REGISTRY_PATH = REPO_ROOT / "corpus" / "registry.yaml"
