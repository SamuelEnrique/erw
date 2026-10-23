# Session 888 report: the licenses' third round

23 October 2026, from 05:05 UTC, on lab-desktop (the data machine), a session of `queue/done/048-night-23-october-data-utility-files-products.md`. Model spend USD 0. Pulls: 10 requests of 20, two a host, each host's robots file first (reads 97 to 106).

## Read these first

- **`uswtdb_wind_turbines` is settled: public, agreeing with its flag.** Its publisher name, "U.S. Geological Survey (USGS), with LBNL and ACP", matched no verdict, so it was "not settled". USGS's verdict (read 87, session 496: "USGS-authored or produced data and information are considered to be in the U.S. Public Domain") was already in the record. A name rule in `scripts/licenses.py` now maps it: the database is a USGS data release, and its header says so.
- **FERC answered its robots file without a challenge for the first time.** Its policy page still answers HTTP 403 (as in read 58), so FERC has no verdict. Its 8 EQR tables, and PUDL's 21 FERC Form 714 tables (held internal "until a person rules"), stay unsettled.
- **Catalyst Cooperative (PUDL) already had a verdict** (read 85, session 484). This session read PUDL's documentation front page before finding it: the same CC-BY-4.0 line. No second verdict was written, and its FERC Form 714 tables are left unmatched on purpose, waiting on FERC's page.
- **The state commissions linked from pages already read:**
  - Oregon's commission's pages link the State of Oregon's terms and conditions. They cover warranties, privacy, trademarks and a DMCA notice, but grant no reuse of content.
  - Arizona's Corporation Commission links only a privacy policy, which grants no reuse; its host has no robots file.
  - Pennsylvania's commission's pages link no terms page.
  - So `large_load_rules` and `large_load_rule_reads` stay unsettled.
- **The record now:** 326 tables. Flag and verdict agree on 240 (239 before); disagree on 0; 41 are not settled (42 before). The ERW's verdict: 223 public (221 before session 887; the CER's table and USWTDB), 54 internal, 49 unsettled.

## Decisions made without you

- Every request of the round is recorded, the failed and the repeated included, each under a label of its own (one row a publisher).
- `test_session205`'s bound on the record's size was raised by 20 for chain 048's sessions 887 and 888 (12 reads), each under its own ceiling. The bound dated from session 311's sweep.
- No guessed terms address was asked: the state commissions were read only where a page already read links one, as the queue file says. The tax agencies and DOE are not linked from any saved page.

## For Samuel's ruling

- PUDL's FERC Form 714 tables (21) and FERC's EQR tables (8) wait on FERC's own terms, which answer 403 to the ERW. A ruling that FERC's filings are U.S. government works, or a read from another network, would settle 29 tables.

## Files

- New: `tests/test_session888.py` (3 tests), this report.
- Changed: `scripts/licenses.py` (the USGS name rule), `tests/test_session205.py` (the bound), `warehouse/metadata/license_reads.csv` (97 to 106), `license_tables.csv`, `docs/licenses.md`.
- On the data machine only: `runs/c048/s888/` (probe, record and fix scripts), `runs/license_reads/s888/`.
