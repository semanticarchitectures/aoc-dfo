"""Command line: ``uv run aoc-dfo <command>``."""

from __future__ import annotations

import argparse
import sys

from . import ONTOLOGY_DIR, REPO_ROOT
from .canonical import canonical_turtle, canonicalize_file
from .handling import scan
from .labelmap import render_markdown, resolve_tokens, spec_tokens
from .modules import MODULES, header_graph
from .pins import verify_pins
from .registry import check_registry

LABEL_MAP = REPO_ROOT / "docs" / "cco-label-map.md"


def cmd_headers(args: argparse.Namespace) -> int:
    """Write generated headers for modules that have no content yet (or all, with --force)."""
    for m in MODULES:
        if m.path.exists() and not args.force:
            print(f"skip {m.path.name} (exists; use --force to regenerate)")
            continue
        m.path.write_text(canonical_turtle(header_graph(m)), encoding="utf-8")
        print(f"wrote {m.path.relative_to(REPO_ROOT)}")
    return 0


def cmd_fmt(args: argparse.Namespace) -> int:
    for path in sorted(ONTOLOGY_DIR.glob("*.ttl")):
        path.write_text(canonicalize_file(path), encoding="utf-8")
    return 0


def cmd_labelmap(args: argparse.Namespace) -> int:
    found, missing = resolve_tokens(spec_tokens())
    LABEL_MAP.write_text(render_markdown(found), encoding="utf-8")
    print(f"wrote {LABEL_MAP.relative_to(REPO_ROOT)} ({len(found)} terms)")
    for m in missing:
        print(f"UNRESOLVED {m}", file=sys.stderr)
    return 1 if missing else 0


def cmd_check(args: argparse.Namespace) -> int:
    """Fast checks without pytest: pins, registry, handling."""
    problems = verify_pins() + check_registry() + scan()
    for p in problems:
        print(p, file=sys.stderr)
    print("ok" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


def cmd_prov(args: argparse.Namespace) -> int:
    """Regenerate ontology/aoc-prov.ttl and provenance/sources.trig from code and registry."""
    from .modules import BY_NAME
    from .provenance import vocab_graph, write_sources

    m = BY_NAME["aoc-prov"]
    g = header_graph(m) + vocab_graph()
    for prefix, ns in vocab_graph().namespaces():
        g.bind(prefix, ns)
    m.path.write_text(canonical_turtle(g), encoding="utf-8")
    print(f"wrote {m.path.relative_to(REPO_ROOT)}")
    print(f"wrote {write_sources().relative_to(REPO_ROOT)}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    from .validate import data_graph, run_shapes

    conforms, _, text = run_shapes(data_graph())
    print(text if not conforms else "provenance shapes: conforms")
    return 0 if conforms else 1


def cmd_citations(args: argparse.Namespace) -> int:
    from .citations import catalog_citations, check, rdf_citations

    cites = rdf_citations() + catalog_citations()
    problems = check(cites)
    for p in problems:
        print(p, file=sys.stderr)
    print(f"{len(cites)} citations, {len(problems)} unresolved")
    return 1 if problems else 0


def cmd_ingest(args: argparse.Namespace) -> int:
    if args.source == "niem":
        from .ingest import niem

        m = niem.build(niem.fetch())
        print(f"NIEM {m['tag']} @ {m['commit'][:12]}: {m['row_counts']}")
    elif args.source == "afman-v3":
        from .ingest import afman

        m = afman.build(afman.fetch())
        print(f"{m['source_id']}: {m['counts']}")
    return 0


def cmd_site(args: argparse.Namespace) -> int:
    from pathlib import Path

    from .site import build_site

    versions = build_site(Path(args.out))
    print(f"built {args.out} (versions: {', '.join(versions)})")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aoc-dfo")
    sub = parser.add_subparsers(dest="command", required=True)
    h = sub.add_parser("headers", help="generate ontology module headers")
    h.add_argument("--force", action="store_true")
    h.set_defaults(func=cmd_headers)
    sub.add_parser("fmt", help="rewrite ontology/*.ttl in canonical Turtle").set_defaults(func=cmd_fmt)
    sub.add_parser("labelmap", help="regenerate docs/cco-label-map.md").set_defaults(func=cmd_labelmap)
    sub.add_parser("check", help="pins, registry and handling checks").set_defaults(func=cmd_check)
    sub.add_parser("prov", help="regenerate aoc-prov.ttl and provenance/sources.trig").set_defaults(func=cmd_prov)
    sub.add_parser("validate", help="run SHACL provenance shapes").set_defaults(func=cmd_validate)
    sub.add_parser("citations", help="check every citation resolves to an ingested anchor").set_defaults(func=cmd_citations)
    i = sub.add_parser("ingest", help="ingest a registered source into anchored text or tables")
    i.add_argument("source", choices=["niem", "afman-v3"])
    i.set_defaults(func=cmd_ingest)
    s = sub.add_parser("site", help="build the GitHub Pages site that w3id IRIs redirect to")
    s.add_argument("--out", default="site")
    s.set_defaults(func=cmd_site)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
