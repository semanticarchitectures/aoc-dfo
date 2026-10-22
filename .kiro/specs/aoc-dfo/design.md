# Design Document — AOC Data Flow Ontology (AOC-DFO)

**Spec ID:** AOC-DFO-DES
**Version:** 1.1
**Date:** 2026-10-22 (baseline v1.0: 2026-09-04)
**Traces to:** AOC-DFO-REQ v1.1
**Amendments:** [001](amendments/001-aks-role-pins-od1-od4-mission-threads.md)

Sections changed by Amendment 001 are marked *(A001)*. Names such as `cco:InformationContentEntity`
are CCO label shorthand; ontology files use CCO 2.2 IRIs, listed in `docs/cco-label-map.md`.

## 1. Overview *(A001)*

AOC-DFO is a six-module OWL 2 DL ontology under the shared BFO 2020 / CCO 2.2 pin, with generated SHACL shapes, a synthetic instance dataset, and a competency-question suite. It is an AKS component (ADR 0005, ADR 0006): part of the shared model, the alignment target for the KB ontology, and at the far horizon the AOC side of the unmanned-to-AOC interface. It follows the umbrella's spec-driven, amendment-tracked, CQ-gated discipline.

The central design choice is **layer separation by stability**:

| Layer | Stability | Module | Primary sources |
|---|---|---|---|
| Doctrine (nodes, processes, decisions, products, cycle) | High | `aoc-doctrine.ttl` | AFMAN 13-1AOC Vol 3, AFDP 3-0.1, AFDP 3-60, JP 3-30 (2019 public edition) |
| Message standards (types, elements) | Medium | `aoc-messages.ttl`, `aoc-msgstruct.ttl` | NIEM 6.0 MilOps, MIM; USMTF/J-series/VMF by name only |
| Domain entities | High | `aoc-domain.ttl` | CCO 2.2, doctrine definitions |
| Flows (who sends what to whom, when, over what) | Medium | `aoc-flows.ttl` | Doctrine + public system documentation |
| Systems (KRADOS apps, TBMCS, JADOCS, GCCS-J, DCGS) | Low | inside `aoc-flows.ttl` as implementations | Kessel Run and program public releases |
| Mission threads (design-time scenarios) | Authored | `aoc-threads.ttl` (TBox) + `data/threads/` (scenarios) | Analyst-authored, grounded in the layers above |
| Alignment (ENSIM, KB, GMNS) | Follows partners | `aoc-align.ttl` | Partner schemas, pinned |

Systems are deliberately the least authoritative layer: they implement standards and carry flows, but never define them (R9.4). This keeps the model valid across the TBMCS → KRADOS transition.

## 2. Source architecture *(A001)*

### 2.1 Tier 1a corpus (public, citable)

Primary first: **AFMAN 13-1AOC Vol 3** (25 Jun 2024; no releasability restrictions), then AFMAN 13-1AOC Vol 2 (18 Feb 2020; official division names and abbreviations IRD, SRD, CPD, COD, AMD).
USAF doctrine: AFDP 3-0.1 Command and Control (22 Jan 2025; supersedes AFDP 3-30), AFDP 3-0, AFDP 3-60 Targeting (1 May 2026; six-stage air tasking cycle), AFDP 3-01 Counterair, AFDP 3-52 Airspace Control, AFDP 2-0, AFDP 3-36, AFDP 3-85, AFDP 5-0; AFDP 3-30 Appendix B (7 Jan 2020) as a superseded secondary source; AFI 13-114 Vol 3 (ASOC).
Joint (public earlier editions only): JP 3-30 (25 Jul 2019), and others as public copies are confirmed. Each is marked superseded by its current edition.
Schemas: NIEM 6.0 (OASIS NIEMOpen) MilOps domain; MIP Information Model (MIM); JC3IEDM 3.1.4 for legacy alignment only.
Standards literature: Link 16 and USMTF public descriptive documents (message names and purposes only).
Systems: Kessel Run OpsC2 / KRADOS pages and releases; TBMCS, JADOCS, GCCS-J, DCGS public fact sheets.

`corpus/registry.yaml` is the authoritative list, with one ProvenanceEnvelope per source (§7).

