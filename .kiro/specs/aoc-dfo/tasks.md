# Implementation Plan — AOC Data Flow Ontology (AOC-DFO)

**Spec ID:** AOC-DFO-TSK
**Version:** 1.1
**Date:** 2026-10-22 (baseline v1.0: 2026-09-04)
**Traces to:** AOC-DFO-REQ v1.1, AOC-DFO-DES v1.1
**Repo:** all tasks land in `semanticarchitectures/aoc-dfo` unless marked *(umbrella)*.
**Amendments:** [001](amendments/001-aks-role-pins-od1-od4-mission-threads.md)

Conventions: tasks are ordered for execution; `[ ]` incomplete, `[x]` done; each task cites the
requirements it satisfies. Phases 0–1 are sequential; Phases 2–4 can overlap once their inputs exist;
Phase 9 (threads) starts after Phase 7 has its first flows; "Continuous" runs throughout.
Tasks changed or added by Amendment 001 are marked *(A001)*.

## Phase 0 — Scoping and setup

- [x] **0.1** Resolve OD-1 to OD-4 and record them. OD-2/OD-3 by umbrella ADR 0006; OD-1/OD-4 and the rest in Amendment 001. _Requirements: R12.3_ *(A001)*
- [x] **0.1a** *(umbrella)* Select the shared BFO 2020 and CCO pins and record them in the umbrella's ontology steering pin table. _Requirements: R6.1_ *(A001)*
- [x] **0.2** Scaffold the repository per design §8: single uv project (Python 3.12), src-layout, module directories, `HANDLING.md`, `AGENTS.md`, README linking the umbrella, LICENSE (Apache 2.0) and NOTICE, `corpus-controlled/` gitignored. _Requirements: R12.1, R12.5, R12.6_ *(A001)*
- [x] **0.3** Vendor BFO and CCO at the shared pin under `ontology/imports/` with `PINS.yaml` (commit, path, SHA-256, license), write `catalog-v001.xml`, and add the pin-hash and catalog-resolution checks. Write `docs/conformance.md` from the umbrella ontology rules (GMNS's conformance spec is not published; reconcile later). _Requirements: R6.1, R6.6, R6.7, NFR-4_ *(A001)*
- [x] **0.4** Create the seven ontology module headers (six core + `aoc-align`) with IRIs, version IRIs and the `owl:imports` graph of design §8, and the `owl:imports` contract test. _Requirements: R12.2, R14.3_ *(A001)*
- [x] **0.5** CI: pin and catalog checks, module contract, Turtle parse and canonical serialization, handling-marking grep, registry schema check, `cco:` label-map check, ROBOT reason (HermiT) and report, SHACL and CQ jobs (empty until later phases). _Requirements: R12.4, NFR-1, NFR-2, NFR-3_ *(A001)* — done 2026-10-22; SHACL and CQ jobs are placeholders until shapes/ and cq/ have content
- [x] **0.6** *(umbrella)* Add the repo URL to the umbrella README and portfolio, and the AOC-DFO spec to `docs/specs-index.md`. _Requirements: R12.6_ *(A001)*

## Phase 1 — Source corpus and provenance

- [ ] **1.1** Define the ProvenanceEnvelope as a PROV-O pattern (`prov:Entity` per source version, named graph per version, `dfo:anchor`, `dfo:sourceTier`, `dfo:handlingCaveat`, `dfo:supersededBy`) and its SHACL shape; mirror it in the `registry.yaml` schema. _Requirements: R1.1, R1.7, R8.6_ *(A001)*
- [x] **1.2** Populate `corpus/registry.yaml` with Tier 1a sources from design §2.1 and register Tier 1b/Tier 2 sources as `unavailable` and NATO surrogates as `verify-availability`. _Requirements: R1.3, R1.4, R1.6_ *(A001: updated 2026-10-22)*
- [ ] **1.3** Build the ingest script: PDF/HTML → anchored Markdown with paragraph, figure and table anchors preserved. Ingest AFMAN 13-1AOC Vol 3 first. _Requirements: R1.2_ *(A001)*
- [ ] **1.4** Build the schema ingest for NIEM 6.0 MilOps and MIM: XSD/model → element tables with element-path anchors. _Requirements: R1.2, R5.1_ *(A001)*
- [ ] **1.5** Stand up the corpus MCP server (search, fetch-by-anchor, list-sources) for extraction agents. _Requirements: R5.4_
- [ ] **1.6** CI check: any ontology assertion or catalog row lacking a provenance link fails the build. _Requirements: R1.2_
- [ ] **1.7** *(A001)* For each joint publication, find whether a public earlier edition exists on an official or long-standing government mirror; record it with `dfo:supersededBy` the current edition. _Requirements: R1.5, R1.6_

## Phase 2 — Doctrine layer

- [ ] **2.1** Extract AOC divisions and teams from AFMAN 13-1AOC Vol 3, AFMAN 13-1AOC Vol 2 and AFDP 3-0.1; model as `dfo:C2Node` subclasses/instances with roles. _Requirements: R2.1_ *(A001)*
- [ ] **2.2** Extract external nodes (JFC/JOC, JFACC staff, component LNOs, TACS elements, ISR nodes, coalition AOC) from AFDP 3-0.1, AFDP 3-52, AFI 13-114 Vol 3 and the public JP 3-30 edition. _Requirements: R2.2_ *(A001)*
- [ ] **2.3** Extract doctrinal processes and decisions per node; model as `dfo:DoctrineProcess` and `dfo:Decision` with agents and provenance. _Requirements: R2.3, R14.1_ *(A001)*
- [ ] **2.4** Model the six air tasking cycle stages (AFDP 3-60) with ordering and stated durations. _Requirements: R2.4_ *(A001)*
- [ ] **2.5** Extract doctrinal products; classify under CCO 2.2 ICE categories with written rationale per class; relate producing acts to products; flag each as an information artifact type. _Requirements: R3.1, R3.2, R3.3, R13.2_ *(A001)*
- [ ] **2.6** Write doctrine-layer CQs (minimum 8) with SPARQL; add to `cq/register.yaml`. _Requirements: R10.1_
- [ ] **2.7** Review gate: doctrine layer reviewed against sources; reasoner consistent. _Requirements: NFR-1_

## Phase 3 — Message structure and catalog

- [ ] **3.1** Author `aoc-msgstruct.ttl`: set/segment/field/group classes, format-standard instances (under Prescriptive ICE), structural properties. _Requirements: R6.5_ *(A001)*
- [ ] **3.2** Define `catalog/messages.csv` schema (id, standard, version, conveyed products, tier, notes). _Requirements: R4.1_
- [ ] **3.3** Extract message types associated with AOC functions from public doctrine and system documentation: USMTF sets, J-series, VMF K-series, MTF-XML, NIEM-MilOps exchanges (names and purposes only). _Requirements: R4.3_ *(A001)*
- [ ] **3.4** Identify unstructured flows (chat, briefings, voice) from doctrine and catalog them with the medium named. _Requirements: R4.2_
- [ ] **3.5** Map each doctrinal product and inter-node exchange to at least one catalog entry; log unmapped flows. _Requirements: R4.2_
- [ ] **3.6** Build the `build-messages` generator: `messages.csv` → `aoc-messages.ttl` (IBE + ICE per type, `conveysProduct`, `conformsToStandard`, artifact-type flag). _Requirements: R4.4, R13.2_ *(A001)*
- [ ] **3.7** Review gate: catalog completeness against Phase 2 products and flows.

## Phase 4 — Element extraction and canonical vocabulary

- [ ] **4.1** Build the canonical element vocabulary from NIEM 6.0 MilOps, then MIM; assign each canonical element a stable ID and provenance. _Requirements: R5.1, R5.2_ *(A001)*
- [ ] **4.2** Define `catalog/elements.csv` schema (element id, message type, name, datatype, cardinality, definition ref, canonical mapping, tier, gap status). _Requirements: R5.2_
- [ ] **4.3** Build the element extraction agent (Claude Code + corpus MCP) for public schema-defined message types; emit rows with provenance. _Requirements: R5.4_
- ~~**4.4** Tier 2 ingest and mapping~~ — removed by Amendment 001 (OD-1: public sources only).
- [ ] **4.5** Generate placeholder elements per message type with `dfo:sourceTier "2-unavailable"` and no invented definitions; map name-only elements or log `no-canonical-equivalent`. _Requirements: R5.3, R5.5_ *(A001)*
- [ ] **4.6** Review gate: element rows spot-checked against source anchors (sample ≥10%).

## Phase 5 — BFO/CCO mapping and domain layer

- [ ] **5.1** Author `docs/mapping-rules.md` (MR-1 to MR-9) including the MR-2 decision table for CCO 2.2 ICE categories. _Requirements: R6.2, R6.3_ *(A001)*
- [ ] **5.2** Author `aoc-domain.ttl`: reuse CCO 2.2 classes; add only CQ-gated classes (ACM types, mission package, sortie, target nomination) with provenance. _Requirements: R7.1, R7.2, R6.4_ *(A001)*
- [ ] **5.3** Author `docs/ensim-alignment.md` and `aoc-align.ttl` (ENSIM names, `Interaction`/`CommsLink` mapping); add KB and GMNS alignment when their ontologies exist at the shared pin. _Requirements: R7.3, R14.1, R14.3_ *(A001)*
- [ ] **5.4** Extend `build-messages` to emit element ICE subclasses with `cco:is_about` restrictions to domain classes per MR-2/MR-3. _Requirements: R6.3_
- [ ] **5.5** Run the conformance checklist; record any delta for later reconciliation with GMNS's conformance spec. _Requirements: R6.6_ *(A001)*
- [ ] **5.6** Write mapping/domain CQs (minimum 10). _Requirements: R10.1, R10.2_
- [ ] **5.7** Review gate: reasoner consistent over full import closure; no ungated new classes. _Requirements: NFR-1_

## Phase 6 — SHACL shapes

- [ ] **6.1** Build the `build-shapes` generator: one node shape per message type from `elements.csv`, enforcing required cardinality and datatypes/enumerations. _Requirements: R8.1, R8.2, R8.3, R8.5_
- [ ] **6.2** Implement Tier 2-unavailable handling: constrain only Tier 1a-supported facts; emit a `sh:description` limitation note. _Requirements: R8.4_
- [ ] **6.3** Unit-test the generator with hand-built positive and negative instances for three representative message types (one per major standard).

## Phase 7 — Flow model

- [ ] **7.1** Define `catalog/flows.csv` schema (producer, consumer(s), message type, stage, trigger, channel, system, provenance). _Requirements: R9.1, R9.2_ *(A001)*
- [ ] **7.2** Extract flows from AFMAN 13-1AOC Vol 3 and doctrine per air tasking cycle stage; record triggers with anchors. _Requirements: R9.2_ *(A001)*
- [ ] **7.3** Model systems (KRADOS and its applications, TBMCS, JADOCS, GCCS-J, DCGS) as `dfo:C2System` implementing standards; attach channels and systems where Tier 1a sources support it; mark unknown otherwise. _Requirements: R9.3, R9.4_ *(A001)*
- [ ] **7.4** Build the `build-flows` generator: `flows.csv` → `aoc-flows.ttl` as `cco:ActOfCommunication` subclasses/instances. _Requirements: R9.1_
- [ ] **7.5** Build the diagram generator: SPARQL → Mermaid per stage; commit outputs under `docs/diagrams/`. _Requirements: R9.5_
- [ ] **7.6** Write flow CQs (minimum 12), including dependency-trace queries (product → elements → originating message → node). _Requirements: R10.2_

## Phase 8 — Validation dataset and release

- [ ] **8.1** Design a synthetic 72-hour ATO cycle scenario (units, targets, airspace, missions) with no real operational data; mark all instances synthetic. _Requirements: R11.1, R11.2_
- [ ] **8.2** Generate ≥50 synthetic message instances spanning all catalog categories; validate against shapes to zero unintended violations. _Requirements: R11.3_
- [ ] **8.3** Execute the full CQ suite (≥30, including CQ-T1 to CQ-T6); store golden answers; enable CI diffing. _Requirements: R10.1, R10.3, R10.4_ *(A001)*
- [ ] **8.4** Generate the gap report from `dfo:sourceTier` and `dfo:supersededBy` annotations. _Requirements: R11.4_ *(A001)*
- [ ] **8.5** Verify deterministic Turtle serialization across two clean builds. _Requirements: NFR-2_
- [ ] **8.6** Release v1.1: tag, changelog, updated spec set, amendment log closed for the release. _Requirements: R12.3, R14.4_ *(A001)*

## Phase 9 — Mission-thread layer *(A001, new)*

- [ ] **9.1** Author `aoc-threads.ttl`: `dfo:MissionThreadScenario`, `dfo:TransmissionStep`, `dfo:CommunicationChannel` (+ CQ-gated subclasses), `dfo:EndpointRole` (+ capability-profile subclasses), the `dfo:step*` annotation properties, `dfo:realizesFlow`, `dfo:fallbackFor`. _Requirements: R13.1, R13.2_
- [ ] **9.2** Write the thread shapes: required step properties, `dfo:stepOrder` uniqueness per scenario, and SHACL-SPARQL subclass checks for every `dfo:step*` reference. _Requirements: R13.3, R13.4, R8.6_
- [ ] **9.3** Author three synthetic scenarios in `data/threads/`: nominal; degraded channel with a fallback step; a counterair or CAS thread crossing to a TACS node. Each step links to the doctrinal flow it realizes, or is reported by CQ-T2. _Requirements: R11.5, R13.5, R13.7_
- [ ] **9.4** Write CQ-T1 to CQ-T6 with SPARQL and golden answers; CQ-T6 returns a gap entry until a public source supports an unmanned endpoint. _Requirements: R13.6, R10.2_
- [ ] **9.5** Review gate: scenario classification check (R13.7 guardrail) on every scenario PR; resolve or carry MD-1 to MD-4.

## Continuous (all phases)

- [ ] **C.1** Log every scope, design, or requirement change as a numbered amendment under `.kiro/specs/aoc-dfo/amendments/`. _Requirements: R12.3_ *(A001)*
- [ ] **C.2** Keep CI green on every merge: pins, contract, ROBOT reason and report, SHACL, conformance, CQ suite, handling grep. _Requirements: R12.4_ *(A001)*
- [ ] **C.3** Keep `docs/ensim-alignment.md` and `aoc-align.ttl` current as doctrine classes are added. _Requirements: R14.1_ *(A001)*
- [ ] **C.4** *(A001)* Never change a pin here first. Follow the umbrella pin table; update vendored files and hashes in one PR when it changes. _Requirements: R6.1, R14.2_

## Dependencies and sequencing notes

- Phase 4 runs the public-only path (4.5); 4.4 is removed (OD-1).
- Phase 5.4 depends on 4.1–4.3 (elements exist) and 5.2 (domain classes exist).
- Phase 6 depends on 4.x complete; Phase 7.5 depends on 7.4.
- Phase 8.2 depends on Phase 6 complete. Phase 9.3 depends on 7.4 (flows to realize) and 9.2.
- A Foundry projection (OD-4) is out of scope for v1.x; open a separate spec after 8.6 if needed.
