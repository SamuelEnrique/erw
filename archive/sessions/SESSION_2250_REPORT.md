# Session 2250 report: the shale gas reserves (EIA, 2007 to 2021), a third source of the session's own choosing

24 October 2026, from 03:49 UTC, on lab-desktop (the data machine), the thirteenth session of `queue/done/101-day-4-november-data-france-spain-brazil-australia.md`, unattended. Model spend USD 0. Pulls: EIA's API, 11 requests of 20 (below).

## Read these first

- **Why this source:**
  - Shale gas is most of U.S. gas production. The ERW held EIA's production, wells and dry gas reserves, but not the shale reserves by state with their yearly changes.
  - It was chosen among the EIA routes the ERW does not hold, listed in this session. It is not one of queues 102's and 103's sources (PSE, Elia or Energy-Charts' Belgium, EMI, the Northwestern Division's dams, Eskom, the Coordinador, XM, Taipower).
- **A closed record, said so:** EIA's route gives 2007 to 2021, and its shale gas production route also ends in 2021. The table is not a running series, and its header says so.
- **One table written, validated, archived, in coverage (sector gas), in the release package, both holds:** `eia_shale_gas_reserves_annual`, 2007 to 2021, 4,455 rows, 469 series, in bcf (already in the vocabulary).
  - The measures: proved reserves, reserves-based production, revisions up and down, sales, acquisitions, extensions, discoveries, and adjustments.
  - Areas: the U.S., the lower 48, the federal offshore, 23 states, and the districts within California, Louisiana, New Mexico and Texas.
  - A district's geo is its state's, so states and districts overlap: a sum takes one level.
- **The cross-check** (`runs/c101/s2250/cross.py`, `cross.out`):
  - **EIA's reserves balance closes exactly for the U.S.** in every year from 2009 to 2021 but 2020: last year's reserves, plus extensions and discoveries, plus revisions, plus acquisitions, less sales, plus adjustments, less production.
  - **2020 is EIA's own:** the reported figure is 596 bcf above the computed one.
  - **The states' sum** is 0.997 to 1.000 of the U.S.
  - U.S. shale proved reserves rose from 23,304 bcf (2007) to 393,779 (2021), production from 1,293 to 27,985 bcf a year.

## The pulls

1. and 2. The petroleum and natural-gas routes' children.
3. The third level of four routes (natural-gas/enr, /stor, /prod, petroleum/stoc): 4 requests.
4. The shale gas route's metadata and all its data (2 requests, kept as the sample).
5. The shale gas production route's metadata (it also ends in 2021).
6. The trial's two pages. The write reused them (0 requests).


## Errors

- None.

## Decisions made without you

- **EIA's shale gas reserves as the session's own choice,** though it ends in 2021, because it is the only public record of the shale reserves by state, and their yearly changes.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia_shale_gas_reserves.py`, `tests/test_session2250.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`
  - the coverage, sources, archive manifest and license files
  - `docs/redivis/release-v1/`
- On the data machine only: `runs/c101/s2250/`, `runs/s2250_*`, `warehouse/raw/eia_shale_gas_reserves/`.
