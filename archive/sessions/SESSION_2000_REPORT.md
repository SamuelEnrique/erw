# Session 2000 report: energy jobs by state and technology (the 2026 U.S. Energy and Employment Report)

23 October 2026, from 15:00 UTC, on lab-desktop (the data machine), the first session of `queue/done/056-evening-23-october-data-jobs-reactors-large-loads-hydro.md`, taken while chain 055 was unfinished (below). Model spend USD 0. Pulls: 5 requests of 15 (www.energy.gov's robots file, asked in a call of its own and read first: it allows `/documents/` and `/policy/`; the USEER page; the public data workbook; the national report, for the cross-check; the workbook again by the trial).

## Read these first

- **Chain 057 written and pushed first:** `queue/next/057-night-23-october-data-wholesale-solar-industry-buildings.md` (sessions 2014 to 2027, machine: data: EIA's wholesale hub prices, Berkeley Lab's Tracking the Sun, EIA's manufacturing and buildings surveys, a gap of the undescribed tables, the licenses' eleventh round and the rest in chain 040's form), committed alone and pushed to main (`374fe79b`; `git status -sb` showed nothing ahead), with a snapshot pair (`c056-057-before`, `-after`: 0 differences; the deploy succeeded at 15:02 UTC). The queue move of 056 went first with its own pair (`c056-take-before`, `-after`: 0 differences). 2014 to 2027 were free: the bare numbers in other files are years.
- **Chain 055 was unfinished when chain 056 was taken:** its agent had stopped at 14:19 UTC in session 987 (no other Claude process on the machine; its worktree untouched for 36 minutes), with sessions 985 (its write waiting for the lock), 987, 988, 990 and 991 not done. This agent finished them first where it could (987 at once; 985 when the lock was free), since chain 056 reads chain 055's note and builds on its landing. Chain 056's branch (`wip/2000-2013-data`) starts from chain 055's.
- **One table written, validated, archived, in coverage (sectors power, gas, oil and coal, public), in the release package, both holds:** `doe_useer_employment`, 3,311 rows: the 2026 USEER's employment in 2025 by sector, technology and industry for the nation (with 2024's totals), and by sector and technology in each state and DC (and USEER's one row of Puerto Rico and the U.S. Virgin Islands).
- **The cross-check against the report's own summary:** 8,380,422 energy workers in 2025 (the report: 8.4 million), -86,277 from 2024 (-86,000); electric power generation 919,031 (919,000), fuels 1,025,930 (one million), energy efficiency 2,360,303 (2.4 million), motor vehicles 2,582,820 (2.6 million), transmission, distribution and storage 1,492,338 (1.5 million, +28,679 against +28,000). The states' sector totals are within 0.06 to 0.80 percent of the nation's.
- **A publisher's error, not taken:** the workbook's "2025 TDS Employment" block holds one row, "TDS Total", which repeats the "Pumped Hydro" storage row figure for figure; the T&D and storage blocks hold the same workers, so nothing is lost.

## Decisions made without you

- **Chain 055 finished before chain 056's own work,** where the lock allowed (above); the reversible choice is the order.
- **The USEER's figures kept as published,** survey estimates with decimals, not rounded to whole workers.
- **The workforce characteristics sheets not taken** (shares by sex, ethnicity, race and the rest).

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/doe_useer.py`, `tests/test_session2000.py` (5 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On main: `queue/next/057-night-23-october-data-wholesale-solar-industry-buildings.md`.
- On the data machine only: `runs/c056/s2000/`, `runs/license_reads/s2000/`, `runs/s2000*`, `warehouse/raw/doe_useer/`.
