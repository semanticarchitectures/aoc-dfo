"""R12.2, R14.3, MR-6: the owl:imports graph matches design §8, and nothing imports aoc-align."""

import pytest

from aoc_dfo import ONTOLOGY_DIR
from aoc_dfo.modules import BY_NAME, MODULES, actual_imports, expected_imports


@pytest.mark.parametrize("module", MODULES, ids=lambda m: m.name)
def test_module_imports_match_contract(module):
    assert module.path.exists(), f"missing {module.path.name}; run `uv run aoc-dfo headers`"
    assert actual_imports(module.path) == expected_imports(module)


def test_no_module_imports_align():
    align = BY_NAME["aoc-align"].iri
    importers = [m.name for m in MODULES if align in actual_imports(m.path)]
    assert importers == []


def test_top_level_imports_every_core_module():
    top = BY_NAME["aoc-dfo"]
    core = {m.iri for m in MODULES if m.in_top and m.name != "aoc-dfo"}
    assert core <= actual_imports(top.path)


def test_domain_and_doctrine_never_import_msgstruct():
    msgstruct = BY_NAME["aoc-msgstruct"].iri
    for name in ("aoc-domain", "aoc-doctrine"):
        assert msgstruct not in actual_imports(BY_NAME[name].path)


def test_no_unexpected_ontology_files():
    on_disk = {p.stem for p in ONTOLOGY_DIR.glob("*.ttl")}
    assert on_disk == {m.name for m in MODULES}