### 2.2 Tier 1b and Tier 2: unavailable (OD-1)

Tier 1b (current joint publications on JEL+, CAC-gated) and Tier 2 (MIL-STD-6040, 6016, 6017, MTF-XML, system ICDs) are registered by title and date with status `unavailable`. Nothing from them is ingested. `corpus-controlled/` remains in `.gitignore` as a guard only.

NATO surrogates (ADatP-3, ATDLP-5.16, STANAG 5516) are `verify-availability`: ingested only from an official NATO public release, never from a mirror (R1.6).

### 2.3 Public-only strategy

NIEM 6.0 MilOps and MIM are public and share lineage with USMTF/J-series element semantics. They are the canonical element vocabulary (R5.1). Message types named in public literature exist in the catalog; their elements are placeholders unless a public schema defines them. Shapes enforce only Tier 1a-supported constraints. The gap report (R11.4) lists every Tier 1b/Tier 2 hole and every superseded-edition dependency, so the fidelity ceiling is visible: authoritative at node, product and flow level; hypothesis below it.

## 3. Module design

### 3.1 `aoc-doctrine.ttl` *(A001)*

- **Nodes:** `dfo:C2Node` ⊑ `cco:Organization` (ENSIM name). Subclasses `dfo:AOCDivision`, `dfo:AOCTeam`; instances for the five core divisions per AFMAN 13-1AOC Vol 2 §1.1 (SRD, CPD, COD, IRD, AMD) and named teams. External nodes as `dfo:C2Node` subclasses (JFC/JOC, JFACC staff, component LNO, TACS element, ISR node, coalition AOC).
- **Roles:** BFO `role` subclasses per doctrinal responsibility (CCO 2.2 has no Organization Role); CCO's `Authority Role` where authority is the point.
- **Processes:** `dfo:DoctrineProcess` ⊑ `cco:PlannedAct` (ENSIM name; replaces v1.0 `dfo:AOCFunction`), with `cco:has_agent` → node.
- **Decisions and tasks:** `dfo:Decision` ⊑ `cco:PlannedAct` (ENSIM name), `cco:has_agent` → node or role, `dfo:informedBy` → the artifact types that feed it (mirrors ENSIM `informedBy`). `dfo:Task` ⊑ `cco:PlannedAct` (MD-2).
- **Air tasking cycle:** `dfo:AirTaskingCycleStage` ⊑ `dfo:DoctrineProcess`, six stages per AFDP 3-60 (1 May 2026), ordered via `bfo:precedes`; durations as CCO temporal intervals where doctrine states them.
- **Products:** `dfo:DoctrinalProduct` ⊑ `cco:InformationContentEntity`, sub-typed per CCO 2.2 category. Proposed starting classification, to be confirmed against sources with rationale per class (R3.2): Prescriptive: ATO, ACO, SPINS, ITO, JAOP, AOD; Descriptive: BDA report, MISREP, ISR synchronization matrix; Designative: JIPTL, RTL/JTL. CCO 2.2 `Report` (Document Content Entity) is evaluated for MISREP/BDA.
- Every product class is flagged `dfo:isInformationArtifactType true` (§3.6).

### 3.2 `aoc-msgstruct.ttl`

Structural vocabulary only, no domain semantics:
- `dfo:MessageSet`, `dfo:MessageSegment`, `dfo:MessageField`, `dfo:RepeatableGroup` ⊑ `cco:InformationBearingEntity` parts.
- `dfo:FormatStandard` ⊑ `cco:PrescriptiveInformationContentEntity` (a standard prescribes how to form messages) *(A001: was Directive ICE)*; instances: USMTF, Link16, VMF, MTFXML, NIEMMilOps, Unstructured.
- Properties: `dfo:conformsToStandard`, `dfo:hasSegment`, `dfo:hasField`, `dfo:fieldOrder`, `dfo:minOccurs`, `dfo:maxOccurs`, `dfo:sourceTier`.

### 3.3 `aoc-messages.ttl`

Generated from `catalog/messages.csv`. One `cco:InformationBearingEntity` subclass per message type; one `cco:InformationContentEntity` subclass for its content (candidate parent: CCO 2.2 `Message`, under Media Content Entity) *(A001)*; `dfo:conveysProduct` → doctrinal product; `dfo:conformsToStandard` → format standard. Elements from `catalog/elements.csv` become ICE subclasses with `cco:is_about some <domain class>`. Message content classes are flagged `dfo:isInformationArtifactType true`.

