# Amendment 002 — Citation form for classes, provenance module, NIEM USMTF vocabulary

- Status: Accepted (2026-11-11, approved by Kevin).
- Amends: AOC-DFO-REQ v1.1 (R1.2), AOC-DFO-DES v1.1 (§7, §8), AGENTS.md
- Found while building tasks 1.1 and 1.4.

## B1. Classes and properties cite with `dcterms:source`, not `prov:wasDerivedFrom`

**Problem.** Design §7 puts `prov:wasDerivedFrom` and `dfo:anchor` directly on classes. PROV-O
declares `prov:wasDerivedFrom` an object property. On a class it must be treated as an annotation
property, and OWL 2 DL forbids one IRI being both. The KB will import PROV-O for its own provenance
(umbrella tech steering), so the first time the KB and AOC-DFO are loaded together the merged
ontology would leave OWL 2 DL. A separate `dfo:anchor` also loses which anchor belongs to which
source when a class cites two.

**Change.**

| Cites | Property | Form |
| --- | --- | --- |
| Classes and properties (TBox) | `dcterms:source` (an annotation property) | `<https://w3id.org/aoc-dfo/source/<registry id>#<anchor>>` |
| Individuals: mission-thread steps, instance data (ABox) | `prov:wasDerivedFrom` | the same anchored IRI |

The anchor is the IRI fragment, so each citation carries its own anchor and `dfo:anchor` is
dropped. Each registry entry is one edition, so `…/source/<id>` is a source version, described as a
`prov:Entity` in its own named graph in `provenance/sources.trig`. That part is unchanged from §7
and from the umbrella's provenance rule.

**Requirement text.** R1.2 becomes: "WHEN an ontology class, property, message element, flow, or
transmission step is asserted THEN the system SHALL attach at least one citation of a registered
source version with an anchor: `dcterms:source` for classes and properties, `prov:wasDerivedFrom`
for individuals, in the form `…/source/<id>#<anchor>`."

## B2. A citation must resolve to text that exists

The SHACL shapes check form and that the source is registered and citable. Task 1.6 adds a stricter
gate (`aoc-dfo citations`, run in CI): the source must be **ingested** and the anchor must **exist**
in it. A registered but un-ingested source cannot be cited yet. This is how "every claim cites a
source" (umbrella product principle 1) becomes checkable rather than nominal.

## B3. Provenance vocabulary gets its own module

The terms that describe source versions (`dfo:sourceTier`, `dfo:edition`, `dfo:availability`,
`dfo:handlingCaveat`, `dfo:contentSha256`, `dfo:supersededBy`) live in a new module `aoc-prov`.
It imports nothing; `aoc-dfo` imports it. Design §8's contract table gains one row:
`aoc-prov` may import nothing.

Terms that exist because a requirement or the design needs them (provenance vocabulary now,
structural and mission-thread classes later) cite the approved design by section
(`…/source/AOC-DFO-DES-1.1#sec-7`) instead of naming a competency question. The design is
registered as a source for this purpose. Domain classes still need a CQ (R6.4).

## B4. NIEM 6.0 includes public, field-level USMTF vocabulary

NIEM 6.0's `usmtf` namespace ("Military Operations subdomain based on USMTF", Distribution A)
defines 5,719 properties and 5,700 types, every one with a definition. It is field-level
vocabulary, not USMTF message-set structure. Consequences:

- R5.1's canonical vocabulary is NIEM 6.0 `mo` **and** `usmtf`, ingested at tag `6.0-ps02`.
- Phase 4 (elements) can ground USMTF fields in a public source instead of creating
  `tier2-unavailable` placeholders for them. Placeholders remain for message-set structure
  (which fields form which set) and for Link 16 / VMF, which NIEM does not cover.
- The OD-1 decision is unchanged (public sources only). Its cost is smaller than assumed.
- NIEM's edition is **6.0 PS02** (29 Apr 2025), the newest in the official repo. The "6.0 OS"
  edition named in September could not be confirmed from here.

## B5. Other corrections

- AGENTS.md's provenance rule changes to the B1 form.
- MIM (secondary vocabulary) is not ingested yet: its site is not reachable from the build
  session. Task 1.4 is done for NIEM; MIM moves to the first task that needs it.

## Open question

- **OQ-1.** Should the umbrella record B1 as the shared citation form, so the KB cites the same
  way? It affects the shared model, so it is an umbrella decision. Until then it is AOC-DFO's.
  Raised as umbrella ADR 0011 (proposed 2026-11-11, acquisition-knowledge-system PR #1).
