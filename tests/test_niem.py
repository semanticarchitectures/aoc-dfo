"""Task 1.4 (R5.1, R5.2, R1.2): NIEM 6.0 element tables are pinned, complete and anchored."""

import csv
import hashlib

import pytest
import yaml

from aoc_dfo.ingest import niem
from aoc_dfo.registry import load_registry

MANIFEST = yaml.safe_load((niem.OUT_DIR / "MANIFEST.yaml").read_text(encoding="utf-8"))
TABLES = ("properties.csv", "types.csv", "type-contains-property.csv")


def rows(name):
    with (niem.OUT_DIR / name).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


@pytest.mark.parametrize("name", TABLES)
def test_committed_table_matches_manifest_hash(name):
    data = (niem.OUT_DIR / name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == MANIFEST["outputs_sha256"][name]


def test_manifest_pins_the_code_constants():
    assert (MANIFEST["commit"], MANIFEST["tag"]) == (niem.COMMIT, niem.TAG)
    assert set(MANIFEST["namespaces"]) == set(niem.NAMESPACES)


def test_registry_entry_matches_manifest():
    entry = next(s for s in load_registry()["sources"] if s["id"] == niem.SOURCE_ID)
    assert entry["status"] == "verified" and entry["tier"] == "1a"
    assert niem.COMMIT in entry["url"] and "PS02" in entry["edition"]


@pytest.mark.parametrize("name,key", [("properties.csv", "qname"), ("types.csv", "qname")])
def test_every_row_is_defined_and_anchored(name, key):
    data = rows(name)
    assert len(data) == MANIFEST["row_counts"][name.removesuffix(".csv")]
    assert all(r["definition"] for r in data), "NIEM defines every mo/usmtf component"
    assert all(r["anchor"] == r[key] for r in data)
    assert len({r["anchor"] for r in data}) == len(data), "anchors are unique"
    assert {r["namespace"] for r in data} == set(niem.NAMESPACES)


def test_containment_rows_reference_known_types_and_anchor_uniquely():
    types = {r["qname"] for r in rows("types.csv")}
    data = rows("type-contains-property.csv")
    assert all(r["type"] in types for r in data)
    assert len({r["anchor"] for r in data}) == len(data)


def test_usmtf_subdomain_is_present():
    """The finding behind Amendment 002: public, field-level USMTF vocabulary."""
    usmtf = [r for r in rows("properties.csv") if r["namespace"] == "usmtf"]
    assert len(usmtf) > 5000
    assert any(r["qname"] == "usmtf:AirTaskingOrderNumber" or "AirTaskingOrderNumber" in r["type"]
               for r in usmtf)


@pytest.mark.skipif(not (niem.CACHE_DIR / "csv" / "Property.csv").exists(),
                    reason="NIEM cache absent; run `uv run aoc-dfo ingest niem` to check reproduction")
def test_tables_reproduce_from_the_pinned_inputs(tmp_path):
    for rel, digest in MANIFEST["inputs_sha256"].items():
        assert hashlib.sha256((niem.CACHE_DIR / rel).read_bytes()).hexdigest() == digest
    m = niem.build(niem.CACHE_DIR / "csv", out=tmp_path, retrieved=MANIFEST["retrieved"])
    for name in TABLES:
        assert m["outputs_sha256"][name] == MANIFEST["outputs_sha256"][name]
