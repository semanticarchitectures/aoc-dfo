# Design Document — AOC Data Flow Ontology (AOC-DFO)

**Spec ID:** AOC-DFO-DES
**Version:** 1.0 (baseline)
**Date:** 2026-09-04
**Traces to:** AOC-DFO-REQ v1.0
**Amendments:** none

## 1. Overview

AOC-DFO is a five-module OWL 2 ontology under BFO 2020 / CCO, with generated SHACL shapes, a synthetic instance dataset, and a competency-question suite. It is built with the same spec-driven, amendment-tracked, CQ-gated discipline as GMNS and is packaged for inclusion in the SA ontology monorepo.

The central design choice is **layer separation by stability**:

| Layer | Stability | Module | Primary sources |
|---|---|---|---|
| Doctrine (nodes, functions, products, cycle) | High | `aoc-doctrine.ttl` | JP 3-30, AFDP 3-30/3-60, AFTTP 3-3.AOC |
| Message standards (types, elements) | Medium | `aoc-messages.ttl`, `aoc-msgstruct.ttl` | NIEM-MilOps, JC3IEDM, USMTF/J-series/VMF (Tier 2) |
| Domain entities | High | `aoc-domain.ttl` | CCO, doctrine definitions, GMNS alignment |
| Flows (who sends what to whom, when, over what) | Medium | `aoc-flows.ttl` | Doctrine + system public documentation |
| Systems (TBMCS, KRADOS, JADOCS, GCCS-J, DCGS) | Low | inside `aoc-flows.ttl` as transport/implementation | Public fact sheets, program releases |

Systems are deliberately the least authoritative layer: they implement standards and carry flows, but never define them (REQ 9.4). This keeps the model valid across the TBMCS → KRADOS transition.

## 2. Source architecture

### 2.1 Tier 1 corpus (public, citable)

Joint: JP 3-30 (Joint Air Operations), JP 3-09 (Joint Fire Support), JP 3-52 (Joint Airspace Control), JP 3-60 (Joint Targeting), JP 2-01 (Joint and National Intelligence Support), JP 3-01 (Countering Air and Missile Threats).
USAF: AFDP 3-30 (Command and Control), AFDP 3-60 (Targeting), AFDP 3-1 (Counterair), AFDP 3-52 (Airspace Control), AFTTP 3-3.AOC (public portions), AFI 13-1AOC Vol 3.
Schemas: NIEM Military Operations domain (current release), JC3IEDM (MIP Baseline 3.1 or current public), C2 Core / UCore (archival).
Standards literature: Link 16 unclassified descriptive documents; DISA public USMTF program descriptions.
Systems: GCCS-J, JADOCS, TBMCS, DCGS public fact sheets; Kessel Run / KRADOS public releases.

Each entry in `corpus/registry.yaml` carries a ProvenanceEnvelope (see §7).

### 2.2 Tier 2 corpus (controlled)

MIL-STD-6040 (USMTF), MIL-STD-6016 (Link 16), MIL-STD-6017 (VMF), MTF-XML schemas, system ICDs. Stored, if obtained, outside the public repository under `corpus-controlled/` (gitignored, referenced by hash only). The build must succeed with this directory empty (REQ 1.3, 4.5, 5.5).

### 2.3 Tier-2-absent strategy

NIEM-MilOps and JC3IEDM are public and share lineage with USMTF/J-series element semantics. They become the canonical element vocabulary (REQ 5.1). Tier 2 elements, when available, are mapped *onto* that vocabulary rather than the reverse. When absent, message types still exist in the catalog and shapes enforce only Tier 1-supported constraints. The gap report (REQ 11.4) makes the boundary explicit.

## 3. Module design

### 3.1 `aoc-doctrine.ttl`

- Nodes: `dfo:AOCDivision`, `dfo:AOCTeam` ⊑ `cco:Organization`; instances for Strategy, Combat Plans, Combat Ops, ISR, Air Mobility, and named teams. External nodes as `cco:Organization` subclasses (JFC, JFACC staff, component LNO, TACS element, ISR node, coalition AOC).
- Roles: `cco:OrganizationalRole` per doctrinal responsibility.
- Functions: `dfo:AOCFunction` ⊑ `cco:Act`, with `cco:has_agent` → node.
- ATO cycle: `dfo:ATOCycleStage` ⊑ `cco:PlannedAct`, ordered via `bfo:precedes`; durations as `cco:Duration` where doctrine states them.
- Products: `dfo:DoctrinalProduct` ⊑ `cco:InformationContentEntity`, sub-typed per CCO category (Directive: ATO, ACO, SPINS, ITO; Descriptive: BDA report, MISREP, ISR sync matrix; Prescriptive/Directive: JAOP, AOD; Designative: JIPTL, RTL/JTL). Rationale recorded per class (REQ 3.2).

