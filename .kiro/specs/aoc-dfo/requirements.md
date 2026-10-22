# Requirements Document — AOC Data Flow Ontology (AOC-DFO)

**Spec ID:** AOC-DFO-REQ
**Version:** 1.0 (baseline)
**Date:** 2026-09-04
**Status:** Draft for review
**Amendments:** none

## Introduction

AOC-DFO is a BFO/CCO-conformant ontology, SHACL shape set, and instance dataset that models the data flows into, out of, and within a USAF Air Operations Center. Unlike the existing doctrinal overview document, AOC-DFO models each flow at the message level: every message type is typed against its format standard (USMTF, Link 16 J-series, VMF, MTF-XML, NIEM-MilOps, or unstructured), and every message element is mapped to a CCO Information Content Entity and to the domain entity it is about. Every class, element, and flow carries provenance to a source publication and anchor.

The primary consumers are (a) Semantic Architectures engineers building IMS and C2 prototypes on Palantir Foundry and MCP-connected tooling, and (b) AFMC/AOC program-office stakeholders who need a citable, doctrine-grounded interface model.

Source material is split into two tiers. Tier 1 sources are publicly released government publications and schemas. Tier 2 sources are distribution-controlled standards and ICDs (MIL-STD-6040, MIL-STD-6016, MIL-STD-6017, system ICDs). Tier 2 availability is not assumed; the model must remain valid and honest with Tier 2 absent.

## Glossary

- **AOC-DFO**: this ontology and its companion artifacts.
- **Node**: an organizational unit that produces or consumes AOC data (AOC division, team, external component, TACS element, ISR node).
- **Doctrinal product**: a named output defined in doctrine (e.g., ATO, ACO, JIPTL, MAAP, SPINS, MISREP).
- **Message type**: a class of information bearing entity conforming to a format standard (e.g., USMTF ATOCONF, Link 16 J3.2).
- **Message element**: a named field or segment of a message type.
- **Flow**: an act of communication transmitting a message instance from a producer node to one or more consumer nodes at a point in the ATO cycle.
- **Tier 1 / Tier 2**: source access tiers as defined above.
- **ProvenanceEnvelope**: the citation structure reused from the DoD Legal Structure Agent (document ID, version, date, anchor, tier, handling caveat).
- **Competency question (CQ)**: a natural-language question the ontology must answer via SPARQL; the gate for adding classes.
- **ICE / IBE**: CCO Information Content Entity / Information Bearing Entity.

## Requirements

### Requirement 1 — Source corpus and provenance

**User story:** As a modeler, I want every source ingested with a machine-readable provenance record, so that every assertion in the ontology can be traced to a publication and anchor.

**Acceptance criteria**
1. WHEN a source document is added to the corpus THEN the system SHALL create a ProvenanceEnvelope record with document identifier, edition/version, publication date, tier (1 or 2), and handling caveat.
2. WHEN an ontology class, property, message element, or flow is asserted THEN the system SHALL attach at least one provenance annotation referencing a ProvenanceEnvelope and an anchor (paragraph, figure, table, or schema path).
3. IF a Tier 2 source is unavailable THEN the system SHALL record the source in the corpus registry with status `unavailable` and SHALL NOT fabricate content attributed to it.
4. THE corpus registry SHALL include, at minimum, the Tier 1 publications listed in design.md §2.1.

### Requirement 2 — Doctrine layer: nodes and functions

**User story:** As a modeler, I want the organizational nodes and their doctrinal functions represented as CCO organizations, roles, and acts, so that flows can be anchored to doctrinally defined producers and consumers.

**Acceptance criteria**
1. THE ontology SHALL model each AOC division and team named in AFDP 3-30 and AFTTP 3-3.AOC (public portions) as a `cco:Organization` subclass or instance with its doctrinal role.
2. THE ontology SHALL model external nodes (JFC/JOC, JFACC staff, component LNOs, TACS elements, ISR nodes, coalition AOCs) with the same pattern.
3. WHEN a node is modeled THEN the system SHALL associate it with at least one doctrinal function modeled as a `cco:Act` subclass with provenance.
4. THE ontology SHALL model the ATO cycle stages as a temporally ordered sequence of `cco:Act` subclasses with prescribed durations where doctrine states them.

### Requirement 3 — Doctrinal products

**User story:** As a modeler, I want each doctrinal product represented as a CCO directive or descriptive ICE, so that message types can be linked to the product they convey.

