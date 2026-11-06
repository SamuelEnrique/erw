# Session 2820 report: queue file 145 written first; MAVIR not taken (its robots files close every path); Europe's non-household electricity by consumption band (Eurostat, nrg_pc_205_v) in its place

26 October 2026, from about 06:25 to 06:35 UTC, on lab-desktop (the data machine), chain 144, unattended. Precheck passed first (`runs/c144/pre2820.out`). Model spend USD 0. Pulls: 7 requests of 15 (6 by the probe, 1 by the fetch).

## Read these first

- **Queue file 145 first:**
  - `queue/next/145-day-15-december-data-seps-ast-ems-nosbih.md` (sessions 2834 to 2847) was written from file 144 by `runs/c144/write_145.py`, made by exact replacements from chain 143's writer (`runs/c144/make_write_145.py`). It keeps the rules word for word.
  - 145 was the next free number, and 2834 to 2847 were free on main and on every branch.
  - **Its sources are four more European transmission system operators:** Slovakia's SEPS, Latvia's AST, Serbia's EMS and Bosnia and Herzegovina's NOS BiH. None is in the record, the queue or the unlanded chains' branches.
  - Pushed to main alone as `2020b116`; snapshots `c144-q145w-before` and `c144-q145w-after` show **0 differences**.
- **Chain 144's worktree:** `erw-c144` on `wip/2820-2833-data`, from main at `2020b116`.
- **Test 205's bound** is raised by 40 for this chain's reads, from 1629.
- **MAVIR not taken: its robots files close every path to every reader.** www.mavir.hu's and mavir.hu's robots files both say `User-Agent: *`, `Disallow: /` (reads 1629 and 1630). Nothing else was asked; the host is closed.
- **Eurostat's TEN00119 asked again once** through the probe (read 1632): still HTTP 403, "temporarily unavailable", as at 05:13 UTC.
- **In MAVIR's place, `eurostat_nonhousehold_bands_annual`:** Eurostat's non-household consumption volumes of electricity by consumption bands (nrg_pc_205_v), 2017 to 2025. For each country it gives the share of non-household electricity used in each of the seven price-statistics bands, IA (under 20 MWh a year) to IG (150,000 MWh and over).
  - 2,013 rows, 37 countries, in pct. Eurostat's EU and euro-area rows are blank.
  - The table has been written, validated, archived and put in coverage. It is held from the live set and from Redivis storage until session 2829's draft.
- **Why this source:** these are the bands of Eurostat's non-household electricity prices (nrg_pc_205, in EUR, not taken). The volumes say how much of a country's use each price band stands for, and how concentrated its industrial demand is. Session 2799's reading of the dataflow list named it; no connector or chain holds it.
- **Figures, 2025:**
  - **Norway: 50.6 per cent of non-household use by consumers of 150,000 MWh a year and over**;
  - Ireland 22.5, Germany 22.2, France 16.5, Poland 8.6.
- **The check:** the seven bands make 100 within 0.5 points in all 216 country years that give all seven (within 0.01). No held table gives the same measure.
- **Kept as published:**
  - 56 zeros;
  - 249 blanks, with no row;
  - Kosovo, left out.

## The requests

| n | What | Outcome |
|---|---|---|
| 1, 2 | www.mavir.hu's and mavir.hu's robots files (each its own request) | 200, `Disallow: /` to every reader |
| 3 | ec.europa.eu's robots file | 200, byte for byte session 2818's |
| 4 | TEN00119's data (probe) | HTTP 403, temporarily unavailable |
| 5 | nrg_pc_205_v's data (probe) | 200 |
| 6 | the NRG_CONS codelist (probe) | 200 |
| 7 | nrg_pc_205_v's data, into the connector's raw folder | 200, byte for byte |

Reads recorded: 1629 to 1634.

## Decisions made without you

- **MAVIR's host closed at its robots files.** A Eurostat table was taken in its place rather than another Hungarian host: Hungary's statistics office was closed by an earlier chain, and its grid figures are held through Energy-Charts.

## For Samuel's ruling

- None new.

## Files

- New:
  - `warehouse/connectors/eurostat_nonhousehold_bands.py`
  - `tests/test_session2820.py` (4 tests, passing)
  - this report
- Changed:
  - `tests/test_session205.py` (the bound);
  - the table's registration and holds;
  - the license record (reads 1629 to 1634) and `docs/licenses.md`;
  - coverage, sources, the archive manifest and the release v1 records.
- On the data machine only:
  - `runs/c144/make_write_145.py`, `runs/c144/write_145.py`, `runs/c144/raise205.py`, `runs/c144/s2820/`, `runs/license_reads/s2820/`;
  - `warehouse/raw/eurostat_nonhousehold_bands/`.