### 3.2 `aoc-msgstruct.ttl`

Structural vocabulary only, no domain semantics:
- `dfo:MessageSet`, `dfo:MessageSegment`, `dfo:MessageField`, `dfo:RepeatableGroup` ⊑ `cco:InformationBearingEntity` parts.
- `dfo:FormatStandard` ⊑ `cco:Directive ICE` (a standard is a directive about how to form messages); instances: USMTF, Link16, VMF, MTFXML, NIEMMilOps, Unstructured.
- Properties: `dfo:conformsToStandard`, `dfo:hasSegment`, `dfo:hasField`, `dfo:fieldOrder`, `dfo:minOccurs`, `dfo:maxOccurs`, `dfo:sourceTier`.

### 3.3 `aoc-messages.ttl`

Generated from `catalog/messages.csv`. One `cco:InformationBearingEntity` subclass per message type; one `cco:InformationContentEntity` subclass for its content; `dfo:conveysProduct` → doctrinal product; `dfo:conformsToStandard` → format standard. Elements from `catalog/elements.csv` become ICE subclasses with `cco:is_about some <domain class>`.

### 3.4 `aoc-domain.ttl`

Reuses CCO for Aircraft (`cco:Aircraft`), military units (`cco:MilitaryOrganization`), targets (`cco:Target`-adjacent via CCO event/artifact patterns), geospatial (`cco:GeospatialRegion`, `cco:GeospatialLocation`), time (`cco:TemporalInterval`). Adds under CQ gate: `dfo:AirspaceControlMeasure` and subtypes, `dfo:MissionPackage`, `dfo:Sortie`, `dfo:TargetNomination`. GMNS alignment table maintained in `docs/gmns-alignment.md` (REQ 7.3).

### 3.5 `aoc-flows.ttl`

- `dfo:DataFlow` ⊑ `cco:ActOfCommunication` with `cco:has_agent` (producer node), `cco:has_recipient` (consumer node), `dfo:bears` (message type or instance), `dfo:occursInStage` (ATO stage), `dfo:triggeredBy` (doctrinal condition, provenance-annotated), `dfo:viaTransport` (system or net).
- Systems: `dfo:C2System` ⊑ `cco:Artifact` with `dfo:implementsStandard`. Instances: TBMCS, KRADOS, JADOCS, GCCS-J, DCGS, Link16Net.
- Diagram generation: SPARQL → Mermaid (or Graphviz) per stage; committed under `docs/diagrams/`.

## 4. Mapping rules (normative)

Held in `docs/mapping-rules.md`; summarized:

- **MR-1** Message type → IBE subclass; message content → ICE subclass; never collapse the two.
- **MR-2** Every element is an ICE subclass. Its CCO category follows the element's function: identifier fields → Designative ICE; measurement/state fields → Descriptive ICE; tasking fields → Directive ICE.
- **MR-3** Every element carries `cco:is_about some X` where X is a domain class; X must not be an ICE (no "about a message" chains except for explicit reference fields, which use `cco:is_about some dfo:MessageInstance`).
- **MR-4** New classes require a CQ ID in `rdfs:comment` and a ProvenanceEnvelope reference.
- **MR-5** Tier 2-derived assertions carry `dfo:sourceTier "2"`; placeholders carry `"2-unavailable"` and no definition text.
- **MR-6** Structural constructs live only in `aoc-msgstruct.ttl`; domain modules must not import it directly (enforced by module linting).
- **MR-7** Systems are transports/implementations, never the range of `dfo:bears` or `dfo:conveysProduct`.

## 5. Extraction pipeline