### 3.4 `aoc-domain.ttl` *(A001)*

Reuses CCO 2.2 for Aircraft (`cco:Aircraft`), organizations (`cco:Organization`, `cco:GovernmentOrganization`, `cco:ArmedForce`; CCO 2.2 has no Military Organization), targets (`cco:Target`, `cco:ActOfTargeting`), geospatial (`cco:GeospatialRegion` and related), time (BFO `temporal interval`). Adds under the CQ gate: `dfo:AirspaceControlMeasure` and subtypes, `dfo:MissionPackage`, `dfo:Sortie`, `dfo:TargetNomination`.

### 3.5 `aoc-flows.ttl` *(A001)*

- `dfo:DataFlow` ⊑ `cco:ActOfCommunication` with `cco:has_agent` (producer node), `cco:has_recipient` (consumer node), `cco:has_input` (the message or product bearer; replaces v1.0 `dfo:bears`), `dfo:occursInStage` (air tasking cycle stage), `dfo:triggeredBy` (doctrinal condition, provenance-annotated), `dfo:viaChannel` → `dfo:CommunicationChannel` (§3.6), `dfo:viaSystem` → `dfo:C2System` (optional). Corresponds to ENSIM `Interaction`.
- Systems: `dfo:C2System` ⊑ `cco:InformationProcessingArtifact` *(was `cco:Artifact`, absent in CCO 2.2)* with `dfo:implementsStandard`. Instances: KRADOS (AOC Block 20) and its applications as parts (Slapshot → MAAP, Triton → ATO, Spacer → ACO/airspace, Jigsaw → air refueling plan, MaiTai → asset availability); TBMCS (Block 10.1); JADOCS; GCCS-J; DCGS. KRID (authentication) and Rebel Alliance (inter-app events) are system properties, not flows. Skyhook and Direct: names only, no public function; registered as gaps.
- Diagram generation: SPARQL → Mermaid per stage; committed under `docs/diagrams/`.

### 3.6 `aoc-threads.ttl` — mission-thread layer *(A001, new)*

Purpose: design-time mission-thread traceability (decision → information artifact → channel → endpoint), for hypothetical threads authored by analysts.

| Class | Parent (CCO 2.2 / BFO) | Key properties |
|---|---|---|
| `dfo:MissionThreadScenario` | `cco:Plan` (MD-1) | `dfo:scenarioLabel`, `dfo:isSynthetic true`, `dfo:variantOf` → another scenario |
| `dfo:TransmissionStep` | `cco:PrescriptiveInformationContentEntity`; continuant part of a scenario | `dfo:stepOrder` (xsd:positiveInteger), `dfo:partOfScenario`, `dfo:realizesFlow` → `dfo:DataFlow`, `dfo:fallbackFor` → step; type references below |
| `dfo:CommunicationChannel` | `cco:TelecommunicationNetwork` | Subclasses: `dfo:Link16Network`, `dfo:VoiceNet`, `dfo:ChatService`, `dfo:SIPRNetService`, … added under the CQ gate. Later attributes (capacity, fallback, interoperability) attach here |
| `dfo:EndpointRole` | BFO `role` | Borne by a `dfo:C2Node` or a platform. Capability profiles as defined subclasses, e.g. `dfo:Link16FighterEndpointRole ≡ dfo:EndpointRole and (inheres in some (cco:Aircraft and has part some Link 16 terminal))` |
| `dfo:Decision`, `dfo:Task` | `cco:PlannedAct` | Defined in `aoc-doctrine` (§3.1); threads reference them |
| *Information artifact type* | — (no class) | Any ICE class flagged `dfo:isInformationArtifactType true` |

**Type references by punning.** A step is a real individual (an authored document part). What it is about is a class. Steps point to classes through annotation properties, so the ontology stays in OWL 2 DL and no hypothetical aircraft or ATO is asserted to exist:

