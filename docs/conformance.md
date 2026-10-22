# AOC-DFO conformance checklist

Status: v0.1 (2026-10-22). Satisfies R6.6 until GMNS publishes its `ontology-conformance-spec.md`;
then the two are reconciled by amendment. Each rule cites where it comes from and how it is checked.

| # | Rule | Source | Check |
| --- | --- | --- | --- |
| C1 | BFO 2020 and CCO are imported unchanged at the shared pin; vendored files match the pinned SHA-256 | Umbrella ontology steering (tiers, pinned versions); R6.1, R6.7 | `tests/test_pins_and_catalog.py` (CI) |
| C2 | Every `owl:imports` resolves to a local file through `ontology/catalog-v001.xml`; nothing is fetched over the network | NFR-4 | `tests/test_pins_and_catalog.py`; ROBOT job uses the catalog |
| C3 | Module imports match the contract in design §8; nothing imports `aoc-align` | R12.2, R14.3, MR-6 | `tests/test_module_contract.py` |
| C4 | The full import closure is consistent under HermiT, with no unsatisfiable classes | NFR-1 | CI `robot` job (`reason`) |
| C5 | ROBOT QC report has no ERROR on AOC-DFO terms | Umbrella ontology steering, change control | CI `robot` job (`report --fail-on ERROR`) |
| C6 | Every new class or property names the CQ that requires it (`rdfs:comment` cites a CQ ID present in `cq/register.yaml`) | Umbrella ontology steering (mid-level tier); R6.4, MR-4 | Review now; automated check with task 2.6 |
| C7 | Every asserted class, flow and transmission step has `prov:wasDerivedFrom` a registered source version and a `dfo:anchor` | Umbrella tech steering (PROV-O); R1.2, R8.6 | ProvenanceEnvelope SHACL shape (task 1.1) |
| C8 | One SHACL shape per class and per n-ary relation | Umbrella ontology steering (shapes tier) | Generated shapes (tasks 6.1, 9.2) |
| C9 | Relationships that change over time are n-ary nodes with `validFrom`/`validTo` | Umbrella ontology steering (time) | Review; most AOC-DFO content is type-level and time-invariant, so applies to instance data only |
| C10 | Spec `cco:` shorthand resolves to exactly one CCO 2.2 term; ontology files use IRIs | MR-9 | `tests/test_registry_and_spec.py` |
| C11 | Turtle is canonical | NFR-2 | `tests/test_canonical.py` |
| C12 | Public, unclassified content only | NFR-3, HANDLING.md | `tests/test_handling.py` (tripwire) + review |
| C13 | Shared names (ENSIM `C2Node`, `DoctrineProcess`, `Decision`) are used as-is; divergence needs an umbrella ADR | Umbrella ontology steering (alignment); R14.1, R14.2 | Review; `docs/ensim-alignment.md` |
| C14 | Published IRIs are stable; terms are deprecated, never deleted | R14.4 | Review from the first release |

Not applicable: echelon named-graph scoping (KB L0–L4). AOC-DFO is a reference ontology, not echelon-scoped data.
