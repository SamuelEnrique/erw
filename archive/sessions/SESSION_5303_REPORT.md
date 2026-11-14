# Session 5303 report: the third pass, the states' large-load laws

13 and 14 November 2026, unattended, `portable-laptop` window P4 (Opus 5.5, xhigh). Branch `wip/5300-large-load`. Nothing built, nothing landed, no warehouse data written.

## Read these first

- **`docs/research/large_load/legislation_2026-11-13.csv`: 28 laws and bills from 26 states,** each read in the legislature's own text or the state code. All 295 cites match.
- **Statuses:** 10 in effect, 6 enacted, 4 passed, 3 passed one chamber, 3 introduced, 1 vetoed, 1 died.
- **Texas S.B. 6 is withheld.** capitol.texas.gov's robots file disallows `/TLODOCS/`, and the reader had fetched `/tlodocs/` because Python's check is case-sensitive.
  - The entry is out, the cached copy is deleted, and the reader now compares robots rules in both cases.
  - S.B. 6's rules still appear through 16 TAC 25.194, read in the PUCT's own documents.

## What was done

- **Two groups:** the South and West (7 laws after the withholding), and the Midwest and Northeast (21).
- **Both were cut off by this machine's network outage and resumed.**
  - Utah S.B. 132's status now comes from the Legislature's own bill record: in effect 7 May 2025.
  - Delaware's H.B. 233 was read on the legislature's own page (signed 26 August 2026).

## What was found

- **Enacted or in effect:**
  - Oregon's POWER Act (20 MW).
  - Utah S.B. 132 (100 MW).
  - Idaho Code 61-335 (50 MW, effective 1 July 2026).
  - Florida CS/CS/SB 484 (50 MW).
  - South Carolina Act 41 of 2025 (50 MW).
  - Virginia's 2026 act (25 MW).
  - Minnesota 216B.1622.
  - Missouri S.B. 4.
  - New Jersey P.L. 2026 c.32.
  - Maryland Ch. 625 of 2025 and Ch. 353 of 2026.
  - Delaware H.B. 233.
  - Nebraska LB 1010 (20 MW).
  - Kansas S.B. 98.
  - Michigan PA 207 of 2024.
  - West Virginia H.B. 2014.
- **Passed, no signature shown in the documents read:** Alabama SB 270 (Act 2026-610, 150 MW), Indiana HEA 1007 (internal: IN.gov), South Dakota SB 135, New York A11560 (both houses, 4 June 2026).
- **Could not be read:**
  - Oklahoma: its legislature and OSCN refuse by robots.
  - California: leginfo's robots answers 403.
  - Georgia: the bill site is built by script.
  - Tennessee: no official source found.

## Decisions made without you

1. **A robots rule is read in both cases.** A server may treat paths without regard to case, so the reader refuses a path that a rule bars as written or lower-cased. Allow lines keep their force: CenterPoint's `/api/public/` stays allowed.
2. **A retry after this machine's own network failure.** The Midwest and Northeast group retried, once, Missouri pages that had failed when DNS failed for every host, as a certificate failure is retried once.