| Annotation property | Range (checked by SHACL-SPARQL) |
|---|---|
| `dfo:stepArtifactType` | a class flagged `dfo:isInformationArtifactType true` |
| `dfo:stepChannelType` | a subclass of `dfo:CommunicationChannel` |
| `dfo:stepFromDecision` | a subclass of `dfo:Decision` or `dfo:Task` |
| `dfo:stepSenderRole`, `dfo:stepReceiverRole` | a subclass of `dfo:EndpointRole` |

A SHACL-SPARQL constraint per property checks `?value rdfs:subClassOf* <root>` against the ontology graph (R13.4).

**Example (illustrative, synthetic):**

```turtle
:scn-cas-nominal a dfo:MissionThreadScenario ; dfo:isSynthetic true ;
    dfo:scenarioLabel "CAS tasking to a fighter flight, nominal" .
:scn-cas-nominal-s1 a dfo:TransmissionStep ; dfo:partOfScenario :scn-cas-nominal ; dfo:stepOrder 1 ;
    dfo:stepFromDecision dfo:ApproveImmediateCASRequest ;
    dfo:stepArtifactType dfo:AirSupportRequestContent ;
    dfo:stepChannelType dfo:ChatService ;
    dfo:stepSenderRole dfo:ASOCEndpointRole ; dfo:stepReceiverRole dfo:CombatOpsDivisionEndpointRole .
```

Class names in the example are placeholders until the CQ gate admits them.

**Guardrail (R13.7).** Steps stay at artifact type over channel type. No timing, capacity, net assignments, or fallback sequences from real operations.

### 3.7 `aoc-align.ttl` *(A001, new)*

Alignment axioms to partners, kept out of the core modules (R7.3, R14.3): ENSIM names (documented in `docs/ensim-alignment.md`; ENSIM is a TypeScript/JSON schema, so alignment is a mapping table plus, where useful, IRIs minted for ENSIM concepts), the KB ontology (when it exists), and GMNS (when its ontology is published at the shared pin).

## 4. Mapping rules (normative)

Held in `docs/mapping-rules.md`; summarized:

- **MR-1** Message type → IBE subclass; message content → ICE subclass; never collapse the two.
- **MR-2** Every element is an ICE subclass. Its CCO 2.2 category follows the element's function: identifier fields → Designative ICE; measurement/state fields → Descriptive ICE; tasking fields → Prescriptive ICE. *(A001: was Directive ICE)*
- **MR-3** Every element carries `cco:is_about some X` where X is a domain class; X must not be an ICE (no "about a message" chains except for explicit reference fields, which use `cco:is_about some dfo:MessageInstance`).
- **MR-4** New classes require a CQ ID in `rdfs:comment` and a provenance link (§7).
- **MR-5** Tier 2-derived assertions would carry `dfo:sourceTier "2"`; none exist in v1.x. Placeholders carry `"2-unavailable"` and no definition text. Assertions from a public earlier edition carry `dfo:supersededBy`. *(A001)*
- **MR-6** Structural constructs live only in `aoc-msgstruct.ttl`; domain modules must not import it (enforced by the `owl:imports` contract test).
- **MR-7** Systems are implementations, never the range of `cco:has_input` on a flow or of `dfo:conveysProduct`. *(A001)*
- **MR-8** *(A001)* Scenario individuals never assert hypothetical particulars (aircraft, ATOs, nets). They reference classes through the `dfo:step*` annotation properties only.
- **MR-9** *(A001)* Ontology files use CCO 2.2 IRIs; spec text uses labels. `docs/cco-label-map.md` is generated from the pinned CCO file and checked in CI.

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
                       validate (ROBOT reason + report, SHACL, conformance, CQ suite) ──► reports/
