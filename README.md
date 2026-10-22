# AOC-DFO — AOC Data Flow Ontology

A BFO/CCO ontology of the data flows into, out of and within a USAF Air Operations Center (AOC),
built only from public sources, with every assertion cited to a source and anchor.

AOC-DFO is a component of the **[Acquisition Knowledge System (AKS)](https://github.com/semanticarchitectures/acquisition-knowledge-system)**.
In AKS it is:

1. the reference ontology of AOC data flows;
2. the **alignment target** for the knowledge base's acquisition ontology, so the two graphs join
   without remapping (umbrella ADR 0005, ADR 0006);
3. at the far horizon, the **AOC side of the interface** between unmanned mission plans and the AOC.

Umbrella steering and ADRs take precedence over anything in this repo. Read the umbrella's
`.kiro/steering/` and `docs/vision.md` before changing the model.

## Status

Phase 0 (scaffolding). The spec is v1.1, pending approval: [requirements](.kiro/specs/aoc-dfo/requirements.md),
[design](.kiro/specs/aoc-dfo/design.md), [tasks](.kiro/specs/aoc-dfo/tasks.md),
[Amendment 001](.kiro/specs/aoc-dfo/amendments/001-aks-role-pins-od1-od4-mission-threads.md).
The ontology modules are headers only; no classes yet.

## What it models

| Module | Contents |
| --- | --- |
| `aoc-doctrine` | C2 nodes, doctrine processes, decisions, the air tasking cycle, doctrinal products |
| `aoc-msgstruct` | Message syntax: sets, segments, fields, format standards |
| `aoc-messages` | Message types and their content |
| `aoc-domain` | What messages are about: aircraft, targets, airspace, units, time, places |
| `aoc-flows` | Doctrinal data flows, their channels and implementing systems |
| `aoc-threads` | Design-time mission threads: decision → information artifact → channel → endpoint |
| `aoc-align` | Alignment to ENSIM, the KB ontology and GMNS (not imported by the core) |

## Upper ontologies (AKS shared pin)

| Ontology | Pin |
| --- | --- |
| BFO 2020 | tag `release-2024-01-29` |
| CCO | `v2.2` (2026-08-13) |

Both are vendored in [`ontology/imports/`](ontology/imports/PINS.yaml) and resolved through
[`ontology/catalog-v001.xml`](ontology/catalog-v001.xml). Pins change in the umbrella first, never
here alone. CCO 2.x uses opaque IRIs; [`docs/cco-label-map.md`](docs/cco-label-map.md) maps the
spec's label shorthand to them.

## Sources

Public only (OD-1). The [corpus registry](corpus/registry.yaml) lists every source with its tier,
edition and status. CAC-gated joint publications and distribution-controlled message standards are
registered as `unavailable`, and the gap report will say what that costs. The model is
authoritative at node, product and flow level and a hypothesis below it.

## Working on it

```sh
uv sync                    # Python 3.12
uv run pytest              # pins, catalog, module contract, canonical Turtle, registry, handling, label map
uv run aoc-dfo check       # fast pins/registry/handling check
uv run aoc-dfo fmt         # rewrite ontology/*.ttl in canonical Turtle
uv run aoc-dfo labelmap    # regenerate docs/cco-label-map.md after spec edits
```

CI also runs ROBOT (HermiT reasoning and a QC report) with the XML catalog; see
[`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Open items

- **Base IRI is provisional:** `https://w3id.org/aoc-dfo/`. Confirm (or replace) before any class
  is published; it is set once in `src/aoc_dfo/__init__.py` and the catalog.
- GMNS's ontology and conformance spec are not in the GMNS repo, so GMNS alignment and conformance
  reconciliation wait (R6.6).

## Handling

Public, unclassified content only. See [HANDLING.md](HANDLING.md).

## License

Apache 2.0 ([LICENSE](LICENSE)). Vendored BFO (CC BY 4.0) and CCO (BSD 3-Clause) keep their own
licenses; see [NOTICE](NOTICE).
