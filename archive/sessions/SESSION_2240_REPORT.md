# Session 2240 report: Brazil's energy balance an hour by subsystem (ONS's open data)

24 October 2026, from 03:24 UTC, on lab-desktop (the data machine), the third session of `queue/done/101-day-4-november-data-france-spain-brazil-australia.md`, unattended. Model spend USD 0. Pulls: 11 requests of 15 (below).

## Read these first

- **ONS's terms read first.**
  - dados.ons.org.br's robots file disallows `/api/` and asks a crawl delay of 10 seconds (read 370). Its dataset pages are allowed, so the CKAN API was not used, and the page requests were spaced at least 10 seconds apart.
  - The open data bucket on S3 has no robots file (read 372).
  - **The dataset page** (read 371) gives a new verdict, may be public in both columns, under CC BY: "Ao acessar este site e/ou utilizar as informações provenientes dele, será considerado que você aceitou os termos e condições da LICENÇA CC-BY, que permite que os reutilizadores distribuam, modifiquem, adaptem e desenvolvam o material sobre os dados, desde que seja dado o crédito apropriado ao criador(ONS) e que informe quais alterações foram feitas." The changes are named in the header: wide to long, the hour placed in UTC.
- **One table written, validated, archived, in coverage (sector power), in the release package, both holds:** `ons_brazil_balance_hourly`, 2020 to 22 October 2026, 1,790,640 rows.
  - Five entities: the four subsystems (North, Northeast, South, Southeast/Centre-West) and the national interconnected system (SIN).
  - Six measures in MW, the hour's mean (ONS's "MWmed", its data dictionary, read 373): hydro, thermal, wind, solar, load and net interchange.
  - **The hour placed in UTC from Brasília time.** ONS's files and dictionary state no time zone, but solar generation peaks at 11:00 to 12:00 on their clock, which is local noon, not 15:00. Brasília keeps UTC-3, with no daylight saving since 2019.
  - **As published, not reconciled:**
    - Net interchange equals generation minus load to within 1 MW in about 96% of the hours (1,834 to 2,440 hours a subsystem break it).
    - The four subsystems sum to SIN except in some hours, most of them in 2026 (wind up to 15,423 MW apart). ONS says its data are being made consistent after publication.
- **The cross-check** (`runs/c101/s2240/cross.py`, `cross.out`): SIN's load a year is 0.852 to 0.916 of Ember's Brazilian demand from 2020 to 2025, rising. For example, 2025 is 697.374 against 762.12 TWh.
  - SIN is the interconnected grid, without Brazil's isolated systems or generation behind the meter. Which explains the gap and its narrowing is not tested here.
  - Wind and solar rose from 10.7% of SIN generation in 2020 to 29.6% in 2025.

## The pulls

1. dados.ons.org.br/robots.txt (read 370).
2. The energy balance dataset page (read 371), 10 seconds after.
3. The bucket's robots file (read 372): HTTP 404.
4. to 10. The seven yearly files, 2020 to 2026. They were seeded into the raw store, and the trial and the write read them offline.
11. The data dictionary (read 373).

## Errors

- **The docstring first said net interchange equals generation minus load.** It did on the Northern subsystem's 2025 file, the one tried. The cross-check found the hours where it does not, and the docstring and header now say so. The table was written after the correction.

## Decisions made without you

- **The energy balance by subsystem** rather than generation by plant. It gives the same fuels nationally and by region, with load and interchange, at a fraction of the size, within the ceiling.
- **Brasília time inferred from the solar peak,** stated in the header as an inference.
- **ONS's inconsistencies kept as published,** counted, not corrected.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/ons_balance.py`, `tests/test_session2240.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`
  - `warehouse/metadata/license_reads.csv` (370 to 373), `warehouse/metadata/license_verdicts.csv` (ONS)
  - the coverage, sources, archive manifest and license files
  - `docs/redivis/release-v1/`
- On the data machine only: `runs/c101/s2240/`, `runs/license_reads/s2240/`, `runs/s2240_*`, `warehouse/raw/ons_balance/`.
