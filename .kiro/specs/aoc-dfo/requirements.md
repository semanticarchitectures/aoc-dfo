# Requirements Document — AOC Data Flow Ontology (AOC-DFO)

**Spec ID:** AOC-DFO-REQ
**Version:** 1.1
**Date:** 2026-10-22 (baseline v1.0: 2026-09-04)
**Status:** Draft for review (v1.1 pending approval)
**Owning repo:** [semanticarchitectures/aoc-dfo](https://github.com/semanticarchitectures/aoc-dfo)
**Umbrella:** [Acquisition Knowledge System](https://github.com/semanticarchitectures/acquisition-knowledge-system) (ADR 0005, ADR 0006)
**Amendments:** [001](amendments/001-aks-role-pins-od1-od4-mission-threads.md) — AKS role, shared pins, OD-1/OD-4, mission-thread layer

Criteria changed or added by Amendment 001 are marked *(A001)*. IDs are cited as `R<n>.<m>`
(Requirement n, criterion m).

## Introduction

AOC-DFO is a BFO/CCO-conformant ontology, SHACL shape set, and instance dataset that models the data flows into, out of, and within a USAF Air Operations Center. Unlike the existing doctrinal overview document, AOC-DFO models each flow at the message level: every message type is typed against its format standard (USMTF, Link 16 J-series, VMF, MTF-XML, NIEM-MilOps, or unstructured), and every message element is mapped to a CCO Information Content Entity and to the domain entity it is about. Every class, element, and flow carries provenance to a source publication and anchor.

*(A001)* AOC-DFO is a component of the Acquisition Knowledge System (AKS) and part of its one shared model (ADR 0005). It has three jobs: (1) the reference ontology of AOC data flows; (2) the alignment target for the KB's acquisition ontology, so the two graphs join without remapping; and (3) at the far horizon, the AOC side of the interface between unmanned mission plans and the AOC. A mission-thread layer strings doctrinal flows into ordered, design-time threads (decision → information artifact → channel → endpoint) for traceability analysis.

The primary consumers are (a) AKS components and agents that read the shared model (the KB, ENCAP agents, Turnpoint at the far horizon), (b) Semantic Architectures engineers building C2 prototypes on MCP-connected tooling, and (c) AFMC/AOC program-office stakeholders who need a citable, doctrine-grounded interface model. *(A001)*

*(A001)* v1.x uses **public sources only** (OD-1). Sources fall into three tiers. Tier 1a sources are publicly released government publications and schemas. Tier 1b sources are unclassified but CAC-gated (current joint publications on JEL+); they are unavailable to this project. Tier 2 sources are distribution-controlled standards and ICDs (MIL-STD-6040, MIL-STD-6016, MIL-STD-6017, system ICDs); they are also unavailable. The model must remain valid and honest with Tiers 1b and 2 absent, and must report every gap they leave.

## Glossary

- **AOC-DFO**: this ontology and its companion artifacts.
- **AKS**: the Acquisition Knowledge System umbrella. *(A001)*
- **Node** (`dfo:C2Node`): an organizational unit that produces or consumes AOC data (AOC division, team, external component, TACS element, ISR node). Name reused from ENSIM. *(A001)*
- **Doctrinal product**: a named output defined in doctrine (e.g., ATO, ACO, JIPTL, MAAP, SPINS, MISREP).
- **Message type**: a class of information bearing entity conforming to a format standard (e.g., USMTF ATOCONF, Link 16 J3.2).
- **Message element**: a named field or segment of a message type.
- **Flow** (`dfo:DataFlow`): an act of communication transmitting a message from a producer node to one or more consumer nodes at a point in the ATO cycle, as doctrine describes it.
- **Mission thread** *(A001)*: an analyst-authored, design-time scenario (`dfo:MissionThreadScenario`) made of ordered transmission steps. Each step says which information artifact type moves, over which channel type, from which decision, between which endpoint roles. Hypothetical, never a record of a real operation.
- **Information artifact type** *(A001)*: any ICE class in AOC-DFO that a transmission step can carry (a doctrinal product or a message type's content). A role a class plays, not a class itself.
- **Channel type** *(A001)*: a class of communication channel (Link 16 network, voice net, chat).
- **Endpoint role** *(A001)*: the role of sending or receiving in a thread, borne by a node or by a platform type with a capability profile; never a specific airframe.
- **Tier 1a / 1b / 2**: source access tiers as defined above. *(A001)*
- **ProvenanceEnvelope**: the required citation pattern (document, edition, date, anchor, tier, handling caveat), expressed in PROV-O with one named graph per source version. *(A001)*
- **Competency question (CQ)**: a natural-language question the ontology must answer via SPARQL; the gate for adding classes.
- **ICE / IBE**: CCO Information Content Entity / Information Bearing Entity. Spec text uses CCO label shorthand; ontology files use CCO 2.x IRIs. *(A001)*
- **Shared pin** *(A001)*: the BFO 2020 and CCO releases recorded in the umbrella's ontology steering, used by every AKS ontology.

## Requirements

### Requirement 1 — Source corpus and provenance

**User story:** As a modeler, I want every source ingested with a machine-readable provenance record, so that every assertion in the ontology can be traced to a publication and anchor.

**Acceptance criteria**
1. WHEN a source document is added to the corpus THEN the system SHALL create a ProvenanceEnvelope record with document identifier, edition/version, publication date, tier (1a, 1b or 2), and handling caveat. *(A001)*
2. WHEN an ontology class, property, message element, flow, or transmission step is asserted THEN the system SHALL attach at least one provenance link to a source version (`prov:wasDerivedFrom`) and an anchor (paragraph, figure, table, or schema path). *(A001)*
3. IF a Tier 1b or Tier 2 source is unavailable THEN the system SHALL record it in the corpus registry with status `unavailable` and SHALL NOT fabricate content attributed to it. *(A001)*
4. THE corpus registry SHALL include, at minimum, the Tier 1a publications listed in design.md §2.1.
5. *(A001)* WHERE a public earlier edition substitutes for an unavailable current edition THE system SHALL mark every assertion derived from it with `dfo:supersededBy` the current edition and SHALL list it in the gap report.
6. *(A001)* THE system SHALL ingest a source only from an official government or standards-body release, and SHALL NOT ingest unofficial mirrors.
7. *(A001)* THE system SHALL express the ProvenanceEnvelope in PROV-O, with each source version as a `prov:Entity` in its own named graph, consistent with the umbrella's technology standards.

### Requirement 2 — Doctrine layer: nodes and processes

**User story:** As a modeler, I want the organizational nodes and their doctrinal processes represented as CCO organizations, roles, and acts, so that flows can be anchored to doctrinally defined producers and consumers.

**Acceptance criteria**
1. THE ontology SHALL model each AOC division and team named in AFDP 3-0.1, AFMAN 13-1AOC Vol 3 and AFMAN 13-1AOC Vol 2 as a `dfo:C2Node` (a `cco:Organization` subclass) subclass or instance with its doctrinal role. *(A001)*
2. THE ontology SHALL model external nodes (JFC/JOC, JFACC staff, component LNOs, TACS elements, ISR nodes, coalition AOCs) with the same pattern.
3. WHEN a node is modeled THEN the system SHALL associate it with at least one `dfo:DoctrineProcess` (a `cco:PlannedAct` subclass) with provenance. *(A001)*
4. THE ontology SHALL model the air tasking cycle stages (six stages per AFDP 3-60, 1 May 2026) as a temporally ordered sequence of `dfo:DoctrineProcess` subclasses with prescribed durations where doctrine states them. *(A001)*

### Requirement 3 — Doctrinal products

**User story:** As a modeler, I want each doctrinal product represented as a CCO ICE of the right category, so that message types and transmission steps can be linked to the product they convey.

**Acceptance criteria**
1. THE ontology SHALL model each doctrinal product named in the available editions of JP 3-30, AFDP 3-0.1 and AFMAN 13-1AOC Vol 3 (including JAOP, AOD, JIPTL, MAAP, ATO, ACO, SPINS, ITO, RTL/JTL, BDA report, MISREP, ISR synchronization matrix) as an ICE subclass. *(A001)*
2. WHEN a product is modeled THEN the system SHALL classify it under the CCO 2.2 ICE category (Prescriptive, Descriptive, Designative, or Representational) with a stated rationale. *(A001: CCO 2.2 has no Directive ICE)*
3. WHEN a product is produced by a node THEN the system SHALL relate the producing act to the product via a CCO output relation.

### Requirement 4 — Message catalog

**User story:** As a modeler, I want an enumerated catalog of message types per flow, so that every doctrinal product and inter-node exchange is tied to a concrete carrier format.

**Acceptance criteria**
1. THE system SHALL maintain a message catalog in which each entry has: message type identifier, format standard, standard version, conveyed doctrinal product(s), and source tier.
2. WHEN a flow is identified in doctrine THEN the catalog SHALL list at least one carrier message type or SHALL classify the flow as `unstructured` with the medium named (chat, briefing, voice).
3. THE catalog SHALL cover, at minimum, USMTF sets, Link 16 J-series messages, VMF K-series messages, MTF-XML, and NIEM-MilOps exchange types that public doctrine or public system documentation associates with AOC functions. *(A001)*
4. THE system SHALL generate `aoc-messages.ttl` from the catalog such that every catalog entry has exactly one corresponding `cco:InformationBearingEntity` subclass.
5. IF a message type's format standard is Tier 2 and unavailable THEN the catalog entry SHALL still exist with element detail marked `tier2-unavailable`.

### Requirement 5 — Message element extraction

**User story:** As a modeler, I want message elements extracted into a canonical element vocabulary, so that elements from different standards can be compared and mapped uniformly.

**Acceptance criteria**
1. THE system SHALL define a canonical element vocabulary derived from public schemas: NIEM 6.0 Military Operations domain first, and the MIP Information Model (MIM) second. *(A001)*
2. WHEN a message element is extracted from any standard THEN the system SHALL record its name, datatype, cardinality, definition text (or reference), owning message type, and provenance.
3. WHERE an element is known only by name from public descriptive literature THE system SHALL map it to a canonical element or SHALL log it in the gap register as `no-canonical-equivalent`. *(A001: no Tier 2 extraction in v1.x)*
4. THE extraction SHALL be executed by a reproducible pipeline (script or MCP-backed agent) and SHALL NOT rely on hand-transcribed element tables.
5. IF an element is known to exist but its definition is inaccessible THEN the system SHALL create a placeholder element with `dfo:sourceTier "2-unavailable"` and no invented definition.

### Requirement 6 — BFO/CCO mapping

**User story:** As an ontologist, I want message structure and content mapped to BFO/CCO under explicit rules, so that AOC-DFO joins the KB ontology, GMNS and other AKS ontologies without remapping.

**Acceptance criteria**
1. THE ontology SHALL import BFO 2020 and CCO at the shared pin recorded in the umbrella's ontology steering (currently BFO 2020 tag `release-2024-01-29`, CCO `v2.2`), and SHALL change a pin only after the umbrella table changes. *(A001)*
2. THE ontology SHALL model each message type as a `cco:InformationBearingEntity` subclass and its content as a `cco:InformationContentEntity` subclass.
3. WHEN a message element is mapped THEN the system SHALL assert it as an ICE subclass with a `cco:is_about` restriction to a domain entity class.
4. THE ontology SHALL define new classes only where a registered competency question cannot be answered with existing BFO/CCO classes, and each new class SHALL cite the CQ that requires it.
5. THE ontology SHALL place message-structure constructs (set, segment, field, repeatable group) in a separate module `aoc-msgstruct.ttl` so that the domain module contains no structural-only classes.
6. THE ontology SHALL pass the AOC-DFO conformance checklist (`docs/conformance.md`), derived from the umbrella's ontology rules; WHEN GMNS publishes its `ontology-conformance-spec.md` THEN the checklist SHALL be reconciled with it by amendment. *(A001)*
7. *(A001)* THE build SHALL resolve every BFO and CCO import from vendored files through an XML catalog, and SHALL fail IF a vendored file's SHA-256 differs from the pin.

### Requirement 7 — Domain entity layer

**User story:** As a modeler, I want the things messages are about (aircraft, missions, targets, airspace, units, times, locations) modeled with CCO classes, so that `is_about` targets are well-defined.

**Acceptance criteria**
1. THE ontology SHALL reuse CCO 2.2 Agent, Artifact, Event, Geospatial, and Time classes for domain entities wherever CCO provides them. *(A001)*
2. WHEN CCO lacks a needed domain class (e.g., airspace control measure types, mission package) THEN the system SHALL add it under the CQ gate in R6.4 with provenance to the defining doctrine.
3. THE ontology SHALL align domain classes with GMNS and KB ontology classes where the same real-world kind is modeled, using `owl:equivalentClass` or `rdfs:subClassOf` with a documented rationale, in a separate alignment module that the core modules do not import. *(A001)*

### Requirement 8 — SHACL shapes

**User story:** As a data engineer, I want SHACL shapes per message type and per thread class, so that instances can be validated for structural conformance.

**Acceptance criteria**
1. THE system SHALL generate one SHACL node shape per message type in the catalog.
2. WHEN a message type has required elements THEN its shape SHALL enforce minimum cardinality 1 for each.
3. WHEN an element has a defined datatype or enumeration THEN its shape SHALL enforce it.
4. WHEN element detail is `tier2-unavailable` THEN the shape SHALL enforce only what Tier 1a sources support and SHALL carry a `sh:description` noting the limitation. *(A001)*
5. THE shapes SHALL be generated from the element vocabulary and catalog, not hand-authored.
6. *(A001)* THE system SHALL provide a SHACL shape enforcing the ProvenanceEnvelope pattern on every asserted class, flow and transmission step.

### Requirement 9 — Flow model

**User story:** As an analyst, I want each flow modeled as an act of communication with producer, consumer, bearer, channel, and ATO-cycle placement, so that I can trace dependencies across the cycle.

**Acceptance criteria**
1. THE ontology SHALL model each flow as a `cco:ActOfCommunication` (or a documented subclass) with agent, recipient, and bearer participants.
2. WHEN a flow is modeled THEN the system SHALL assign it to an air tasking cycle stage and record the doctrinal trigger with provenance.
3. WHEN a flow's channel is known from Tier 1a sources THEN the system SHALL record it as a `dfo:CommunicationChannel` subclass (Link 16 network, voice net, chat, SIPR service). *(A001)*
4. THE ontology SHALL model systems (KRADOS and its applications, TBMCS, JADOCS, GCCS-J, DCGS) as implementations of message standards that a flow may run through, and SHALL NOT model system-specific interfaces as the primary flow definition. *(A001)*
5. THE system SHALL generate flow diagrams per air tasking cycle stage from the graph.

### Requirement 10 — Competency questions

**User story:** As a reviewer, I want a registered set of competency questions with executable SPARQL, so that ontology coverage is measured, not asserted.

**Acceptance criteria**
1. THE system SHALL maintain a CQ register with at least 30 questions, each with a SPARQL query and expected answer characteristics.
2. THE CQ register SHALL include at least: (a) all consumers of a given product; (b) all elements a product depends on, traced to originating message and node; (c) all flows in a given ATO stage; (d) all message types carried by a given channel type; (e) all elements lacking Tier 1a grounding; (f) the six mission-thread CQs in R13.6. *(A001)*
3. WHEN the ontology or dataset changes THEN all CQ queries SHALL be re-executed and results compared to the prior baseline.
4. *(A001)* THE CQ suite SHALL run in CI as golden-answer tests, per the umbrella's testing expectations.

### Requirement 11 — Validation dataset

**User story:** As a tester, I want a synthetic end-to-end ATO cycle dataset and synthetic mission threads, so that shapes and CQs are exercised on realistic instance data.

**Acceptance criteria**
1. THE system SHALL provide a synthetic dataset representing one 72-hour ATO cycle with at least 50 message instances spanning all catalog message categories.
2. THE synthetic dataset SHALL contain no real operational data and SHALL be marked as synthetic in every instance.
3. WHEN the synthetic dataset is validated against the shapes THEN it SHALL produce zero violations, or each violation SHALL be documented as intentional for test coverage.
4. THE system SHALL produce a gap report listing every element, message type, flow and transmission step whose grounding is `tier2-unavailable`, Tier 1b-unavailable, or from a superseded edition. *(A001)*
5. *(A001)* THE system SHALL provide at least three synthetic mission-thread scenarios: one nominal, one with a degraded channel and a fallback step, and one counterair or CAS thread that crosses the AOC boundary to a TACS node.

### Requirement 12 — Repository, packaging, and governance

**User story:** As a maintainer, I want AOC-DFO packaged and governed like the other AKS components, so that it can be pinned, imported and reviewed consistently. *(A001)*

**Acceptance criteria**
1. THE repository SHALL be the standalone repo `semanticarchitectures/aoc-dfo` (ADR 0006), a single uv project with src-layout and Python 3.12, and SHALL keep its spec in `.kiro/specs/aoc-dfo/`. *(A001)*
2. THE repository SHALL enforce ontology module boundaries (domain, msgstruct, messages, doctrine, flows, threads) with an `owl:imports` contract test. *(A001)*
3. WHEN a change alters requirements, design, or task scope THEN it SHALL be recorded as a numbered amendment in the spec set.
4. THE repository SHALL provide CI that runs pin and catalog checks, reasoning consistency (ROBOT with HermiT), a ROBOT QC report, SHACL validation, conformance checks, and the CQ suite on every change. *(A001)*
5. THE repository SHALL contain a HANDLING.md stating that the repository holds public, unclassified content only and that Tier 1b, Tier 2, CUI and classified material must never be committed. *(A001)*
6. *(A001)* THE README and AGENTS.md SHALL link to the umbrella repo and state that umbrella steering and ADRs take precedence over this spec.

### Requirement 13 — Mission-thread layer *(A001, new)*

**User story:** As an analyst, I want to author hypothetical mission threads as ordered steps that reuse the doctrinal model, so that I can trace a decision through information artifacts and channels to endpoints, and compare nominal and degraded variants.

**Acceptance criteria**
1. THE ontology SHALL provide a module `aoc-threads.ttl` defining `dfo:MissionThreadScenario`, `dfo:Decision`, `dfo:Task`, `dfo:TransmissionStep`, `dfo:CommunicationChannel` and `dfo:EndpointRole`, each placed under a CCO 2.2 or BFO class as given in design.md §3.6.
2. THE ontology SHALL treat information artifact types as existing ICE classes flagged `dfo:isInformationArtifactType true`, and SHALL NOT define a metaclass for them.
3. WHEN a transmission step is authored THEN it SHALL state its order within the scenario, its artifact type, its channel type, its originating decision, and its sender and receiver endpoint roles, by reference to classes.
4. IF a transmission step references an IRI that is not a subclass of the expected root THEN SHACL validation SHALL report a violation.
5. WHERE a step realizes a doctrinal flow THE step SHALL link to that `dfo:DataFlow`; WHERE it replaces another step under degraded conditions THE step SHALL link to it with `dfo:fallbackFor`.
6. THE CQ register SHALL include the thread CQs CQ-T1 to CQ-T6 in design.md §5.1, including CQ-T6 (unmanned-platform endpoint steps), which SHALL return either results or a gap entry.
7. THE scenarios SHALL stay at the level of artifact type over channel type, and SHALL NOT record timing, capacity, net assignments or fallback sequences drawn from real operations.

### Requirement 14 — Alignment with the AKS shared model *(A001, new)*

**User story:** As an AKS architect, I want AOC-DFO to share names, pins and provenance conventions with the rest of the shared model, so that the KB, ENSIM and AOC-DFO graphs can be joined and compared without remapping.

**Acceptance criteria**
1. THE ontology SHALL use ENSIM's org-doctrine names for the matching concepts (`C2Node`, `DoctrineProcess`, `Decision`) in the `dfo:` namespace, and SHALL record the correspondence, including ENSIM `Interaction` and `CommsLink`, in `docs/ensim-alignment.md`.
2. IF AOC-DFO needs to diverge from an ENSIM name or from the shared pin THEN the change SHALL wait for an umbrella ADR.
3. THE repository SHALL NOT import the KB ontology or any other AKS component's ontology into its core modules; alignment axioms SHALL live in a separate module.
4. THE ontology SHALL keep IRIs stable across releases and SHALL deprecate rather than delete a published term.
5. THE design SHALL avoid structure that a SPARQL CONSTRUCT export cannot flatten, so a later Foundry projection needs no remodeling (OD-4).

## Non-functional requirements

- **NFR-1** Reasoning consistency (HermiT, through ROBOT) SHALL complete without inconsistency on the full import closure. *(A001)*
- **NFR-2** All Turtle SHALL be serialized deterministically for diff-friendly review.
- **NFR-3** Public repository content SHALL be UNCLASSIFIED with no CUI.
- **NFR-4** *(A001)* No build or test step SHALL fetch an ontology over the network.

## Out of scope (v1.x)

- Classified message content or classified system interfaces.
- Real-time message parsing or a runtime message bus.
- Coalition-specific formats beyond those referenced by Tier 1a US doctrine (ADatP-3 deferred unless an official public release is confirmed). *(A001)*
- Tier 1b and Tier 2 sources (OD-1). *(A001)*
- Foundry ontology deployment. A later adapter projects the graph; AOC-DFO is not shaped for Foundry object types (OD-4). *(A001)*
- Building the unmanned-to-AOC interface. v1.x only keeps it expressible (R13.6). *(A001)*
- Real or logged mission data in mission threads. *(A001)*