```

Every extraction agent must emit provenance for each row; rows without provenance fail CI. Human review gate sits between extraction and catalog commit. Mission-thread scenarios are authored by hand (they are analyst products, not extractions), validated by the same shapes. *(A001)*

### 5.1 Mission-thread competency questions *(A001, new)*

| ID | Question |
|---|---|
| CQ-T1 | For scenario S, list its steps in order with artifact type, channel type, sender role and receiver role. |
| CQ-T2 | Which steps in S realize no doctrinal `dfo:DataFlow` (hops doctrine does not describe)? |
| CQ-T3 | Which steps in any scenario depend on channel type C, and which of them have a fallback step? |
| CQ-T4 | Starting from decision D, which artifact types and endpoint roles does it reach, transitively across steps? |
| CQ-T5 | For each step in S, which source versions and anchors ground it, and which steps rest only on superseded or unavailable sources? |
| CQ-T6 | Which steps have an unmanned-platform endpoint role, and over which channel types? (Expected in v1.1: empty result plus a gap entry.) |

## 6. Validation strategy *(A001)*

- **Pins:** vendored BFO/CCO hashes match the umbrella pin table; every `owl:imports` IRI resolves through `ontology/catalog-v001.xml` to a local file (R6.7, NFR-4).
- **Module contract:** `owl:imports` graph matches §8 (R12.2).
- **Reasoning:** ROBOT `reason` with HermiT over the full import closure (NFR-1); ROBOT `report` QC on every PR (umbrella change control).
- **SHACL:** pySHACL with generated shapes (R8), the ProvenanceEnvelope shape (R8.6) and the thread-reference SPARQL constraints (R13.4); synthetic data validated per R11.3.
- **Conformance:** `docs/conformance.md`, derived from umbrella ontology rules (pins, CQ gate, one shape per class and n-ary relation, PROV-O provenance, no imported-file edits). GMNS's conformance spec is not published in the GMNS repo; reconcile when it is (R6.6).
- **CQ suite:** `cq/register.yaml` with SPARQL per CQ; golden answers stored; CI diffs against them (R10.3, R10.4).
- **Gap report:** generated from `dfo:sourceTier` and `dfo:supersededBy` annotations (R11.4).
- **Serialization:** canonical Turtle; CI fails if re-serializing changes a committed file (NFR-2).

## 7. Provenance model *(A001)*

The ProvenanceEnvelope is a required pattern expressed in PROV-O (umbrella tech standard), not a bespoke class:

```turtle
# One named graph per source version, e.g. <urn:aoc-dfo:src/AFMAN-13-1AOCV3/2024-06-25>
<urn:aoc-dfo:src/AFMAN-13-1AOCV3/2024-06-25> a prov:Entity ;
    dcterms:identifier "AFMAN-13-1AOCV3" ; dfo:edition "25 Jun 2024" ;
    dcterms:issued "2024-06-25"^^xsd:date ; dfo:sourceTier "1a" ;
    dfo:handlingCaveat "UNCLASSIFIED; no releasability restrictions" ;
    prov:atLocation <https://static.e-publishing.af.mil/production/1/af_a3/publication/afman13-1aocv3/afman13-1aocv3_.pdf> .

dfo:CombatOperationsDivision prov:wasDerivedFrom <urn:aoc-dfo:src/AFMAN-13-1AOCV3/2024-06-25> ;
    dfo:anchor "para 1.1" .        # illustrative anchor
```

Required on every asserted class, flow and step: `prov:wasDerivedFrom` (≥1) and `dfo:anchor`. Source versions carry identifier, edition, date, tier, caveat and location. Superseded editions add `dfo:supersededBy`. Anchors: paragraph numbers for doctrine, figure/table IDs, XPath or element path for schemas. Field names follow the DoD Legal Structure Agent envelope so existing tooling maps one to one.

## 8. Repository layout *(A001)*

```
aoc-dfo/
  pyproject.toml            # single uv project, Python 3.12
  src/aoc_dfo/              # pins, build, extract, validate
  ontology/
    aoc-dfo.ttl             # top-level, imports all core modules
    aoc-domain.ttl  aoc-msgstruct.ttl  aoc-messages.ttl
    aoc-doctrine.ttl  aoc-flows.ttl  aoc-threads.ttl
    aoc-align.ttl           # alignment; not imported by aoc-dfo.ttl
    catalog-v001.xml        # IRI → local file for every import
    imports/                # vendored BFO and CCO at the shared pin + PINS.yaml
  shapes/
  catalog/                  # messages.csv, elements.csv, flows.csv
  corpus/                   # registry.yaml, text/ (Tier 1a only)
  corpus-controlled/        # gitignored guard; stays empty (OD-1)
  cq/
  data/synthetic/  data/threads/
  docs/                     # mapping-rules, conformance, cco-label-map, ensim-alignment, diagrams/
  .kiro/specs/aoc-dfo/      # requirements, design, tasks, amendments/
  .kiro/steering/           # pointer to umbrella steering + component notes
  HANDLING.md  AGENTS.md  README.md  LICENSE  NOTICE
