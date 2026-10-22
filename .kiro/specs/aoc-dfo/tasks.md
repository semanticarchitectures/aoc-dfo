# Implementation Plan — AOC Data Flow Ontology (AOC-DFO)

**Spec ID:** AOC-DFO-TSK
**Version:** 1.0 (baseline)
**Date:** 2026-09-04
**Traces to:** AOC-DFO-REQ v1.0, AOC-DFO-DES v1.0
**Amendments:** none

Conventions: tasks are ordered for execution; `[ ]` incomplete; each task lists the requirements it satisfies. Phases 0–1 are sequential; Phases 2–4 can overlap once their inputs exist; Phase 8 runs throughout.

## Phase 0 — Scoping and setup

- [ ] **0.1** Resolve open decisions OD-1 through OD-4 (design.md §10) and record as Amendment 001 if any change scope. _Req: 12.3_
- [ ] **0.2** Scaffold repository per design.md §8: uv workspace, src-layout, module directories, `HANDLING.md`, `corpus-controlled/` gitignored. _Req: 12.1, 12.5_
- [ ] **0.3** Pin BFO 2020 and CCO imports to the GMNS versions (or per OD-3); copy `ontology-conformance-spec.md` from GMNS and register it as the conformance baseline. _Req: 6.1, 6.6_
- [ ] **0.4** Configure import-linter module contracts (domain, msgstruct, messages, doctrine, flows). _Req: 12.2_
- [ ] **0.5** Set up CI skeleton: reasoner consistency, SHACL, conformance, CQ suite, handling-marking grep. _Req: 12.4, NFR-3_

## Phase 1 — Source corpus and provenance

- [ ] **1.1** Define ProvenanceEnvelope in RDF (`dfo:ProvenanceEnvelope` and properties) and in `registry.yaml` schema. _Req: 1.1_
- [ ] **1.2** Populate `corpus/registry.yaml` with all Tier 1 sources from design.md §2.1, including edition and date; mark Tier 2 entries with status `unavailable` until obtained. _Req: 1.3, 1.4_
- [ ] **1.3** Build ingest script: PDF/HTML → anchored Markdown with paragraph, figure, and table anchors preserved. _Req: 1.2_
- [ ] **1.4** Build schema ingest for NIEM-MilOps and JC3IEDM: XSD/XMI → element tables with XPath/element-path anchors. _Req: 1.2, 5.1_
- [ ] **1.5** Stand up the corpus MCP server (search, fetch-by-anchor, list-sources) for use by extraction agents. _Req: 5.4_
- [ ] **1.6** Write CI check: any ontology assertion or catalog row lacking a provenance reference fails the build. _Req: 1.2_

## Phase 2 — Doctrine layer

- [ ] **2.1** Extract AOC divisions and teams from AFDP 3-30 and AFTTP 3-3.AOC; model as `cco:Organization` subclasses/instances with roles. _Req: 2.1_
- [ ] **2.2** Extract external nodes (JFC/JOC, JFACC staff, component LNOs, TACS elements, ISR nodes, coalition AOC) from JP 3-30, JP 3-52, JP 3-09, JP 2-01. _Req: 2.2_
- [ ] **2.3** Extract doctrinal functions per node; model as `dfo:AOCFunction` acts with agents and provenance. _Req: 2.3_
- [ ] **2.4** Model the ATO cycle stages with ordering and stated durations. _Req: 2.4_
- [ ] **2.5** Extract doctrinal products; classify under CCO ICE categories with written rationale per class; relate producing acts to products. _Req: 3.1, 3.2, 3.3_
- [ ] **2.6** Write doctrine-layer CQs (minimum 8) with SPARQL; add to `cq/register.yaml`. _Req: 10.1_
- [ ] **2.7** Review gate: doctrine layer reviewed against sources; reasoner consistent. _Req: NFR-1_

## Phase 3 — Message structure and catalog

- [ ] **3.1** Author `aoc-msgstruct.ttl`: set/segment/field/group classes, format-standard instances, structural properties. _Req: 6.5_
- [ ] **3.2** Define `catalog/messages.csv` schema (id, standard, version, conveyed products, tier, notes). _Req: 4.1_
- [ ] **3.3** Extract message types associated with AOC functions from Tier 1 doctrine and system documentation: USMTF sets, J-series, VMF K-series, MTF-XML, NIEM-MilOps exchanges. _Req: 4.3_
- [ ] **3.4** Identify unstructured flows (chat, briefings, voice) from doctrine and catalog them with medium named. _Req: 4.2_
- [ ] **3.5** Map each doctrinal product and inter-node exchange to at least one catalog entry; log unmapped flows. _Req: 4.2_
- [ ] **3.6** Build `build-messages` generator: `messages.csv` → `aoc-messages.ttl` (IBE + ICE per type, `conveysProduct`, `conformsToStandard`). _Req: 4.4_
- [ ] **3.7** Review gate: catalog completeness against Phase 2 products and flows.

## Phase 4 — Element extraction and canonical vocabulary

