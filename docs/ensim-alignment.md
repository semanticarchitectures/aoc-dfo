# ENSIM alignment

Status: draft (2026-10-22). Satisfies R14.1; becomes axioms in `ontology/aoc-align.ttl` as the
AOC-DFO classes are admitted (task 5.3).

ENSIM source, pinned: [semanticarchitectures/ENSIM](https://github.com/semanticarchitectures/ENSIM)
commit `aa7b714` (2026-09-15), `packages/org-doctrine-model/schema/*.schema.json` and generated
`types/*.ts`. ENSIM is a JSON Schema / TypeScript model, not OWL, so alignment is a mapping table.
ENSIM is not modified (umbrella portfolio: read as a pinned snapshot).

| ENSIM type | ENSIM fields (key) | AOC-DFO | Correspondence | Notes |
| --- | --- | --- | --- | --- |
| `Organization` | id, name | `cco:Organization` | same kind | AOC-DFO uses CCO's class directly |
| `Role` | id, name | BFO `role` subclasses | same kind | CCO 2.2 has no Organization Role |
| `C2Node` | organizationId, `function` ∈ {Tasking, Coordination, Reporting, ExecutionMonitoring}, producesArtifacts | `dfo:C2Node` ⊑ `cco:Organization` | same name, same kind | ENSIM `function` maps to the `dfo:DoctrineProcess` the node is agent of, not to a node attribute |
| `DoctrineProcess` | ordered `steps` (actor role/node/organization, producesArtifact) | `dfo:DoctrineProcess` ⊑ `cco:PlannedAct` | same name, same kind | ENSIM steps ≈ occurrent parts; `producesArtifact` ≈ `cco:has_output` a doctrinal product |
| `Decision` | roleId, informedBy (participants), criteria, possibleOutcomes | `dfo:Decision` ⊑ `cco:PlannedAct` | same name, same kind (chosen 2026-10-22: local, align later) | ENSIM `informedBy` lists participants; AOC-DFO `dfo:informedBy` lists artifact types. Reconcile at alignment |
| `System` | type ∈ {Aircraft, Communications, …}, commsLink | `dfo:C2System`; `cco:Aircraft` for aircraft | partial | ENSIM mixes platforms and C2 systems in one type; AOC-DFO splits them |
| `Interaction` | from, to, interactionType, commsLink, viaSystem | `dfo:DataFlow` ⊑ `cco:ActOfCommunication` | close | `from`→`cco:has_agent`, `to`→`cco:has_recipient`, `viaSystem`→`dfo:viaSystem`. Only interaction types Commands/Informs/CoordinatesWith are data flows |
| `CommsLink` | mode ∈ {Verbal, Digital, Mixed}, medium, protocol, format | `dfo:CommunicationChannel` + `dfo:FormatStandard` | close | `medium`/`protocol` → channel type; `format` → format standard |
| `Mission`, `MissionReport`, `TaskingRequest` | — | candidates: `dfo:MissionPackage`, MISREP product, AIRSUPREQ content | to review | Admit only under the CQ gate |

Divergences that would need an umbrella ADR (R14.2): none so far.
