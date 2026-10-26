# Session 2827 report: the EU's energy import origin concentration by fuel (Eurostat, nrg_ind_ioc), the second own choice

26 October 2026, from about 06:58 to 07:03 UTC, on lab-desktop (the data machine), chain 144, unattended. Precheck passed (`runs/c144/pre2827.out`). Model spend USD 0. Pulls: 4 of 20 (2 by the probe, 2 by the fetch).

## Read these first

- **`eurostat_import_concentration_annual` is new:** Eurostat's energy import origin concentration index by fuel (nrg_ind_ioc). For each EU member, a year from 2015 to 2024, it measures how concentrated its imports of each fuel are on few countries of origin, from 0 (many origins) to 1 (one).
  - The fuels are 43, among them the total, electricity, natural gas, crude oil and the oil products, coal and peat.
  - 6,497 rows, 27 members. The sector is `power;gas;oil;coal`.
  - The table has been written, validated, archived and put in coverage. It is held from the live set and from Redivis storage until session 2829's draft.
- **Why this source:** it pairs with chain 141's import dependency (how much is imported) and session 2821's gas imports by origin (from whom, to 2020). This says how concentrated, and runs to 2024. Session 2799's reading of the dataflow list named it.
- **Figures, natural gas:**
  - Germany 0.4944 in 2020 and 0.3199 in 2024;
  - Italy 0.2678 and 0.2194;
  - Poland 0.3650 and 0.3229.
  - Electricity in 2024: Poland 0.4430, Germany 0.3065.
- **Cross-check against session 2821's gas origins, 2020:** where one partner is 100 per cent of a member's gas (Czechia, Latvia: Russia), this index is 1.0. Germany's 0.4944 sits with Russia at 68.66 per cent and Norway at 23.79, as a concentration measure would.
- **Kept as published:** 1,034 values of 1 (one origin). There are no blanks and no zeros. Every value lies between 0 and 1, which the connector checks.
- **A conflict at the write:** the sources patch met session 2821's row (both Eurostat's `nrg_ind_*`). It was resolved as the union (`runs/c124/resolve_union.py`) before any commit. No marker and no row twice remained.

## The requests

| n | What | Outcome |
|---|---|---|
| 1 | ec.europa.eu's robots file | 200, byte for byte session 2826's |
| 2 | nrg_ind_ioc's data (probe) | 200 |
| 3 | the same, into the connector's raw folder | 200, byte for byte |
| 4 | the SIEC codelist | 200 |

Reads recorded: 1648 and 1649.

## Decisions made without you

- **The sector set to every fuel's** (`power;gas;oil;coal`), as the index covers them all.

## For Samuel's ruling

- None new.

## Files

- New:
  - `warehouse/connectors/eurostat_import_concentration.py`
  - `tests/test_session2827.py` (4 tests, passing)
  - this report
- Changed:
  - the table's registration and holds;
  - the license record (reads 1648 and 1649) and `docs/licenses.md`;
  - coverage, sources, the archive manifest and the release v1 records.
- On the data machine only:
  - `runs/c144/s2827/`, `runs/license_reads/s2827/`;
  - `warehouse/raw/eurostat_import_concentration/`.
