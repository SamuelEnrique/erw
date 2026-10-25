# Session 2764 report: Austria's electricity balance a year from 1970 (Statistics Austria); queue file 141 written first

25 October 2026, about 23:26 to 23:42 UTC, on lab-desktop (the data machine), chain 140, unattended. Precheck passed first (`runs/c140/pre2764.out`). Model spend USD 0. Pulls: 11 requests of 15 (10 by the probe, 1 fetch of the file); two web searches.

## Read these first

- **Queue file 141 first:**
  - `queue/next/141-day-11-december-data-ladwp-austin-seattle-smud.md` (sessions 2778 to 2791) was written from file 140 by `runs/c140/write_141.py`, in chain 139's writer's form. It keeps the rules word for word.
  - 141 was the next free number, and 2778 to 2791 were free on main and on every branch.
  - **Its sources are four of the largest US public power utilities:** the Los Angeles Department of Water and Power, Austin Energy, Seattle City Light and SMUD. They come after chain 139's federal agencies. None is in the record, the queue or the unlanded chains' records. Each session reads its city portal's terms of use, and each names a held cross-check (EIA-930's balancing authorities, EIA-861's sales).
  - Pushed to main alone as `3c23ad4e`; snapshots `c140-q141-before` and `c140-q141-after` show **0 differences**.
- **Chain 140's worktree:** `erw-c140` on `wip/2764-2777-data`, from main at `c48733f2`.
- **`statat_austria_electricity_annual`, public, held from the live set and in the Stanford holds** (`warehouse/connectors/statat_energy_balance.py`, 6,675 rows, 117 entities, 8 variables, 1970 to 2024):
  - From "Energy balances Austria 1970-2024" (.ods, 10 MB, last modified 7 November 2025), sheet "Electricity", listed on Statistics Austria's energy balances page.
  - **The file is read by streaming its 263 MB content.xml with the standard library.** No ODS reader is installed, and none was added to the ERW's requirements.
  - The sheet gives its blocks in TJ and again in MWh; **the table reads the MWh blocks, so nothing is converted**:
    - the balance items: imports, exports, gross inland consumption (electricity's net imports), transformation input and output, the energy sector's use, transport losses, final energy use;
    - the transformation output by plant type (power, CHP, heating), owner (public, autoproducers) and fuel, with sub-fuels (hydropower by size, wind, PV, the biomass kinds);
    - final energy use by 21 sectors and their three totals;
    - the energy sector's use by branch, from 1999, where the sheet begins it.
  - Generation (the transformation output): 29,453,000 MWh in 1970, 59,855,089 in 2000, 78,753,844 in 2024. Final energy use: 20,219,998, 50,805,814 and 62,699,563.
  - **Checked every year within 1 MWh, all passing:**
    - gross inland consumption equals primary production plus imports, stock changes and recycling less exports;
    - final energy use equals the balance's remainder;
    - each parent row equals its parts;
    - the sectors make final energy use;
    - the branches make the energy sector's use.

    281 parent years whose fuel breakdown is not yet split (zero parts under a non-zero fuel, as the hydropower sizes before 2000) are counted, not checked. 96 rows that are 0 in every year (four balance items among them) are not written.
- **Cross-checks, both close:**
  - **Generation equals Eurostat's gross production less pumped hydro** (`eurostat_electricity_production_annual`, TOTAL less RA130) within 0.03 per cent: 49,296 against 49,296 GWh in 1990, 59,855 against 59,871 in 2000, 78,754 against 78,758 in 2024. Statistics Austria's balance leaves pumped storage generation out of the transformation output.
  - **Imports and exports equal E-Control's annual totals** (`econtrol_austria_electricity_monthly`, twelve months summed) within 4 GWh: imports 29,389 against 29,389 GWh (2015), 24,522 against 24,523 (2020), 18,923 against 18,927 (2024); exports 19,328, 22,327 and 25,703 against the same.
- **Terms and verdict:**
  - www.statistik.at's robots file closes only its search pages and names no Claude agent (read 1509); statistik.at redirects to it (read 1510). data.statistik.gv.at has no robots file (read 1511).
  - The open data portal is CC BY 4.0 (read 1512), but its 472 datasets hold no energy (read 1513).
  - The general terms, section 10 (read 1518, outcome exactly `read`): "Provided that the source "STATISTIK AUSTRIA" is cited, and the content is reproduced accurately, it is permitted to reproduce, distribute and make the content publicly available for both commercial and non-commercial purposes", with edits stated. **Verdict added: may be public** (`runs/c140/s2764_verdict.py`). The header credits STATISTIK AUSTRIA and states the ERW's edits.
- **Written under the data lock:** validated, archived (6,675 rows), in coverage. The patch applied cleanly with no marker. Coverage has 604 tables and `sources.csv` 694 sources, none twice. `finish_table.sh`: the release and license checks pass (604 tables, 252 verdicts, 0 problems).
- **Test 205's bound** is raised by 40 for this chain's reads, from 1509.

## Requests (11 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.statistik.at's robots file (its own request) | 200 |
| 2 | statistik.at's robots file (its own request) | redirected to www's, 200 |
| 3 | data.statistik.gv.at's robots file (its own request) | no file; redirected to the portal page |
| 4 | the open data portal's terms | 200, CC BY 4.0 |
| 5 | the open data portal's catalogue | 200, no energy datasets |
| 6 | www.statistik.at's English sitemap index | 200 |
| 7 | its pages sitemap | 200 |
| 8 | the energy balances page | 200 |
| 9 | the legal notice | 200, a disclaimer |
| 10 | the general terms and conditions | 200 |
| 11 | energy_balances_austria_1970-2024_data.ods (the fetch) | 200, 10,265,053 bytes |

Reads recorded: 1509 to 1518.

## Decisions made without you

- **The ODS read with the standard library,** not a new dependency.
- **The MWh blocks taken, the TJ blocks left:** the publisher's own MWh, so no conversion is the ERW's.
- **Rows 0 in every year left out,** counted in the header; zeros within a written row kept.
- **The monthly electricity statistics (2023 to 2026) not taken:** E-Control's monthly series is held already.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/statat_energy_balance.py`, `tests/test_session2764.py`, this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `coverage.csv`, `docs/coverage.md`, `sources.csv`, `archive_manifest.csv`, the license record (reads 1509 to 1518, one verdict), `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`, test 205's bound.
- On the data machine only: `runs/c140/s2764/`, `runs/c140/write_141.py`, `runs/c140/raise205.py`, `runs/c140/s2764_verdict.py`, `runs/license_reads/s2764/`, `warehouse/raw/statistik_austria/s2764eb/`.
