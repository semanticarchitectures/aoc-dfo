"""NIEM 6.0 element tables (task 1.4, R5.1): Military Operations (`mo`) and its USMTF
subdomain (`usmtf`), from the CSV distribution in the official OASIS NIEMOpen repository.

Source: https://github.com/niemopen/niem-model at the pinned commit (tag 6.0-ps02). NIEM is
CC BY 4.0; both namespaces are marked "Distribution A" (approved for public release).

Every row carries its anchor: the qualified name (e.g. ``usmtf:AirTaskingOrderNumberType``),
cited as ``https://w3id.org/aoc-dfo/source/NIEM-6.0#usmtf:AirTaskingOrderNumberType``.
"""

from __future__ import annotations

import csv
import hashlib
import io
import subprocess
from datetime import date
from pathlib import Path

import yaml

from .. import REPO_ROOT

REPO = "https://github.com/niemopen/niem-model.git"
TAG = "6.0-ps02"
COMMIT = "d6e74ac2edf30f5096973c25dbf3c13555466582"
NAMESPACES = ("mo", "usmtf")
SOURCE_ID = "NIEM-6.0"
OUT_DIR = REPO_ROOT / "catalog" / "canonical" / "niem"
# Code-list values (23k rows, 3.5 MB) are rebuilt on demand from the pin, not committed.
FACETS_PATH = REPO_ROOT / "corpus" / "cache" / "niem-facets.csv"
CACHE_DIR = REPO_ROOT / "corpus" / "cache" / "niem-model"
INPUTS = ("Namespace", "Property", "Type", "TypeContainsProperty", "Facet")


def fetch(cache: Path = CACHE_DIR) -> Path:
    """Shallow-fetch the pinned commit's csv/ directory into the cache (gitignored)."""
    if not (cache / ".git").exists():
        cache.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "init", "-q", str(cache)], check=True)
        subprocess.run(["git", "-C", str(cache), "remote", "add", "origin", REPO], check=True)
    subprocess.run(["git", "-C", str(cache), "fetch", "-q", "--depth", "1", "origin", COMMIT],
                   check=True)
    subprocess.run(["git", "-C", str(cache), "checkout", "-q", COMMIT, "--", "csv"], check=True)
    return cache / "csv"


def _rows(text: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(text)))


def _write(path: Path, header: list[str], rows: list[list]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    data = buf.getvalue()
    path.write_text(data, encoding="utf-8")
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def build(csv_dir: Path, out: Path = OUT_DIR, retrieved: str | None = None) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    raw = {name: (csv_dir / f"{name}.csv").read_bytes() for name in INPUTS}
    text = {name: data.decode("utf-8") for name, data in raw.items()}
    ns = {r["NamespacePrefix"]: r for r in _rows(text["Namespace"]) if r["NamespacePrefix"] in NAMESPACES}
    keep = set(NAMESPACES)

    props = sorted(
        ([r["QualifiedProperty"], r["PropertyNamespacePrefix"], r["PropertyName"],
          "element" if r["IsElement"] == "1" else "attribute", r["IsAbstract"],
          r["QualifiedType"], r["SubstitutionGroupQualifiedProperty"], r["Definition"].strip(),
          r["QualifiedProperty"]]
         for r in _rows(text["Property"]) if r["PropertyNamespacePrefix"] in keep),
        key=lambda r: r[0])
    types = sorted(
        ([r["QualifiedType"], r["TypeNamespacePrefix"], r["TypeName"], r["ContentStyle"],
          r["SimpleStyle"], r["ParentQualifiedType"], r["SimpleQualifiedType"],
          r["Definition"].strip(), r["QualifiedType"]]
         for r in _rows(text["Type"]) if r["TypeNamespacePrefix"] in keep),
        key=lambda r: r[0])
    contains = sorted(
        ([r["QualifiedType"], r["QualifiedProperty"], r["MinOccurs"], r["MaxOccurs"],
          f'{r["QualifiedType"]}/{r["QualifiedProperty"]}']
         for r in _rows(text["TypeContainsProperty"]) if r["TypeNamespacePrefix"] in keep),
        key=lambda r: (r[0], r[1]))
    facets = sorted(
        ([r["QualifiedType"], r["FacetName"], r["FacetValue"], r["Definition"].strip(),
          f'{r["QualifiedType"]}/{r["FacetName"]}={r["FacetValue"]}']
         for r in _rows(text["Facet"]) if r["TypeNamespacePrefix"] in keep),
        key=lambda r: (r[0], r[1], r[2]))

    hashes = {
        "properties.csv": _write(out / "properties.csv",
            ["qname", "namespace", "name", "kind", "abstract", "type", "substitution_group",
             "definition", "anchor"], props),
        "types.csv": _write(out / "types.csv",
            ["qname", "namespace", "name", "content_style", "simple_style", "parent_type",
             "simple_type", "definition", "anchor"], types),
        "type-contains-property.csv": _write(out / "type-contains-property.csv",
            ["type", "property", "min_occurs", "max_occurs", "anchor"], contains),
        "facets.csv (cache only)": _write(FACETS_PATH if out == OUT_DIR else out / "facets.csv",
            ["type", "facet", "value", "definition", "anchor"], facets),
    }
    manifest = {
        "source_id": SOURCE_ID,
        "repository": REPO.removesuffix(".git"),
        "tag": TAG,
        "commit": COMMIT,
        "retrieved": retrieved or date.today().isoformat(),
        "license": "CC BY 4.0 (NIEMOpen); namespaces marked Distribution A",
        "namespaces": {p: {"uri": ns[p]["VersionURI"], "definition": ns[p]["Definition"]}
                       for p in NAMESPACES},
        "inputs_sha256": {f"csv/{n}.csv": hashlib.sha256(raw[n]).hexdigest() for n in INPUTS},
        "outputs_sha256": hashes,
        "row_counts": {"properties": len(props), "types": len(types),
                       "type-contains-property": len(contains), "facets": len(facets)},
        "anchor_form": "https://w3id.org/aoc-dfo/source/NIEM-6.0#<anchor column>",
    }
    (out / "MANIFEST.yaml").write_text(
        "# Generated by `uv run aoc-dfo ingest niem`. Do not edit.\n"
        + yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return manifest
