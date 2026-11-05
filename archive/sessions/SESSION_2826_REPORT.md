# Session 2826 report: the share of fossil fuels in Europe's gross available energy (Eurostat, nrg_ind_ffgae), the session's own choice

26 October 2026, from about 06:54 to 06:58 UTC, on lab-desktop (the data machine), chain 144, unattended. Precheck passed (`runs/c144/pre2826.out`). Model spend USD 0. Pulls: 3 of 20 (2 by the probe, 1 by the fetch).

## Read these first

- **`eurostat_fossil_share_annual` is new:** Eurostat's share of fossil fuels in gross available energy (nrg_ind_ffgae), each European country's a year, 1990 to 2024.
  - 1,279 rows, 39 areas, in pct.
  - The table has been written, validated, archived and put in coverage. It is held from the live set and from Redivis storage until session 2829's draft.
- **Why this source:** the ERW holds the renewable shares (`eurostat_renewable_shares_annual`) and import dependency, not the fossil share of the supply. Session 2799's reading of Eurostat's dataflow list named it; no connector or chain holds it.
- **Figures:**
  - the EU27: 82.37 per cent in 1990, 68.12 in 2024;
  - lowest in 2024: Iceland 16.38, Sweden 32.06, Finland 34.07, France 46.99;
  - highest: Malta 94.91, Cyprus 88.62, the Netherlands 85.87, Poland 84.78.
- **Kept as published:**
  - Estonia's three shares above 100 (1990 103.79, 1991 102.19, 1992 100.96), counted in the header and listed in the run log;
  - the United Kingdom and Kosovo, left out.

  The connector's first trial stopped on Estonia's 1990 figure; a share outside 0 to 100 is now counted, not a stop.
- **Context, not a test:** this share plus the renewable share (`renewable_share_overall`, a share of gross final consumption, a different denominator) has a median of 97.6 over 743 country years. The two are not complements, and neither is read from the other.

## The requests

| n | What | Outcome |
|---|---|---|
| 1 | ec.europa.eu's robots file | 200, byte for byte session 2821's |
| 2 | nrg_ind_ffgae's data (probe) | 200 |
| 3 | the same, into the connector's raw folder | 200, byte for byte |

Reads recorded: 1646 and 1647.

## Decisions made without you

- **Shares above 100 kept,** as Eurostat publishes them.

## For Samuel's ruling

- None new.

## Files

- New:
  - `warehouse/connectors/eurostat_fossil_share.py`
  - `tests/test_session2826.py` (3 tests, passing)
  - this report
- Changed:
  - the table's registration and holds;
  - the license record (reads 1646 and 1647) and `docs/licenses.md`;
  - coverage, sources, the archive manifest and the release v1 records.
- On the data machine only:
  - `runs/c144/s2826/`, `runs/license_reads/s2826/`;
  - `warehouse/raw/eurostat_fossil_share/`.