**Acceptance criteria**
1. THE ontology SHALL model each doctrinal product named in JP 3-30 and AFDP 3-30 (including JAOP, AOD, JIPTL, MAAP, ATO, ACO, SPINS, ITO, RTL/JTL, BDA report, MISREP, ISR synchronization matrix) as an ICE subclass.
2. WHEN a product is modeled THEN the system SHALL classify it under the correct CCO ICE category (Directive, Descriptive, Designative, or Prescriptive) with a stated rationale.
3. WHEN a product is produced by a node THEN the system SHALL relate the producing act to the product via a CCO output relation.

### Requirement 4 — Message catalog

**User story:** As a modeler, I want an enumerated catalog of message types per flow, so that every doctrinal product and inter-node exchange is tied to a concrete carrier format.

**Acceptance criteria**
1. THE system SHALL maintain a message catalog in which each entry has: message type identifier, format standard, standard version, conveyed doctrinal product(s), and source tier.
2. WHEN a flow is identified in doctrine THEN the catalog SHALL list at least one carrier message type or SHALL classify the flow as `unstructured` with the medium named (chat, briefing, voice).
3. THE catalog SHALL cover, at minimum, USMTF sets, Link 16 J-series messages, VMF K-series messages, MTF-XML, and NIEM-MilOps exchange types that doctrine or public system documentation associates with AOC functions.
4. THE system SHALL generate `aoc-messages.ttl` from the catalog such that every catalog entry has exactly one corresponding `cco:InformationBearingEntity` subclass.
5. IF a message type's format standard is Tier 2 and unavailable THEN the catalog entry SHALL still exist with element detail marked `tier2-unavailable`.

### Requirement 5 — Message element extraction

**User story:** As a modeler, I want message elements extracted into a canonical element vocabulary, so that elements from different standards can be compared and mapped uniformly.

**Acceptance criteria**
1. THE system SHALL define a canonical element vocabulary derived from Tier 1 schemas (NIEM Military Operations domain and JC3IEDM/MIP) before any Tier 2 elements are mapped.
2. WHEN a message element is extracted from any standard THEN the system SHALL record its name, datatype, cardinality, definition text (or reference), owning message type, and provenance.
3. WHEN a Tier 2 element is extracted THEN the system SHALL map it to a canonical element or SHALL log it in the gap register as `no-canonical-equivalent`.
4. THE extraction SHALL be executed by a reproducible pipeline (script or MCP-backed agent) and SHALL NOT rely on hand-transcribed element tables.
5. IF an element is known to exist but its definition is inaccessible THEN the system SHALL create a placeholder element with `dfo:sourceTier "2-unavailable"` and no invented definition.

### Requirement 6 — BFO/CCO mapping

**User story:** As an ontologist, I want message structure and content mapped to BFO/CCO under explicit rules, so that AOC-DFO is interoperable with GMNS and other CCO-based SA ontologies.

**Acceptance criteria**
1. THE ontology SHALL import BFO 2020 and CCO at the same pinned versions used by GMNS.
2. THE ontology SHALL model each message type as a `cco:InformationBearingEntity` subclass and its content as a `cco:InformationContentEntity` subclass.
3. WHEN a message element is mapped THEN the system SHALL assert it as an ICE subclass with a `cco:is_about` restriction to a domain entity class.
4. THE ontology SHALL define new classes only where a registered competency question cannot be answered with existing BFO/CCO classes, and each new class SHALL cite the CQ that requires it.
5. THE ontology SHALL place message-structure constructs (set, segment, field, repeatable group) in a separate module `aoc-msgstruct.ttl` so that the domain module contains no structural-only classes.
6. THE ontology SHALL pass the GMNS `ontology-conformance-spec.md` checks (or an AOC-DFO-adapted version tracked as an amendment to that spec).

### Requirement 7 — Domain entity layer

**User story:** As a modeler, I want the things messages are about (aircraft, missions, targets, airspace, units, times, locations) modeled with CCO classes, so that `is_about` targets are well-defined.

**Acceptance criteria**
1. THE ontology SHALL reuse CCO Agent, Artifact, Event, Geospatial, and Time classes for domain entities wherever CCO provides them.
2. WHEN CCO lacks a needed domain class (e.g., airspace control measure types, mission package) THEN the system SHALL add it under the CQ gate in Requirement 6.4 with provenance to the defining doctrine.
3. THE ontology SHALL align domain classes with GMNS classes where the same real-world kind is modeled, using `owl:equivalentClass` or `rdfs:subClassOf` with a documented rationale.

