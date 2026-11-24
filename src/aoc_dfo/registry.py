"""Corpus registry checks (R1.1, R1.3, R1.6; OD-1)."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

import yaml

from . import REGISTRY_PATH

TIERS = {"1a", "1b", "2"}
STATUSES = {"verified", "verify-date", "verify-availability", "superseded", "unavailable"}
# R1.6: official government or standards-body hosts. Other hosts need an amendment (A003).
OFFICIAL_SUFFIXES = (".mil", ".gov", ".nato.int")
OFFICIAL_PREFIXES = (
    "https://github.com/niemopen/",            # NIEMOpen (OASIS), the NIEM standards body
    "https://github.com/semanticarchitectures/",  # this project's own approved specs
    "https://www.mimworld.org/",                # MIP, publisher of the MIM
    "https://edocs.nps.edu/",                   # Naval Postgraduate School (DoD); not all .edu is official
)
ARCHIVE_ALLOWED = {"JP-3-30-2019"}
REQUIRED = ("id", "title", "issuer", "edition", "tier", "status", "url", "role")


def load_registry(path: Path = REGISTRY_PATH) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def check_registry(data: dict | None = None) -> list[str]:
    data = data if data is not None else load_registry()
    problems: list[str] = []
    sources = data.get("sources") or []
    ids = [s.get("id") for s in sources]
    problems += [f"duplicate id: {i}" for i in sorted({i for i in ids if ids.count(i) > 1})]
    known = set(ids)
    for s in sources:
        sid = s.get("id", "<no id>")
        problems += [f"{sid}: missing field '{k}'" for k in REQUIRED if k not in s]
        tier, status = str(s.get("tier")), s.get("status")
        if tier not in TIERS:
            problems.append(f"{sid}: tier {tier!r} not in {sorted(TIERS)}")
        if status not in STATUSES:
            problems.append(f"{sid}: status {status!r} not in {sorted(STATUSES)}")
        # OD-1 (Amendment 001): no CAC access, so nothing in tier 1b or 2 is available.
        if tier in {"1b", "2"} and status != "unavailable":
            problems.append(f"{sid}: tier {tier} must be 'unavailable' under OD-1 (public only)")
        if status in {"verified", "superseded"} and not s.get("url"):
            problems.append(f"{sid}: status {status} needs a url")
        # Amendment 003: a non-official host only with archive: true, and only for JP-3-30-2019.
        url = s.get("url") or ""
        host = urlparse(url).hostname or ""
        official = host.endswith(OFFICIAL_SUFFIXES) or url.startswith(OFFICIAL_PREFIXES)
        if s.get("url") and not official and not s.get("archive"):
            problems.append(f"{sid}: {host} is not an official host; R1.6 needs archive: true and an amendment")
        if s.get("archive") and sid not in ARCHIVE_ALLOWED:
            problems.append(f"{sid}: archive copies are allowed only for {sorted(ARCHIVE_ALLOWED)} (A003)")
        if (sup := s.get("superseded_by")) and sup not in known:
            problems.append(f"{sid}: superseded_by {sup} is not a registered id")
    return problems
