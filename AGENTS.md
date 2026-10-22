# AGENTS.md

Instructions for any coding agent working in this repo (Kiro, Claude Code or others).

## Read first

1. The umbrella's standing context: `.kiro/steering/` in
   [acquisition-knowledge-system](https://github.com/semanticarchitectures/acquisition-knowledge-system)
   (product, portfolio, tech, conventions, ontology). Umbrella steering and ADRs take precedence
   over this repo.
2. This repo's [`.kiro/steering/component.md`](.kiro/steering/component.md).
3. The spec: [`.kiro/specs/aoc-dfo/`](.kiro/specs/aoc-dfo/) and its amendments.
4. [HANDLING.md](HANDLING.md).

## Rules

- Spec workflow: requirements, then design, then tasks, each approved before the next. Never edit
  `tasks.md` alone. Record scope changes as a numbered amendment.
- **Public sources only.** Flag gaps; never guess. A missing fact is a one-line open question.
- **Every assertion carries provenance**: `prov:wasDerivedFrom` a registered source version and a
  `dfo:anchor`. An uncited class, flow or step is a defect.
- **CQ gate.** A new class or property names the competency question that needs it.
- **Never edit `ontology/imports/`.** Pins change in the umbrella's ontology steering first.
- Ontology files use CCO 2.x IRIs; spec text uses `cco:` label shorthand that must resolve
  (`uv run aoc-dfo labelmap`).
- Keep Turtle canonical (`uv run aoc-dfo fmt`) and `uv run pytest` green before committing.
- Ask before choices that affect the shared model (names shared with ENSIM or the KB, pins, IRIs,
  provenance pattern); those may need an umbrella ADR.
- Do not import the KB ontology or another component's ontology into a core module. Alignment
  goes in `aoc-align`.
