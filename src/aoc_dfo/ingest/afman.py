"""AFMAN 13-1AOC Volume 3 (25 Jun 2024) as anchored text segments (task 1.3, R1.4).

Source: the e-Publishing PDF, registered as ``AFMAN-13-1AOCV3``. "There are no releasability
restrictions on this publication" (title page). The PDF is not committed (``corpus/raw/`` is
gitignored); its SHA-256 is pinned below and in the registry, and the segments are committed.

Anchors, cited as ``https://w3id.org/aoc-dfo/source/AFMAN-13-1AOCV3#<anchor>``:

=================  ==============================================  ============
anchor             what                                            kind
=================  ==============================================  ============
``front``          title page, summary of changes                  front-matter
``chap-2``         chapter heading                                 heading
``para-2.3.1``     numbered paragraph, the manual's own number     paragraph
``fig-2.1``        figure caption and any text in the figure       figure
``att1-refs``      Attachment 1 references (one segment)           reference-list
``att1-forms``     Attachment 1 prescribed and adopted forms       reference-list
``abbr-JAOC``      Attachment 1 abbreviation or acronym            abbreviation
``term-Cyberspace``  Attachment 1 term and its definition          term
=================  ==============================================  ============

Text is what ``pdftotext -layout`` extracts, with running headers removed and lines joined. It is
not corrected: the PDF's own glitches (e.g. "Genera2l") are kept so a quotation matches the source.
Most figures are images; their text is not extracted here (see MANIFEST ``figures_without_text``).
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import urllib.request
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

import yaml

from .. import REPO_ROOT

SOURCE_ID = "AFMAN-13-1AOCV3"
URL = ("https://static.e-publishing.af.mil/production/1/af_a3/publication/"
       "afman13-1aocv3/afman13-1aocv3_.pdf")
SHA256 = "d96d11dc35eb6ca66b3bbafeef472a25e504b2d022a71ee745cb86ebbc0f99a3"
RAW_PATH = REPO_ROOT / "corpus" / "raw" / SOURCE_ID / "afman13-1aocv3_.pdf"
OUT_DIR = REPO_ROOT / "corpus" / "text" / SOURCE_ID

RUNNING_HEADER = re.compile(r"^\s*(\d+\s+)?AFMAN13-1AOCV3\s+25 JUNE 2024(\s+\d+)?\s*$")
PARA = re.compile(r"^\s*(\d+(?:\.\d+)+)\.\s+(.*)$")
FIGURE = re.compile(r"^\s*Figure (\d+)\.(\d+)\.\s*(.*)$")
TOC_START = re.compile(r"^\s*Chapter 1—")   # first table-of-contents entry
CHAPTER = re.compile(r"^\s*Chapter (\d+)\s*$")
ATTACHMENT = re.compile(r"^\s*Attachment (\d+)\s*$")
GLOSS_ENTRY = re.compile(r"^([^\s—][^—]{0,90}?)\s*—\s*(.+)$")
ATT1_SECTIONS = {"References": "refs", "Prescribed Forms": "forms", "Adopted Forms": "forms",
                 "Abbreviations and Acronyms": "abbr", "Terms": "term"}


@dataclass
class Seg:
    anchor: str
    kind: str
    page: int
    text: str


class FetchError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch(dest: Path = RAW_PATH) -> Path:
    """Return the pinned PDF, downloading it if absent. e-Publishing refuses most non-browser
    clients; if the download fails, save the file from a browser to ``dest``."""
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/pdf"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                dest.write_bytes(r.read())
        except OSError as e:
            raise FetchError(f"could not download {URL} ({e}); save it from a browser to {dest}") from e
    got = sha256(dest)
    if got != SHA256:
        raise FetchError(f"{dest}: SHA-256 {got} is not the pinned {SHA256}")
    return dest


def pdftotext_version() -> str:
    out = subprocess.run(["pdftotext", "-v"], capture_output=True, text=True)
    return (out.stderr or out.stdout).splitlines()[0].strip()


def pages(pdf: Path) -> list[list[str]]:
    """Lines of each page, running headers removed."""
    text = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", str(pdf), "-"],
                          capture_output=True, text=True, check=True).stdout
    raw = text.split("\f")
    if raw and not raw[-1].strip():
        raw.pop()
    return [[ln for ln in p.splitlines() if not RUNNING_HEADER.match(ln)] for p in raw]


def _next_ok(prev: tuple[int, ...], cand: tuple[int, ...]) -> bool:
    """A paragraph number can follow ``prev`` only as its first child or as the next sibling of
    ``prev`` or of one of its ancestors. This rejects cross-references that wrap onto a new line."""
    if cand == prev + (1,):
        return True
    for k in range(1, len(prev) + 1):
        if cand == prev[:k - 1] + (prev[k - 1] + 1,):
            return True
    return False


def _join(lines: list[str]) -> str:
    return re.sub(r"\s+", " ", " ".join(ln.strip() for ln in lines)).strip()


def _slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9.\-]+", "-", s).strip("-")


def segment(page_lines: list[list[str]]) -> tuple[list[Seg], dict]:
    segs: list[Seg] = []
    buf: list[str] = []
    cur: Seg | None = None
    notes = {"rejected_paragraph_numbers": [], "figures_without_text": []}

    def flush():
        nonlocal cur, buf
        if cur is not None:
            body = _join(buf)
            cur.text = (cur.text + " " + body).strip() if cur.text else body
            segs.append(cur)
        cur, buf = None, []

    def start(seg: Seg, first: str = ""):
        nonlocal cur, buf
        flush()
        cur, buf = seg, ([first] if first else [])

    state = "front"
    para: tuple[int, ...] = (0,)
    last_fig = (0, 0)
    pending_heading: tuple[str, int, str] | None = None   # (kind, number, anchor) awaiting title
    att1 = None
    used: set[str] = set()

    def unique(anchor: str) -> str:
        n, a = 2, anchor
        while a in used:
            a, n = f"{anchor}-{n}", n + 1
        used.add(a)
        return a

    start(Seg(unique("front"), "front-matter", 1, ""))
    for pno, lines in enumerate(page_lines, start=1):
        for ln in lines:
            s = ln.strip()
            if state == "front" and TOC_START.match(ln):
                flush()
                state = "toc"
                continue
            if state in ("front", "toc", "body") and (m := CHAPTER.match(ln)):
                if state == "toc" and m.group(1) != "1":
                    continue
                state = "body"
                n = int(m.group(1))
                para = (n,)
                start(Seg(unique(f"chap-{n}"), "heading", pno, f"Chapter {n}"))
                pending_heading = ("chap", n, "")
                continue
            if state == "toc":
                continue
            if state == "body" and ATTACHMENT.match(ln):
                state = "att"
                start(Seg(unique(f"att-{ATTACHMENT.match(ln).group(1)}"), "heading", pno, s))
                pending_heading = ("att", 0, "")
                continue
            if pending_heading and s:
                cur.text = f"{cur.text} — {s}"
                pending_heading = None
                flush()
                continue
            if state == "front":
                buf.append(ln)
                continue
            if state == "body":
                if (m := PARA.match(ln)):
                    num = tuple(int(x) for x in m.group(1).split("."))
                    if _next_ok(para, num):
                        para = num
                        start(Seg(unique("para-" + m.group(1)), "paragraph", pno, ""), m.group(0).strip())
                        continue
                    notes["rejected_paragraph_numbers"].append(f"p{pno}: {m.group(1)}")
                if (m := FIGURE.match(ln)):
                    fig = (int(m.group(1)), int(m.group(2)))
                    title = m.group(3)
                    # "(See\nFigure 4.1. CPD Organization ...)." is a reference, not the caption
                    if fig > last_fig and title.count(")") <= title.count("("):
                        last_fig = fig
                        start(Seg(unique(f"fig-{fig[0]}.{fig[1]}"), "figure", pno, ""), s)
                        continue
                if cur is None:   # text after a figure caption with no paragraph yet
                    continue
                buf.append(ln)
                continue
            # Attachment 1
            if s in ATT1_SECTIONS:
                att1 = ATT1_SECTIONS[s]
                if att1 in ("refs", "forms"):
                    if att1 == "forms" and cur is not None and cur.anchor == "att1-forms":
                        buf.append(s)
                    else:
                        start(Seg(unique(f"att1-{att1}"), "reference-list", pno, ""), s)
                else:
                    flush()
                continue
            if att1 in ("abbr", "term") and (m := GLOSS_ENTRY.match(s)) and not ln.startswith(" "):
                kind = "abbreviation" if att1 == "abbr" else "term"
                start(Seg(unique(f"{att1}-{_slug(m.group(1))}"), kind, pno, ""), s)
                continue
            if cur is not None and s:
                buf.append(ln)
    flush()

    for sg in segs:
        if sg.kind == "figure" and re.fullmatch(r"Figure \d+\.\d+\.[^.]*\.?", sg.text):
            notes["figures_without_text"].append(sg.anchor)
    return [s for s in segs if s.text], notes


def build(pdf: Path, out: Path = OUT_DIR) -> dict:
    segs, notes = segment(pages(pdf))
    out.mkdir(parents=True, exist_ok=True)
    with (out / "segments.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for s in segs:
            f.write(json.dumps(asdict(s), ensure_ascii=False, sort_keys=True) + "\n")
    counts: dict[str, int] = {}
    for s in segs:
        counts[s.kind] = counts.get(s.kind, 0) + 1
    manifest = {
        "source_id": SOURCE_ID,
        "url": URL,
        "sha256": sha256(pdf),
        "extractor": f"{pdftotext_version()} -layout",
        "built": date.today().isoformat(),
        "counts": dict(sorted(counts.items())),
        **notes,
    }
    (out / "MANIFEST.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True),
                                       encoding="utf-8")
    return manifest
