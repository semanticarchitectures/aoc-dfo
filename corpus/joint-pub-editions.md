# Public editions of CAC-gated joint publications (task 1.7)

Status: **candidates found 2026-11-11; JP 3-30 decided (Amendment 003); none downloaded yet.** The hosts below are blocked
from the build session, so editions, dates and hashes are from search results, not from the files.
Each becomes a registry entry (`superseded_by` the current edition) only after its file is
downloaded, its title page checked, and its SHA-256 recorded.

Current editions are CAC-gated on JEL+ and stay `unavailable` (OD-1). R1.6 allows only official
government or standards-body releases.

| Pub | Current (unavailable) | Newest public edition found | Host | Official? |
| --- | --- | --- | --- | --- |
| JP 3-30 Joint Air Operations | 2025 | 25 Jul 2019 | irp.fas.org; aerospace.csis.org | **No** (FAS, CSIS are not government) |
| JP 3-30 (older) | | 10 Feb 2014 | nsarchive.gwu.edu | No (university archive) |
| JP 3-30 (older) | | 12 Jan 2010 | apps.dtic.mil (ADA513761) | Yes (DTIC) |
| JP 3-60 Joint Targeting | 2024 | 28 Sep 2018 | esd.whs.mil (DoD FOIA reading room, 21-F-0520) | Yes |
| JP 3-52 Joint Airspace Control | 2022 | 13 Nov 2014 | edocs.nps.edu | Yes (Naval Postgraduate School) |
| JP 3-09 Joint Fire Support / Joint Fires | 2025 | 10 Apr 2019 (likely) | irp.fas.org | No; older editions on UNT CyberCemetery and webharvest.gov (NARA) archives of dtic.mil |
| JP 3-01 Countering Air and Missile Threats | 2024 (w/Ch 1) | 2017–2018 | irp.fas.org; defenseinnovationmarketplace.dtic.mil (summary) | FAS no; the DTIC item may be a summary, not the pub |
| JP 2-0 Joint Intelligence | 2024 (w/Ch 1) | 22 Oct 2013 | everyspec.com | No; older on webharvest.gov (NARA) |
| JP 6-0 Joint Communications | 2023 | 2019 (likely) | irp.fas.org | No; 10 Jun 2010 on edocs.nps.edu (official) |

Sources: search results 2026-11-11 for each title (links in the table's hosts):
[irp.fas.org JP 3-30](https://irp.fas.org/doddir/dod/jp3_30.pdf),
[CSIS JP 3-30](https://aerospace.csis.org/wp-content/uploads/2019/09/JointAirOperations_jp3_30.pdf),
[DTIC ADA513761](https://apps.dtic.mil/sti/tr/pdf/ADA513761.pdf),
[WHS FOIA JP 3-60](https://www.esd.whs.mil/Portals/54/Documents/FOID/Reading%20Room/Joint_Staff/21-F-0520_JP_3-60_9-28-2018.pdf),
[NPS JP 3-52](https://edocs.nps.edu/2014/December/jp3_52.pdf),
[irp.fas.org JP 3-09](https://irp.fas.org/doddir/dod/jp3_09.pdf),
[irp.fas.org JP 3-01](https://irp.fas.org/doddir/dod/jp3_01.pdf),
[NPS JP 6-0 2010](https://edocs.nps.edu/dodpubs/topic/jointpubs/JP6/JP6-0_100610.pdf).

## Decision (R1.6) — Amendment 003, 2026-11-11

Kevin chose option 2 for **JP 3-30 only**: the 25 Jul 2019 edition is used from an archive
(irp.fas.org; CSIS as a second host), with its host, retrieval date, SHA-256 and the caveat
"archived copy of a publicly released edition; not an official host" recorded on `JP-3-30-2019`
in the registry and in `provenance/sources.trig`. The registry check rejects any other source on a
non-official host. The 2010 DTIC edition was the strict alternative and is not used.

Still undecided: JP 3-09, JP 3-01, JP 2-0 and JP 6-0, whose newest public editions are also only on
archives. Official-host candidates (JP 3-60 2018 via WHS, JP 3-52 2014 and JP 6-0 2010 via NPS)
need no amendment.

**Download status.** Both archive hosts and the official .mil hosts refuse non-browser clients from
the build session (HTTP 403, or a 202 challenge page from FAS; CSIS is not on the allowlist). The
files have to be fetched from a browser and then hashed.
