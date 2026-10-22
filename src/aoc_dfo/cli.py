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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aoc-dfo")
    sub = parser.add_subparsers(dest="command", required=True)
    h = sub.add_parser("headers", help="generate ontology module headers")
    h.add_argument("--force", action="store_true")
    h.set_defaults(func=cmd_headers)
    sub.add_parser("fmt", help="rewrite ontology/*.ttl in canonical Turtle").set_defaults(func=cmd_fmt)
    sub.add_parser("labelmap", help="regenerate docs/cco-label-map.md").set_defaults(func=cmd_labelmap)
    sub.add_parser("check", help="pins, registry and handling checks").set_defaults(func=cmd_check)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
