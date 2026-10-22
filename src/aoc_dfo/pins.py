"""Pinned upper ontologies (R6.1, R6.7) and the XML catalog that resolves imports (NFR-4)."""

from __future__ import annotations

import hashlib
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import yaml

from . import CATALOG_PATH, IMPORTS_DIR, ONTOLOGY_DIR, PINS_PATH

_CATALOG_NS = "{urn:oasis:names:tc:entity:xmlns:xml:catalog}"


@dataclass(frozen=True)
class Pin:
    name: str
    file: str
    commit: str
    sha256: str
    ontology_iri: str
    version_iri: str

    @property
    def path(self) -> Path:
        return IMPORTS_DIR / self.file


def load_pins(path: Path = PINS_PATH) -> list[Pin]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    fields = Pin.__dataclass_fields__
    return [Pin(**{k: v for k, v in p.items() if k in fields}) for p in data["pins"]]


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_pins(pins: list[Pin] | None = None) -> list[str]:
    """Return a list of problems; empty means every vendored file matches its pin."""
    problems = []
    for pin in pins or load_pins():
        if not pin.path.exists():
            problems.append(f"{pin.name}: missing {pin.path}")
        elif (actual := sha256_of(pin.path)) != pin.sha256:
            problems.append(f"{pin.name}: sha256 {actual} != pinned {pin.sha256}")
    return problems


def load_catalog(path: Path = CATALOG_PATH) -> dict[str, Path]:
    """Map each IRI in the XML catalog to the local file it resolves to."""
    root = ET.parse(path).getroot()
    return {
        el.get("name"): (path.parent / el.get("uri")).resolve()
        for el in root.iter(f"{_CATALOG_NS}uri")
    }


def resolve(iri: str, catalog: dict[str, Path] | None = None) -> Path:
    catalog = catalog if catalog is not None else load_catalog()
    try:
        return catalog[iri]
    except KeyError:
        raise KeyError(f"IRI not in catalog (would need the network): {iri}") from None


__all__ = ["Pin", "load_pins", "sha256_of", "verify_pins", "load_catalog", "resolve", "ONTOLOGY_DIR"]