- [ ] **4.1** Build canonical element vocabulary from NIEM-MilOps and JC3IEDM ingest output; assign each canonical element a stable ID and provenance. _Req: 5.1, 5.2_
- [ ] **4.2** Define `catalog/elements.csv` schema (element id, message type, name, datatype, cardinality, definition ref, canonical mapping, tier, gap status). _Req: 5.2_
- [ ] **4.3** Build element extraction agent (Claude Code + corpus MCP) for Tier 1 schema-defined message types; emit rows with provenance. _Req: 5.4_
- [ ] **4.4** If Tier 2 available (OD-1): ingest into `corpus-controlled/`, extract USMTF set/field tables and J-series DFI/DUI definitions, map onto canonical vocabulary, log `no-canonical-equivalent` gaps. _Req: 5.3_
- [ ] **4.5** If Tier 2 unavailable: generate placeholder elements per message type with `dfo:sourceTier "2-unavailable"` and no invented definitions. _Req: 5.5_
- [ ] **4.6** Review gate: element rows spot-checked against source anchors (sample ≥10%).

## Phase 5 — BFO/CCO mapping and domain layer

- [ ] **5.1** Author `docs/mapping-rules.md` (MR-1 through MR-7) including the MR-2 decision table for ICE category assignment. _Req: 6.2, 6.3_
- [ ] **5.2** Author `aoc-domain.ttl`: reuse CCO Agent/Artifact/Event/Geospatial/Time classes; add only CQ-gated classes (ACM types, mission package, sortie, target nomination) with provenance. _Req: 7.1, 7.2, 6.4_
- [ ] **5.3** Author `docs/gmns-alignment.md` and add equivalence/subclass axioms with rationale. _Req: 7.3_
- [ ] **5.4** Extend `build-messages` to emit element ICE subclasses with `cco:is_about` restrictions to domain classes per MR-2/MR-3. _Req: 6.3_
- [ ] **5.5** Run conformance spec; file amendment to GMNS conformance spec for any AOC-DFO-specific check. _Req: 6.6_
- [ ] **5.6** Write mapping/domain CQs (minimum 10). _Req: 10.1, 10.2_
- [ ] **5.7** Review gate: reasoner consistent over full import closure; no ungated new classes. _Req: NFR-1_

## Phase 6 — SHACL shapes

- [ ] **6.1** Build `build-shapes` generator: one node shape per message type from `elements.csv`, enforcing required cardinality and datatypes/enumerations. _Req: 8.1, 8.2, 8.3, 8.5_
- [ ] **6.2** Implement Tier 2-unavailable handling: constrain only Tier 1-supported facts; emit `sh:description` limitation note. _Req: 8.4_
- [ ] **6.3** Unit-test generator with hand-built positive and negative instances for three representative message types (one per major standard).

## Phase 7 — Flow model

- [ ] **7.1** Define `catalog/flows.csv` schema (producer, consumer(s), message type, stage, trigger, transport, provenance). _Req: 9.1, 9.2_
- [ ] **7.2** Extract flows from doctrine per ATO stage; record triggers with anchors. _Req: 9.2_
- [ ] **7.3** Model systems (TBMCS, KRADOS, JADOCS, GCCS-J, DCGS, Link 16 nets) as `dfo:C2System` implementing standards; attach transports where Tier 1 sources support it; mark unknown otherwise. _Req: 9.3, 9.4_
- [ ] **7.4** Build `build-flows` generator: `flows.csv` → `aoc-flows.ttl` as `cco:ActOfCommunication` instances/subclasses. _Req: 9.1_
- [ ] **7.5** Build diagram generator: SPARQL → Mermaid per ATO stage; commit outputs under `docs/diagrams/`. _Req: 9.5_
- [ ] **7.6** Write flow CQs (minimum 12), including dependency-trace queries (product → elements → originating message → node). _Req: 10.2_

## Phase 8 — Validation dataset and release

- [ ] **8.1** Design synthetic 72-hour ATO cycle scenario (units, targets, airspace, missions) with no real operational data; mark all instances synthetic. _Req: 11.1, 11.2_
- [ ] **8.2** Generate ≥50 synthetic message instances spanning all catalog categories; validate against shapes to zero unintended violations. _Req: 11.3_
- [ ] **8.3** Execute full CQ suite (≥30); store baseline results; enable CI diffing. _Req: 10.1, 10.3_
- [ ] **8.4** Generate gap report from `dfo:sourceTier` annotations. _Req: 11.4_
- [ ] **8.5** Deterministic Turtle serialization in build; verify diff-stability across two clean builds. _Req: NFR-2_
- [ ] **8.6** Release v1.0: tag, changelog, updated spec set, amendment log closed for baseline. _Req: 12.3_

## Continuous (all phases)

- [ ] **C.1** Log every scope, design, or requirement change as a numbered amendment under `specs/amendments/`. _Req: 12.3_
- [ ] **C.2** Keep CI green on every merge: reasoner, SHACL, conformance, CQ suite, handling grep. _Req: 12.4_
- [ ] **C.3** Maintain `docs/gmns-alignment.md` as domain classes are added. _Req: 7.3_

## Dependencies and sequencing notes

- Phase 4.4 vs 4.5 is a branch on OD-1; only one executes in v1.0.
- Phase 5.4 depends on 4.1–4.3 (elements exist) and 5.2 (domain classes exist).
- Phase 6 depends on 4.x complete; Phase 7.5 depends on 7.4.
- Phase 8.2 depends on Phase 6 complete.
- A Foundry deployment spec (out of scope here) should be opened after 8.6, reusing `aoc-domain.ttl` per OD-4.
