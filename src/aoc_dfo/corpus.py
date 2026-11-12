"""The ingested corpus, one interface over three kinds of source (R1.2, R5.4):

* **Text sources** (doctrine, manuals): ``corpus/text/<ID>/segments.jsonl``, one JSON object per
  anchored segment ``{"anchor", "kind", "page", "text"}``, written by an ingester (task 1.3).
* **Schema sources** (NIEM): the element tables in ``catalog/canonical/niem/``, anchored by
  qualified name.
* **AOC-DFO's design spec**: its numbered sections, anchored ``sec-<n>``.

A citation ``…/source/<ID>#<anchor>`` is valid only if ``<ID>`` is ingested here and ``<anchor>``
exists in it (task 1.6). Registered but un-ingested sources cannot be cited yet.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from . import REPO_ROOT, SPEC_DIR

TEXT_DIR = REPO_ROOT / "corpus" / "text"
NIEM_DIR = REPO_ROOT / "catalog" / "canonical" / "niem"
DESIGN_ID = "AOC-DFO-DES-1.1"
NIEM_ID = "NIEM-6.0"


@dataclass(frozen=True)
class Segment:
    source_id: str
    anchor: str
    kind: str
    text: str
    page: int | None = None


def _text_segments(source_id: str) -> list[Segment]:
    path = TEXT_DIR / source_id / "segments.jsonl"
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            d = json.loads(line)
            out.append(Segment(source_id, d["anchor"], d["kind"], d["text"], d.get("page")))
    return out


def _niem_segments() -> list[Segment]:
    out = []
    for table, kind in (("properties.csv", "niem-property"), ("types.csv", "niem-type"),
                        ("type-contains-property.csv", "niem-containment")):
        with (NIEM_DIR / table).open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                text = (r.get("definition") or
                        f'{r["type"]} contains {r["property"]} [{r["min_occurs"]}..{r["max_occurs"]}]')
                out.append(Segment(NIEM_ID, r["anchor"], kind, text))
    return out


def _design_segments() -> list[Segment]:
    md = (SPEC_DIR / "design.md").read_text(encoding="utf-8")
    parts = re.split(r"^(#{2,3} (\d+(?:\.\d+)?)\.? .*)$", md, flags=re.M)
    out = []
    # re.split with two groups yields [pre, heading, number, body, heading, number, body, ...]
    for i in range(1, len(parts) - 2, 3):
        out.append(Segment(DESIGN_ID, f"sec-{parts[i + 1]}", "section",
                           (parts[i] + parts[i + 2]).strip()))
    return out


@lru_cache(maxsize=None)
def segments(source_id: str) -> tuple[Segment, ...]:
    if source_id == NIEM_ID:
        return tuple(_niem_segments())
    if source_id == DESIGN_ID:
        return tuple(_design_segments())
    if (TEXT_DIR / source_id / "segments.jsonl").exists():
        return tuple(_text_segments(source_id))
    raise KeyError(f"{source_id} is not ingested")


def ingested_ids() -> list[str]:
    text = sorted(p.parent.name for p in TEXT_DIR.glob("*/segments.jsonl"))
    schema = [NIEM_ID] if (NIEM_DIR / "properties.csv").exists() else []
    return [DESIGN_ID, *schema, *text]


@lru_cache(maxsize=None)
def anchor_index(source_id: str) -> dict[str, Segment]:
    return {s.anchor: s for s in segments(source_id)}


def resolve(source_id: str, anchor: str) -> Segment:
    try:
        return anchor_index(source_id)[anchor]
    except KeyError:
        raise KeyError(f"no anchor {anchor!r} in {source_id}") from None


def search(query: str, source_id: str | None = None, limit: int = 20) -> list[Segment]:
    """Case-insensitive match of every query word; ranked by how often they occur."""
    words = [w.lower() for w in re.findall(r"\w+", query)]
    if not words:
        return []
    hits = []
    for sid in ([source_id] if source_id else ingested_ids()):
        for seg in segments(sid):
            low = (seg.anchor + " " + seg.text).lower()
            if all(w in low for w in words):
                hits.append((sum(low.count(w) for w in words), seg))
    hits.sort(key=lambda h: (-h[0], h[1].source_id, h[1].anchor))
    return [s for _, s in hits[:limit]]