```
corpus/registry.yaml ──► ingest ──► corpus/text/{doc}.md (+ anchors)
                                 │
                                 ▼
                       extract-nodes / extract-products / extract-messages / extract-elements
                       (Claude Code agents over an MCP server exposing corpus search + anchor resolution)
                                 │
                                 ▼
                       catalog/*.csv  (reviewed, committed)
                                 │
                                 ▼
                       build-ontology ──► ontology/*.ttl ──► build-shapes ──► shapes/*.ttl
                                 │
                                 ▼
                       validate (reasoner, SHACL, conformance, CQ suite) ──► reports/
```

Every extraction agent must emit provenance for each row; rows without provenance fail CI. Human review gate sits between extraction and catalog commit.

## 6. Validation strategy

- **Reasoning:** full import closure consistent under the reasoner pinned by GMNS (NFR-1).
- **SHACL:** shapes generated per REQ 8; synthetic dataset validated per REQ 11.3.
- **Conformance:** GMNS `ontology-conformance-spec.md` run as-is; deltas proposed as an amendment to that spec, not forked silently.
- **CQ suite:** `cq/register.yaml` with SPARQL per CQ; baseline results stored; CI diffs against baseline (REQ 10.3).
- **Gap report:** generated from `dfo:sourceTier` annotations (REQ 11.4).

## 7. Provenance model

ProvenanceEnvelope reused from the DoD Legal Structure Agent, expressed in RDF:

```
dfo:ProvenanceEnvelope  a owl:Class ;  # ⊑ cco:InformationContentEntity
  dfo:docId, dfo:edition, dfo:pubDate, dfo:anchor, dfo:sourceTier, dfo:handlingCaveat .
<assertion> dfo:hasProvenance <envelope> .
```

Anchors: paragraph numbers for doctrine, figure/table IDs, XPath or element path for schemas.

## 8. Repository layout

```
AOCDataFlowOntology/
  pyproject.toml            # uv workspace member
  src/aoc_dfo/              # build, extract, validate packages
  ontology/                 # five .ttl modules + imports pinned
  shapes/
  catalog/                  # messages.csv, elements.csv, flows.csv
  corpus/                   # registry.yaml, text/ (Tier 1 only)
  corpus-controlled/        # gitignored
  cq/
  data/synthetic/
  docs/                     # mapping-rules.md, gmns-alignment.md, diagrams/
  specs/                    # requirements.md, design.md, tasks.md, amendments/
  HANDLING.md
```

Module boundary contracts (import-linter): `domain` imports nothing internal; `msgstruct` imports nothing internal; `messages` → {msgstruct, domain}; `doctrine` → {domain}; `flows` → {doctrine, messages}.

## 9. Design decisions

- **D-1** NIEM-MilOps/JC3IEDM as canonical element vocabulary rather than USMTF. Rationale: public, structured, shared lineage; keeps the build Tier-2-independent.
- **D-2** Systems as transports, not flow definitions. Rationale: TBMCS/KRADOS transition; standards outlive systems.
- **D-3** Structural module separated from domain. Rationale: CCO's ICE hierarchy does not model message syntax; keeping syntax separate preserves CCO purity and GMNS interoperability.
- **D-4** Unstructured flows (chat, briefings) modeled, not omitted. Rationale: a material share of real AOC flow; omitting them misrepresents dependency.
- **D-5** Generated shapes and diagrams only. Rationale: hand-authored artifacts drift from the catalog.

## 10. Open decisions (require Kevin's input before Phase 1)

- **OD-1** Tier 2 access path: CAC/JITC registration available, or plan to build entirely Tier-2-absent for v1.0?
- **OD-2** Repository home: standalone `AOCDataFlowOntology` repo, or module inside a planned SA ontology monorepo alongside GMNS?
- **OD-3** CCO version pin: match GMNS exactly, or move both to the current CCO release as a joint amendment?
- **OD-4** Foundry target: should `aoc-domain.ttl` class design anticipate Foundry object types now (naming, flat properties), or defer entirely to the follow-on spec?

## 11. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Tier 2 unavailable | Element-level detail limited to NIEM/JC3IEDM proxies | D-1; gap report; placeholders |
| Scope creep toward full JC3IEDM | Schedule | CQ gate (REQ 6.4) |
| CCO ICE categories ambiguous for some fields | Inconsistent mapping | MR-2 decision table in mapping-rules.md; review gate |
| Public system docs too thin for transport layer | Flows lack transport | Transport optional; mark unknown, don't guess |
| Accidental CUI in public repo | Handling violation | corpus-controlled gitignored; CI grep for handling markings |
