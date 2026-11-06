# Session 2926 report: the siting gaps file and the records

6 November 2026, about 05:47 to 05:58 UTC, on lab-desktop (the data machine), chain 153, unattended. Model spend USD 0. Pulls: none.

## Read these first

- **`docs/reviews/siting-gaps.md`:** a new section, "State on 6 November 2026, early morning (chain 153)", one line for every row this chain moved or read:
  - filled: signed agreements, and the Texas wires utility's revenue for the county rows;
  - TPIT moved to October;
  - held but not drawn: the tariffs and the connection rules;
  - open: 4CP 2026 and the interruptible riders.
  - The table above it is unchanged, so `gaps.json` is the same (checked). Commit `50e106a01`.
- **The records after the new table `large_load_connection_rules`** (commit `a9295354d`):
  - `scripts/licenses.py tables`, `write`, `check`: 633 tables, 259 publishers with a verdict, 1,649 requests in the record, **0 problems**.
  - `package/tools/build_tables.py`: `--check` first found the new table missing. It was rebuilt twice, because the second build had to follow the license record. `--check` now exits 0: 633 tables (public 467, internal 114, unsettled 52). The new table is "unsettled" in the package, as `utility_large_load_tariffs` is: neither registry's publisher has a verdict row.
  - `warehouse/redivis/release_v1.py`: `--check` first found 1 difference (the new table). After `--out-dir` (the main checkout's tables) it gives 0 differences. The package's `tables.csv` now carries the fetch columns throughout (`fetch_python`, `fetch_stata`), which is why its diff touches every line. `variables.csv` gains the new table's 26 columns and those of two tables written since it was last built (`ercot_wind_solar_hsl_monthly`, `usgs_mcs_critical_minerals`).
  - Tests of sessions 1001, 1008, 1009 and 1010, and every test that reads the release or the license files: **376 passed, 10 skipped**.
- **The method notes against their code:**
  - `docs/methods/large_load_tariffs.md` said each row cites a commission's copy. PG&E's rows cite its own filed tariff book, so a paragraph now says so and names the owner's question.
  - `large_load_connection_rules.md` (session 2924) and `siting.md` version 9 (session 2923) were written with their code.
  - `ercot_tpit`'s docstring names the July workbook as of 23 October, which the table's header now supersedes. It was left as dated text.

## Decisions made without you

- **The release package rebuilt from the main checkout's tables**, as chain 147's session 2874 did.

## For Samuel's ruling

- None new.
