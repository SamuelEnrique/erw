# Session 2832 report: the diversity index of the EU's energy supply (Eurostat, nrg_ind_di), the third own choice (run before 2829)

26 October 2026, from about 07:03 to 07:07 UTC, on lab-desktop (the data machine), chain 144, unattended. Precheck passed (`runs/c144/pre2832.out`). Model spend USD 0. Pulls: 3 of 20 (2 by the probe, 1 by the fetch). Run before session 2829, as file 144 asks, so that 2829's notes and draft take this table.

## Read these first

- **`eurostat_supply_diversity_annual` is new:** Eurostat's diversity index of energy supply (nrg_ind_di), for each EU member a year, 1992 to 2024.
  - 891 rows, 27 members, unit `index`, written as Eurostat gives it.
  - The file gives the index without its method, so the ERW reads no direction into it ("more diverse" or "less") beyond Eurostat's own metadata, which the note points to.
  - The table has been written, validated, archived and put in coverage (sector `power;gas;oil;coal`). It is held from the live set and from Redivis storage until session 2829's draft.
- **Why this source:** beside session 2827's import concentration and chain 141's import dependency, it completes Eurostat's supply-security indicators in the ERW. Session 2799's reading of the dataflow list named it.
- **Figures, 2024:** the lowest values are Czechia 0.1166, Austria 0.1230 and Finland 0.1292; the highest are Lithuania 0.3599, Malta 0.3478 and Greece 0.3360. Every value lies between 0 and 1, which the connector checks.
- **No cross-check against a held table:** none gives the same index.
- **The connector** was made from session 2826's by exact replacements (`runs/c144/s2832/make_connector.py`), and checked by code for anything left of the original.
- **A conflict at the write:** the sources patch met session 2826's row. It was resolved as the union before any commit. No marker and no row twice remained.

## The requests

| n | What | Outcome |
|---|---|---|
| 1 | ec.europa.eu's robots file | 200, byte for byte session 2827's |
| 2 | nrg_ind_di's data (probe) | 200 |
| 3 | the same, into the connector's raw folder | 200, byte for byte |

Reads recorded: 1650 and 1651.

## Decisions made without you

- **The index written without an interpretation of its direction.**

## For Samuel's ruling

- None new.

## Files

- New:
  - `warehouse/connectors/eurostat_supply_diversity.py`
  - `tests/test_session2832.py` (3 tests, passing)
  - this report
- Changed:
  - the table's registration and holds;
  - the license record (reads 1650 and 1651) and `docs/licenses.md`;
  - coverage, sources, the archive manifest and the release v1 records.
- On the data machine only:
  - `runs/c144/s2832/`, `runs/license_reads/s2832/`;
  - `warehouse/raw/eurostat_supply_diversity/`.
