# Amendment 001 — AKS role, shared pins, OD-1/OD-4, mission-thread layer

- Status: Proposed (2026-10-22). Takes effect when Kevin approves requirements v1.1.
- Amends: AOC-DFO-REQ v1.0, AOC-DFO-DES v1.0, AOC-DFO-TSK v1.0 (all 2026-09-04)
- Produces: AOC-DFO-REQ v1.1, AOC-DFO-DES v1.1, AOC-DFO-TSK v1.1
- Umbrella references: [ADR 0005](https://github.com/semanticarchitectures/acquisition-knowledge-system/blob/main/docs/adr/0005-one-model-many-apps.md),
  [ADR 0006](https://github.com/semanticarchitectures/acquisition-knowledge-system/blob/main/docs/adr/0006-aoc-dfo-repo-and-shared-ontology-pins.md),
  [ontology steering, Pinned versions](https://github.com/semanticarchitectures/acquisition-knowledge-system/blob/main/.kiro/steering/ontology.md),
  [vision](https://github.com/semanticarchitectures/acquisition-knowledge-system/blob/main/docs/vision.md)

The September spec was written before AOC-DFO became part of the Acquisition Knowledge System
(AKS). This amendment records what changed, decides the two open decisions that remained with
AOC-DFO (OD-1, OD-4), and adds the mission-thread layer. It follows the umbrella rule: requirements
first, then design, then tasks.

## A1. AOC-DFO's role in AKS (new context)

Under ADR 0005 (one shared model, many apps), AOC-DFO is part of the shared model, not a standalone
analysis artifact. It now has three jobs, in order of horizon:

| Horizon | Job | Consequence for this spec |
| --- | --- | --- |
| Near | Reference ontology of AOC data flows, built from public doctrine | Unchanged scope (R1–R12) |
| Near | **Alignment target for the KB's acquisition ontology** (umbrella ontology steering, "Align with AOC-DFO so the two graphs join without remapping") | Same BFO/CCO pin as the KB (A2); stable IRIs; ENSIM names reused (A7); new R14 |
| Far | **AOC side of the interface between unmanned mission plans and the AOC** (vision, demonstration thread step 4) | Mission-thread layer (A6) must be able to express an unmanned-platform endpoint and a machine-to-machine channel. Not built now; one competency question and a gap entry keep it in view |

AOC-DFO is a dependency of the KB, never the reverse (umbrella portfolio arrows). Nothing in this
repo may import the KB ontology.

## A2. ADR 0006: standalone repo, shared pins

- **OD-2 (decided by ADR 0006): standalone repo** `semanticarchitectures/aoc-dfo`. The September
  design's "uv workspace member" and monorepo fold-in language is removed. It is a single uv
  project.
- **OD-3 (decided by ADR 0006): shared pin.** Pins are recorded in the umbrella's ontology steering
  and copied here, never chosen here:

  | Ontology | Pin | Commit | File SHA-256 |
  | --- | --- | --- | --- |
  | BFO 2020 | tag `release-2024-01-29` | `044490fc5100ffed6df7d4d15cbc167698b6fdee` | `src/owl/bfo-core.ttl` `6944e2c9…8443a3b` |
  | CCO | `v2.2` (version IRIs `…/2026-08-13/…`) | `0bc7d33e1bc09fd4693366119ab4e03cb0340042` | `src/cco-merged/CommonCoreOntologiesMerged.ttl` `a9453382…baadb42` |

- **Consequences found while selecting the pin** (all now reflected in design v1.1):
  1. BFO's version IRI is the undated PURL, and CCO 2.2 imports that PURL. AOC-DFO vendors both
     files under `ontology/imports/`, resolves IRIs through `catalog-v001.xml`, and CI checks the
     hashes. Nothing resolves over the network.
  2. CCO 2.x uses opaque IRIs. The spec keeps label shorthand (`cco:InformationContentEntity`) for
     readability; `.ttl` files use the IRIs, and `docs/cco-label-map.md` lists every CCO term the
     spec names with its IRI.
  3. CCO 2.2 has **no Directive Information Content Entity**. The ICE subclasses are Descriptive,
     Designative, Prescriptive, Representational, Media Content Entity, Ideology and Religion.
     Design MR-2 and §3.1 change "Directive" to **Prescriptive**. CCO 2.2's `Message` (under Media
     Content Entity) and `Report` are new reuse candidates for message content.
  4. CCO 2.2 has **no Military Organization** and **no Organization Role**. Use `Organization` and
     `Government Organization`; `Armed Force` exists for force-level entities. Roles use BFO `role`
     or CCO's specific role classes.

## A3. OD-1 resolved: public sources only

**Decision:** v1.0 uses only information available to the general public. Kevin has no CAC access
to JEL+ or to JITC/DISA standards, and the umbrella's Phase 1 is public data only.

**Consequences:**

- **Tier 1b becomes unavailable**, not merely unverified. Current joint publications (JP 3-30 2025,
  JP 3-60 2024, JP 3-09 2025, JP 3-52 2022, JP 3-01 w/Ch1, JP 2-0 w/Ch1, JP 6-0, DOD Dictionary) are
  registered by title and date as `unavailable`. Where an earlier edition is public (for example
  JP 3-30, 25 Jul 2019, on the FAS mirror), that edition is the working source, every assertion from
  it carries `dfo:supersededBy` pointing at the current edition, and the gap report lists it.
- **Tier 2 stays unavailable** for the life of v1.0. Task 4.4 is removed; task 4.5 (placeholders)
  executes. `corpus-controlled/` stays in `.gitignore` as a guard, but nothing is ever put there.
- **NATO surrogates** (ADatP-3, ATDLP-5.16, STANAG 5516) are registered as `verify-availability`.
  They are ingested only from an official NATO public release. Unofficial mirrors are excluded.
- **Fidelity ceiling is explicit.** The model is authoritative at node, product and flow level and
  hypothesis-level below it. Element-level detail comes from NIEM 6.0 MilOps and the MIP Information
  Model, labeled as public proxies.
- AFMAN 13-1AOC Vol 3 (25 Jun 2024, no releasability restrictions) is the primary source and is
  ingested first.

## A4. OD-4 resolved: Foundry later, by projection

**Decision:** do not shape AOC-DFO classes for Foundry object types. Foundry gets a projection of
the graph later, through an export adapter.

**Reason:** the umbrella already decides this for the whole shared model. Product principle 7 and
tech steering say Foundry/Envision attaches "through adapters, never rewrites" and is "a projection
of the graph, never the authoritative copy"; the KB does the same with a SPARQL CONSTRUCT export
(KB R10). Shaping AOC-DFO for Foundry now would bend the shared model toward one platform.

**What stays in the design so the projection is easy later:** stable IRIs, n-ary nodes for
relationships with their own attributes (flows, steps), and no anonymous structure that a CONSTRUCT
query cannot flatten. The Foundry export is out of scope for v1.x.

## A5. Corrections carried from the September corpus registry

The registry findings recorded in September (registry `findings:` block) are now applied to the
spec text:

| Was | Now | Source |
| --- | --- | --- |
| AFDP 3-30, Command and Control | **AFDP 3-0.1** (22 Jan 2025) supersedes it; AFDP 3-30 Appendix B kept as a superseded secondary source | AFDP 3-0.1; Air Force Doctrine Smart Book (4 Jul 2026) |
| AFDP 3-1 | **AFDP 3-01**, Counterair Operations (15 Jun 2023) | Smart Book |
| JP 2-01 | **JP 2-0** (w/Ch 1) and the Joint Guide for JIPOE | jcs.mil doctrine status (25 Mar 2025) |
| JC3IEDM as secondary vocabulary | **MIP Information Model (MIM)**; JC3IEDM for legacy alignment only | mimworld.org |
| NIEM-MilOps (unversioned) | **NIEM 6.0** (OASIS NIEMOpen) | docs.oasis-open.org |
| AFI 13-1AOC Vol 3 | **AFMAN 13-1AOC Vol 3** (25 Jun 2024), primary | e-Publishing |
| TBMCS as the system layer | **KRADOS** (AOC Block 20) with app-level components; TBMCS as Block 10.1 legacy | kesselrun.af.mil OpsC2 page |

## A6. Mission-thread layer (new module `aoc-threads`)

**Why:** the primary analysis goal is design-time mission-thread traceability: decision → data →
channel → endpoint, for hypothetical (planned) threads, not logged operations. The September design
models doctrinal flows (who sends what to whom, at which ATO stage) but has no way to string flows
into an ordered thread for one scenario. The far-horizon unmanned-to-AOC interface is analyzed the
same way.

**The six classes and where they land:**

| Class (spec name) | Implemented as | CCO 2.2 parent | Notes |
| --- | --- | --- | --- |
| MissionThreadScenario | `dfo:MissionThreadScenario` | `cco:Plan` (Prescriptive ICE) | Analyst-authored. One instance = one hypothetical thread, e.g. "CAS tasking to a fighter flight, Link 16 degraded" |
| Decision/Task | `dfo:Decision`, `dfo:Task` | `cco:PlannedAct` | Reuses ENSIM's name `Decision` (A7). Anchors a thread to the doctrine layer's processes |
| InformationArtifactType | Not a class. The **role a class plays**: any subclass of `cco:InformationContentEntity` in `aoc-doctrine` or `aoc-messages`, flagged `dfo:isInformationArtifactType true` | — | Avoids a metaclass. Doctrinal products and message types *are* the artifact types |
| TransmissionStep | `dfo:TransmissionStep` | `cco:PrescriptiveInformationContentEntity`, part of a scenario | Ordered. Says which artifact type, over which channel type, from which decision, between which endpoint roles. Optionally realizes a doctrinal `dfo:DataFlow` |
| ChannelType | `dfo:CommunicationChannel` and subclasses (Link 16 network, voice net, chat, …) | `cco:TelecommunicationNetwork` | First-class so capacity, fallback and interoperability attributes can be added later without restructuring. Face-to-face and courier media carry no channel (open question MD-3) |
| EndpointRole | `dfo:EndpointRole` and subclasses | BFO `role` | Borne by organizations (AOC divisions, TACS nodes) or platforms. Capability profiles are subclasses defined by what the bearer has, e.g. "fighter with a Link 16 terminal". Never a specific airframe |

**The pattern that keeps TBox and ABox apart.** Scenarios and steps are real individuals: they are
documents an analyst wrote. What a step is *about* (an artifact type, a channel type, an endpoint
role, a decision type) is a class. Steps refer to those classes through annotation properties
(`dfo:stepArtifactType`, `dfo:stepChannelType`, `dfo:stepFromDecision`, `dfo:stepSenderRole`,
`dfo:stepReceiverRole`), which is OWL 2 punning and keeps the ontology in OWL 2 DL. SHACL-SPARQL
constraints check that each referenced IRI is a subclass of the right root. This means a scenario
never asserts that a hypothetical aircraft or ATO exists.

**Degraded and alternate paths** (resilience, a secondary goal) are just more scenarios, or steps
with `dfo:fallbackFor` pointing at the step they replace. No new classes.

**Far horizon, kept in view, not built:** one competency question (CQ-T6, below) asks which steps in a
scenario have an unmanned-platform endpoint role and which channel types they use. In v1.1 it is
expected to return an empty result plus a gap entry: public sources do not describe unmanned-to-AOC
interfaces in detail (vision guardrail 5).

**Classification guardrail** (carried from the September design discussion): steps stay at "class of
data over class of channel". Scenarios do not record timing, capacity numbers, net assignments or
fallback sequences drawn from real operations.

## A7. Alignment with the shared model

- **ENSIM names.** The umbrella ontology steering says to reuse ENSIM's org-doctrine names and to
  record any divergence in an ADR. AOC-DFO adopts them in its own namespace: `dfo:C2Node`,
  `dfo:DoctrineProcess`, `dfo:Decision`, with `Organization` and role classes from CCO/BFO. The
  September names change: `dfo:AOCFunction` becomes `dfo:DoctrineProcess`; AOC divisions, teams and
  external nodes become subclasses of `dfo:C2Node` (itself an `cco:Organization`). ENSIM's
  `Interaction` (from, to, `commsLink`, `viaSystem`) corresponds to `dfo:DataFlow`; its `CommsLink`
  (mode, medium, protocol, format) corresponds to `dfo:CommunicationChannel` plus the format
  standard. The mapping is a table in `docs/ensim-alignment.md`; ENSIM is not modified.
- **Decision class (choice made 2026-10-22).** `dfo:Decision` is local to AOC-DFO and aligned later.
  Using ENSIM's name keeps this inside the steering rule, so no umbrella ADR is needed now. If the
  KB ontology or decision-traces spec later needs one shared `Decision` class, that is an umbrella
  ADR.
- **Provenance is PROV-O.** The umbrella mandates PROV-O and one named graph per source version.
  The ProvenanceEnvelope stays as the required *pattern* (document, edition, date, anchor, tier,
  handling caveat) but is expressed in PROV-O: each source version is a `prov:Entity` in its own
  named graph; each assertion links to it with `prov:wasDerivedFrom` and carries `dfo:anchor`,
  `dfo:sourceTier` and `dfo:handlingCaveat`. A SHACL shape enforces the pattern. There is no
  bespoke envelope class.
- **Tooling matches the umbrella:** ROBOT for builds, reasoning (HermiT) and QC reports; pySHACL for
  validation; Python 3.12; uv. Ontology changes go through PRs with the motivating CQ and a ROBOT QC
  report.
- **Echelons do not apply.** AOC-DFO is a reference ontology, not echelon-scoped data. The KB's
  L0–L4 named-graph sets do not apply here.

## A8. Process and governance changes

- The spec moves to this repo's `.kiro/specs/aoc-dfo/`, matching the umbrella layout. Design §8's
  `specs/` directory is replaced.
- Requirement IDs are cited as `R<n>.<m>` (Requirement n, criterion m), matching umbrella
  conventions. Tasks cite `_Requirements: R…_`.
- "import-linter" (R12.2) is for Python imports and cannot check `owl:imports`. Module boundaries are
  enforced by an `owl:imports` contract test instead; R12.2 already allows "or equivalent".

## Open modeling questions (one line each, for review)

- **MD-1.** `MissionThreadScenario ⊑ cco:Plan` treats a hypothetical thread as prescriptive. If
  reviewers prefer descriptive-of-a-hypothetical, the alternative parent is Representational ICE.
- **MD-2.** `dfo:Task`: is a task the act tasked (`PlannedAct`, chosen) or the tasking content
  (Prescriptive ICE)? The doctrinal product (e.g. the ATO line) already covers the content.
- **MD-3.** Non-network media (face-to-face brief, courier) have no `CommunicationChannel`. Record
  the medium as an annotation, or add a `dfo:DirectMedium` class under a CQ?
- **MD-4.** No public source yet describes what a TransmissionStep's sender/receiver roles are for
  an unmanned mission-planning system talking to the AOC. Left as a gap (CQ-T6).