```

Module boundary contract (`owl:imports`, checked in CI):

| Module | May import |
|---|---|
| `aoc-domain` | BFO, CCO |
| `aoc-msgstruct` | BFO, CCO |
| `aoc-messages` | `aoc-msgstruct`, `aoc-domain` |
| `aoc-doctrine` | `aoc-domain` |
| `aoc-flows` | `aoc-doctrine`, `aoc-messages` |
| `aoc-threads` | `aoc-flows` |
| `aoc-dfo` (top) | all six core modules |
| `aoc-align` | `aoc-dfo` and pinned partner ontologies; nothing imports it |

## 9. Design decisions

- **D-1** NIEM 6.0 MilOps first, MIM second, as canonical element vocabulary rather than USMTF. Rationale: public, structured, shared lineage; keeps the build Tier-2-independent. *(A001: MIM replaces JC3IEDM)*
- **D-2** Systems as implementations, not flow definitions. Rationale: TBMCS/KRADOS transition; standards outlive systems.
- **D-3** Structural module separated from domain. Rationale: CCO's ICE hierarchy does not model message syntax; keeping syntax separate preserves CCO purity and interoperability.
- **D-4** Unstructured flows (chat, briefings) modeled, not omitted. Rationale: a material share of real AOC flow; omitting them misrepresents dependency.
- **D-5** Generated shapes and diagrams only. Rationale: hand-authored artifacts drift from the catalog.
- **D-6** *(A001)* Channels are first-class classes, not strings. Rationale: capacity, fallback and interoperability attach later without restructuring.
- **D-7** *(A001)* Thread steps reference classes by punning, not by asserting hypothetical particulars. Rationale: keeps TBox and ABox apart and keeps BFO realism.
- **D-8** *(A001)* ENSIM names reused in the `dfo:` namespace. Rationale: umbrella steering; evaluation compares like with like.
- **D-9** *(A001)* Vendored imports with an XML catalog and hash check. Rationale: BFO's version IRI is undated; reproducible offline builds.

## 10. Decisions on the September open decisions *(A001)*

| ID | Decision | Where decided |
|---|---|---|
| OD-1 | Public sources only. Tier 1b and Tier 2 unavailable; task 4.5 placeholders; NATO surrogates only from official releases | Amendment 001 §A3 (2026-10-22) |
| OD-2 | Standalone repo `semanticarchitectures/aoc-dfo` | Umbrella ADR 0006 |
| OD-3 | Shared pin: BFO 2020 `release-2024-01-29`, CCO `v2.2` | Umbrella ADR 0006; pin table in umbrella ontology steering |
| OD-4 | No Foundry shaping; later projection by export adapter | Amendment 001 §A4 (2026-10-22) |

Open modeling questions MD-1 to MD-4 are listed in Amendment 001.

## 11. Risks *(A001)*

| Risk | Impact | Mitigation |
|---|---|---|
| Tier 1b and Tier 2 unavailable | Element detail limited to NIEM/MIM proxies; joint doctrine from 2019-era editions | D-1; gap report; placeholders; `dfo:supersededBy` |
| Scope creep toward full NIEM/MIM | Schedule | CQ gate (R6.4) |
| CCO ICE categories ambiguous for some fields | Inconsistent mapping | MR-2 decision table in mapping-rules.md; review gate |
| Public system docs too thin | Flows lack channel or system | Both optional; mark unknown, don't guess |
| Thread scenarios drift toward real TTPs | Classification exposure | R13.7 guardrail; review checklist item for every scenario PR |
| CCO 2.x IRI churn in a future pin | Broken references | Label map generated from the pin; pin changes only via umbrella |
| GMNS ontology not published at the shared pin | Alignment with GMNS deferred | Tracked in `aoc-align`; flagged to umbrella |
| Accidental CUI in public repo | Handling violation | HANDLING.md; corpus-controlled gitignored; CI grep for handling markings |