### Requirement 8 — SHACL shapes

**User story:** As a data engineer, I want SHACL shapes per message type, so that message instances can be validated for structural conformance.

**Acceptance criteria**
1. THE system SHALL generate one SHACL node shape per message type in the catalog.
2. WHEN a message type has required elements THEN its shape SHALL enforce minimum cardinality 1 for each.
3. WHEN an element has a defined datatype or enumeration THEN its shape SHALL enforce it.
4. WHEN element detail is `tier2-unavailable` THEN the shape SHALL enforce only what Tier 1 sources support and SHALL carry a `sh:description` noting the limitation.
5. THE shapes SHALL be generated from the element vocabulary and catalog, not hand-authored.

### Requirement 9 — Flow model

**User story:** As an analyst, I want each flow modeled as an act of communication with producer, consumer, bearer, transport, and ATO-cycle placement, so that I can trace dependencies across the cycle.

**Acceptance criteria**
1. THE ontology SHALL model each flow as a `cco:ActOfCommunication` (or a documented subclass) with agent, recipient, and bearer participants.
2. WHEN a flow is modeled THEN the system SHALL assign it to an ATO cycle stage and record the doctrinal trigger with provenance.
3. WHEN a flow's transport is known from Tier 1 sources THEN the system SHALL record it (Link 16 net, SIPR service, system name) as a CCO artifact or system class.
4. THE ontology SHALL model systems (TBMCS, KRADOS, JADOCS, GCCS-J, DCGS) as implementations of message standards, and SHALL NOT model system-specific interfaces as the primary flow definition.
5. THE system SHALL generate flow diagrams per ATO cycle stage from the graph.

### Requirement 10 — Competency questions

**User story:** As a reviewer, I want a registered set of competency questions with executable SPARQL, so that ontology coverage is measured, not asserted.

**Acceptance criteria**
1. THE system SHALL maintain a CQ register with at least 30 questions, each with a SPARQL query and expected answer characteristics.
2. THE CQ register SHALL include at least: (a) all consumers of a given product; (b) all elements a product depends on, traced to originating message and node; (c) all flows in a given ATO stage; (d) all message types carried by a given transport; (e) all elements lacking Tier 1 grounding.
3. WHEN the ontology or dataset changes THEN all CQ queries SHALL be re-executed and results compared to the prior baseline.

### Requirement 11 — Validation dataset

**User story:** As a tester, I want a synthetic end-to-end ATO cycle dataset, so that shapes and CQs are exercised on realistic instance data.

**Acceptance criteria**
1. THE system SHALL provide a synthetic dataset representing one 72-hour ATO cycle with at least 50 message instances spanning all catalog message categories.
2. THE synthetic dataset SHALL contain no real operational data and SHALL be marked as synthetic in every instance.
3. WHEN the synthetic dataset is validated against the shapes THEN it SHALL produce zero violations, or each violation SHALL be documented as intentional for test coverage.
4. THE system SHALL produce a gap report listing every element, message type, and flow whose grounding is `tier2-unavailable`.

### Requirement 12 — Repository, packaging, and governance

**User story:** As a maintainer, I want AOC-DFO packaged and governed like GMNS, so that it can be composed into the SA ontology monorepo.

**Acceptance criteria**
1. THE repository SHALL use uv workspace and src-layout consistent with the GMNS monorepo-readiness amendment.
2. THE repository SHALL enforce module boundaries (doctrine, messages, msgstruct, domain, flows) with import-linter or equivalent.
3. WHEN a change alters requirements, design, or task scope THEN it SHALL be recorded as a numbered amendment in the spec set.
4. THE repository SHALL provide CI that runs reasoning consistency, SHACL validation, conformance checks, and the CQ suite on every change.
5. THE repository SHALL contain a HANDLING.md stating that Tier 2 content, if ever added, must not be committed to the public remote.

## Non-functional requirements

- **NFR-1** Reasoning consistency (HermiT or ELK, as used by GMNS) SHALL complete without inconsistency on the full import closure.
- **NFR-2** All Turtle SHALL be serialized deterministically for diff-friendly review.
- **NFR-3** Public repository content SHALL be UNCLASSIFIED with no CUI.

## Out of scope (v1.0)

- Classified message content or classified system interfaces.
- Real-time message parsing or a runtime message bus.
- Coalition-specific formats beyond those referenced by Tier 1 US doctrine (ADatP-3 deferred).
- Foundry ontology deployment (a follow-on spec; AOC-DFO must be designed to permit it).
