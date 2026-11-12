# Amendment 003 — Archived copy of JP 3-30 (2019)

- Status: Accepted (2026-11-11). Kevin decided: use the archived 2019 edition and record its provenance.
- Amends: AOC-DFO-REQ v1.1 (R1.6)
- Background: `corpus/joint-pub-editions.md` (task 1.7).

## Problem

R1.6 (from Amendment 001) allows only official government or standards-body releases. JP 3-30,
the joint air operations doctrine AOC-DFO depends on most, has no official public copy newer than
12 Jan 2010 (DTIC ADA513761). The 25 Jul 2019 edition, the newest one ever released publicly, is
hosted only by non-government archives (irp.fas.org; aerospace.csis.org). The current 2025 edition
is CAC-gated and stays `unavailable` (OD-1).

## Change

R1.6 gains one exception, for JP 3-30 only:

> THE system SHALL ingest a source only from an official government or standards-body release, and
> SHALL NOT ingest unofficial mirrors, EXCEPT the 25 Jul 2019 edition of JP 3-30 (registry id
> `JP-3-30-2019`), which MAY be ingested from a non-government archive WHEN its title page shows
> that edition and date and a public-release distribution statement, and its host, retrieval date
> and SHA-256 are recorded in the registry.

## How the provenance is recorded

| Where | What |
| --- | --- |
| `corpus/registry.yaml`, `JP-3-30-2019` | `url` = the archive copy fetched; `archive: true`; `handling` = "archived copy of a publicly released edition; not an official host"; `retrieved`, `sha256` once downloaded; the CSIS copy noted as a second host |
| `provenance/sources.trig` | `prov:atLocation` (host), `dfo:handlingCaveat` (the caveat above), `prov:generatedAtTime`, `dfo:contentSha256`, `dfo:supersededBy` → `JP-3-30` |
| Registry check | a source on a non-official host must carry `archive: true`, and only `JP-3-30-2019` may (so the exception cannot spread silently) |

Every assertion citing JP 3-30 cites `…/source/JP-3-30-2019#<anchor>`, so the caveat and
`dfo:supersededBy` travel with it. Anchors re-anchor to the 2025 edition if it ever becomes
public.

## Not changed

Other joint publications in `corpus/joint-pub-editions.md` whose newest public edition is only on
an archive (JP 3-09, JP 3-01, JP 2-0, JP 6-0) are not covered. Each needs its own decision.
