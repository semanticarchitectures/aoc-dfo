# Handling

This repository is public. It holds **public, unclassified content only** (NFR-3, R12.5).

## Never commit

- Classified material of any level.
- Controlled Unclassified Information (CUI), including FOUO legacy material.
- Tier 1b content: current joint publications obtained from JEL+ or any CAC-gated site.
- Tier 2 content: MIL-STD-6040 (USMTF), MIL-STD-6016 (Link 16), MIL-STD-6017 (VMF), MTF-XML
  schemas, system ICDs, AFTTP 3-3.AOC, theater SPINS.
- NATO documents not officially released to the public, or any copy from an unofficial mirror.
- Real operational or exercise data, including in mission-thread scenarios (R13.7).

Under OD-1 (Amendment 001) this project has no access to Tier 1b or Tier 2, so none of it should
ever be present. `corpus-controlled/` is in `.gitignore` as a guard only.

## Mission threads

Scenarios stay at "class of data over class of channel". Do not record timing, capacity, net
assignments or fallback sequences drawn from real operations, even from public reporting, if
together they would describe a real TTP. When in doubt, leave it out and record a gap.

## Automated tripwire

CI scans text files for banner and portion markings, FOUO caveats, restrictive distribution
statements and NOFORN (`src/aoc_dfo/handling.py`). It is a tripwire, not a review. Passing it
does not make content releasable.

## If something slips in

Do not push. If already pushed, tell the repository owner at once; removing it needs history
rewriting and possibly a spill report, which is the owner's call.
