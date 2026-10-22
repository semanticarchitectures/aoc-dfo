---
inclusion: always
---

# Component: AOC-DFO

Standing context for this repo. The umbrella's steering
([acquisition-knowledge-system/.kiro/steering](https://github.com/semanticarchitectures/acquisition-knowledge-system/tree/main/.kiro/steering))
applies here and takes precedence; this file adds only what is specific to AOC-DFO.

## Role in AKS

- Reference ontology of AOC data flows, public sources only.
- Alignment target for the KB's acquisition ontology. The KB depends on AOC-DFO, never the reverse.
- Far horizon: models the AOC side of the unmanned-to-AOC interface. Kept expressible, not built.

## Decisions in force

| Decision | Value | Source |
| --- | --- | --- |
| Repo | Standalone `semanticarchitectures/aoc-dfo` | Umbrella ADR 0006 (OD-2) |
| Upper ontologies | BFO 2020 `release-2024-01-29`, CCO `v2.2` | Umbrella ADR 0006 (OD-3), ontology steering pin table |
| Sources | Public only; Tier 1b and Tier 2 unavailable | Amendment 001 (OD-1) |
| Foundry | Not shaped for Foundry; later projection by export | Amendment 001 (OD-4) |
| Shared names | ENSIM's `C2Node`, `DoctrineProcess`, `Decision` in the `dfo:` namespace | Umbrella ontology steering; Amendment 001 §A7 |
| Provenance | PROV-O; named graph per source version; `dfo:anchor` per assertion | Umbrella tech steering; Amendment 001 §A7 |
| Tooling | Python 3.12, uv, rdflib, pySHACL, ROBOT 1.9.8 (HermiT) | Umbrella tech steering |
| Base IRI | `https://w3id.org/aoc-dfo/` — **provisional** | Open item |

## Modeling reminders

- CCO 2.2 has no Directive ICE, no Military Organization and no Organization Role.
- Mission-thread steps reference classes by annotation properties (punning); scenarios never assert
  hypothetical particulars.
- Systems (KRADOS apps, TBMCS) implement standards; they never define flows.
