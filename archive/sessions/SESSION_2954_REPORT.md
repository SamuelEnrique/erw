# Session 2954 report: the queues (with session 2953)

6 November 2026, about 08:21 to 08:25 UTC, on lab-desktop (the data machine), chain 157 (the owner's), unattended. Model spend USD 0. Pulls: none.

## Read these first

- **The landing request file** (the rules): `docs/state/landing_request_portable.md` is not on origin's main, so there is no laptop branch to land here. Session 2947's landing of chain 152's Ask branch is in its gate.
- **`iso_queue_snapshot_summary` is written:** 1,039 rows, public, commit `ff570ca49`. It is a table of its own: `interconnection_queue_summary` is session 95's, from Berkeley Lab's file, and was not overwritten.
  - **Inputs:** the six ISO snapshots held: CAISO, ERCOT and ISO-NE of 19 October, SPP of 26 October, MISO of 30 September (held as before the pause; nothing asked of MISO), NYISO of 26 September.
  - **Each table holds one snapshot**, which its next pull replaces, so withdrawals and completions between snapshots cannot be counted. The queues' own dates stand for them.
  - **The snapshot:** MW and requests by grid, status and fuel group. Active MW: ERCOT 298,606, MISO 257,207, SPP 134,797, CAISO 73,848, NYISO 30,875, ISO-NE 10,801.
  - **By year:** MW and requests entered, completed and withdrawn.
  - **Months from request to in-service**, by request year, the median only at 5 or more: CAISO 18 years written, NYISO 13, SPP 16, ERCOT 8. ISO-NE and MISO give no in-service date.
  - **A fault found and ruled out:** SPP's `actual_in_service_date` holds requested dates (1,321 of its 1,969 dated rows lie after its snapshot, on active and withdrawn requests too). A date counts only on a completed request, on or before the snapshot. The first trial, before the rule, gave SPP's 2026 requests a 29-month median.
  - **A recent year's median counts only the requests already in service**, so it understates; the method note says so.
- **The write:** validator PASS, coverage (a rule added), archive run `20261106T082317Z-local`. Method note `docs/methods/iso_queue_snapshot_summary.md`; test `tests/test_session2953.py` (4 passed).
- **The siting gaps rows:** "generation with a signed interconnection agreement" stays filled from Berkeley Lab's file (chain 153). The ISO snapshots carry no agreement date. "A large load's own wait" stays open: these are generator queues. NYISO's load queue is license-held and was not an input.
- **Session 2954** had no second half: the table was finished in this one.

## Decisions made without you

- **A new name, `iso_queue_snapshot_summary`,** so that session 95's table keeps its own.
- **SPP's in-service dates read only where the request is completed** and the date has passed.

## For Samuel's ruling

- **Keeping each Monday's queue snapshot** (the archive keeps the latest file only), so that withdrawals between snapshots can be counted.
