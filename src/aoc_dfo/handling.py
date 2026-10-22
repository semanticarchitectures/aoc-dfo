"""Handling-marking scan (NFR-3, R12.5).

A cheap tripwire, not a classification review: it catches banner or portion markings and
restrictive distribution statements pasted in from controlled documents. Prose that merely
mentions "CUI" (as HANDLING.md does) is not flagged.
"""

from __future__ import annotations

import re
from pathlib import Path

from . import REPO_ROOT

PATTERNS = {
    "banner marking": re.compile(
        r"^\s*(TOP SECRET|SECRET|CONFIDENTIAL|CUI)(//[A-Z0-9 ,/\-]+)?\s*$", re.MULTILINE),
    "portion marking": re.compile(r"\((TS|S|C|CUI|U//FOUO|FOUO)(//[A-Z0-9 ,\-]+)?\)\s+\S"),
    "FOUO caveat": re.compile(r"FOR OFFICIAL USE ONLY"),
    "restrictive distribution statement": re.compile(r"DISTRIBUTION STATEMENT [B-F]\b"),
    "dissemination control": re.compile(r"//\s*(NOFORN|NF|REL TO|ORCON|PROPIN)\b"),
}

SKIP_DIRS = {".git", ".venv", "node_modules", "imports", "__pycache__", ".pytest_cache",
             "reports", "build"}
TEXT_SUFFIXES = {".md", ".ttl", ".yaml", ".yml", ".csv", ".rq", ".py", ".xml", ".txt", ".toml"}
# Files that must name the patterns in order to describe them.
SELF = {Path(__file__).resolve(), (REPO_ROOT / "tests" / "test_handling.py").resolve()}


def scan(root: Path = REPO_ROOT) -> list[str]:
    hits = []
    for path in sorted(root.rglob("*")):
        if (not path.is_file() or path.suffix not in TEXT_SUFFIXES
                or SKIP_DIRS.intersection(path.relative_to(root).parts)
                or path.resolve() in SELF):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for name, pat in PATTERNS.items():
            for m in pat.finditer(text):
                line = text.count("\n", 0, m.start()) + 1
                hits.append(f"{path.relative_to(root)}:{line}: {name}: {m.group(0).strip()[:60]}")
    return hits
