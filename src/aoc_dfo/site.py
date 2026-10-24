"""Static site for GitHub Pages: the documents that w3id.org/aoc-dfo/ IRIs redirect to.

Layout (mirrors docs/w3id/.htaccess):

    index.html                 human-readable landing page
    ontology.ttl               every AOC-DFO term (dfo: hash namespace), current main
    <module>.ttl               each module, current main
    <version>/ontology.ttl     the same, per release (from git tags vX.Y.Z, plus the
    <version>/<module>.ttl     working-tree version while it is untagged)
    <version>/index.html

Only AOC-DFO modules are published. BFO and CCO are referenced by their own IRIs, never
re-hosted here.
"""

from __future__ import annotations

import html
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from rdflib import OWL, RDF, RDFS, Graph, Literal, URIRef
from rdflib.namespace import DCTERMS

from . import BASE_IRI, ONTOLOGY_DIR, REPO_ROOT, __version__
from .canonical import canonical_turtle
from .modules import MODULES, upper_import_iris

TERMS_DOC = "ontology"  # https://w3id.org/aoc-dfo/ontology#Term
VERSION_TAG = re.compile(r"^v(\d+\.\d+\.\d+)$")


def merged_terms(module_dir: Path, version: str) -> Graph:
    """Union of every module's axioms, under one ontology header for the dfo: namespace."""
    g = Graph()
    for m in MODULES:
        path = module_dir / f"{m.name}.ttl"
        if not path.exists():
            continue
        part = Graph().parse(path, format="turtle")
        for ont in list(part.subjects(RDF.type, OWL.Ontology)):
            part.remove((ont, None, None))
        g += part
    ont = URIRef(BASE_IRI + TERMS_DOC)
    g.bind("owl", OWL)
    g.bind("dcterms", DCTERMS)
    g.add((ont, RDF.type, OWL.Ontology))
    g.add((ont, OWL.versionIRI, URIRef(f"{BASE_IRI}{version}/{TERMS_DOC}")))
    g.add((ont, OWL.versionInfo, Literal(version)))
    g.add((ont, RDFS.label, Literal("AOC Data Flow Ontology — all terms", lang="en")))
    g.add((ont, DCTERMS.source, URIRef("https://github.com/semanticarchitectures/aoc-dfo")))
    g.add((ont, DCTERMS.license, URIRef("https://www.apache.org/licenses/LICENSE-2.0")))
    for iri in upper_import_iris().values():
        g.add((ont, OWL.imports, iri))
    return g


def _index_html(version: str, versions: list[str], prefix: str) -> str:
    rows = "\n".join(
        f'<tr><td><code>{BASE_IRI}{prefix}{m.name}</code></td>'
        f'<td><a href="{m.name}.ttl">{m.name}.ttl</a></td><td>{html.escape(m.title)}</td></tr>'
        for m in MODULES
    )
    vlist = ", ".join(f'<a href="{v}/">{v}</a>' for v in versions) or "none yet"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AOC-DFO {html.escape(version)}</title>
<style>body{{font:16px/1.5 system-ui,sans-serif;max-width:56rem;margin:2rem auto;padding:0 1rem}}
table{{border-collapse:collapse}}td,th{{border-bottom:1px solid #ddd;padding:.3rem .6rem;text-align:left}}
code{{font-size:.9em}}</style></head><body>
<h1>AOC-DFO — AOC Data Flow Ontology</h1>
<p>A BFO/CCO ontology of the data flows into, out of and within a USAF Air Operations Center,
built only from public sources. Part of the
<a href="https://github.com/semanticarchitectures/acquisition-knowledge-system">Acquisition Knowledge System</a>.
Source and spec: <a href="https://github.com/semanticarchitectures/aoc-dfo">github.com/semanticarchitectures/aoc-dfo</a>.</p>
<p>Version shown: <strong>{html.escape(version)}</strong>. Releases: {vlist}.</p>
<h2>Documents</h2>
<p>All terms (namespace <code>{BASE_IRI}ontology#</code>):
<a href="{TERMS_DOC}.ttl">{TERMS_DOC}.ttl</a></p>
<table><tr><th>IRI</th><th>Turtle</th><th>Module</th></tr>
{rows}
</table>
<p>Upper ontologies (not hosted here): BFO 2020 release-2024-01-29; CCO v2.2.</p>
<p>Public, unclassified content only.</p>
</body></html>
"""


def _write_version(src: Path, out: Path, version: str, versions: list[str], prefix: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for m in MODULES:
        p = src / f"{m.name}.ttl"
        if p.exists():
            shutil.copyfile(p, out / p.name)
    (out / f"{TERMS_DOC}.ttl").write_text(
        canonical_turtle(merged_terms(src, version)), encoding="utf-8")
    (out / "index.html").write_text(_index_html(version, versions, prefix), encoding="utf-8")


def release_tags(repo: Path = REPO_ROOT) -> list[tuple[str, str]]:
    """(version, tag) for every vX.Y.Z tag, oldest first."""
    out = subprocess.run(["git", "-C", str(repo), "tag", "--list", "v*"],
                         capture_output=True, text=True, check=False).stdout.split()
    tags = [(m.group(1), t) for t in out if (m := VERSION_TAG.match(t))]
    return sorted(tags, key=lambda vt: tuple(int(x) for x in vt[0].split(".")))


def build_site(out: Path, repo: Path = REPO_ROOT) -> list[str]:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    tags = release_tags(repo)
    versions = [v for v, _ in tags]
    if __version__ not in versions:
        versions.append(__version__)
    for version, tag in tags:
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(
                f"git -C {repo} archive {tag} ontology | tar -x -C {tmp}",
                shell=True, check=True)
            _write_version(Path(tmp) / "ontology", out / version, version, versions,
                           f"{version}/")
    if __version__ not in dict(tags):
        _write_version(ONTOLOGY_DIR, out / __version__, __version__, versions,
                       f"{__version__}/")
    _write_version(ONTOLOGY_DIR, out, __version__, versions, "")  # current main at the root
    (out / ".nojekyll").write_text("", encoding="utf-8")
    return versions
