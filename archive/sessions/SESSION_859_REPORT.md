# Session 859 report: the unsettled licenses a read can settle

23 October 2026, from 02:11 UTC, on lab-desktop (the data machine), a session of `queue/done/046-night-22-october-data-sources-gaps.md`. Model spend USD 0.

## Read these first

- **The Federal Register is settled: "may be public".** The Government Publishing Office, which prints and publishes the Federal Register jointly with the Office of the Federal Register, states on govinfo.gov (record 91): "By virtue of the foregoing, public documents can generally be reprinted without legal restriction." (cut by code from the saved page, `runs/c046/s859/record.py`). federalregister.gov's own pages state no terms (record 67, and its API page, record 92). The verdict is in `license_verdicts.csv` under the Federal Register's key, its note naming the page it rests on.
- **No table's verdict or flag changed.** `large_load_rule_reads` and the four `policy_*` tables lose the Federal Register from their "not read" lists; the policy tables now wait on the Public Utility Commission of Texas alone, `large_load_rule_reads` on four state commissions. Nothing to list for the owner as a flag change.
- **Not settled:** CME Group reset the connection at its robots file (record 93; not asked again); FERC answers 403 (not worked around); the state commissions' pages read before hold no terms, and no other page of theirs was guessed at.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.govinfo.gov | 2 | robots file (allows `/about/`); the policies page |
| www.federalregister.gov | 2 | robots file; the API documentation page |
| www.cmegroup.com | 1 | robots file: connection reset |
| all | **5 of 20** | |

## Decisions made without you

- The Federal Register's verdict rests on its joint publisher's page (GPO), since its own site states no terms; the note says so, and the row can be removed if you would rather wait for OFR's own words.
- CME's reset not retried (a reset can be the host's refusal).

## For Samuel's ruling

- None new. The letters of `docs/state/unsettled_licenses_2026-10-19.md` stand, less the Federal Register's.

## Files

- New: this report. Changed: `warehouse/metadata/license_reads.csv` (91 to 93), `license_verdicts.csv`, `license_tables.csv`, `docs/licenses.md`. On the data machine only: `runs/c046/s859/`, `runs/license_reads/s859/`.
