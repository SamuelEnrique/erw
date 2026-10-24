# Session 2244 report: the crude oil U.S. refineries run (EIA's API gravity and sulfur), a source of the session's own choosing

24 October 2026, from 03:37 UTC, on lab-desktop (the data machine), the seventh session of `queue/done/101-day-4-november-data-france-spain-brazil-australia.md`, unattended. Model spend USD 0. Pulls: EIA's API, 6 requests of 20 (below).

## Read these first

- **Why this source:** the quality of the crude a refinery runs shows how the U.S. slate has moved with shale oil, and it sets refinery yields and margins. The ERW held EIA's refinery inputs, production and capacity, but not their quality. No queue file plans it, and EIA's verdict is on record (public domain). Session 2243 found Eskom closed by its terms and Taiwan's platform unanswered, so this session and the next take EIA data.
- **One table written, validated, archived, in coverage (sector oil), in the release package, both holds:** `eia_crude_quality_monthly`, January 1985 to July 2026, 15,968 rows.
  - 32 series: the average API gravity and sulfur content of the crude run, for the U.S., the five PADDs and the refining districts.
  - Weighted averages: an area's figure is not the sum of its parts, and the header says so.
- **A new unit, `degAPI` (Decision 73),** in the data standard and the validator together. It was agreed with chain 102's agent, whose Decisions start at 74. EIA's unit "D" is degrees API. Sulfur is percent by weight (`pct`).
- **The cross-check** (`runs/c101/s2244/cross.py`, `cross.out`): the U.S. figure against the five PADDs' figures, weighted by each PADD's crude oil input to refineries (`eia_refinery_inputs_monthly`).
  - Over the 259 months both tables hold, they agree to a median 0.023 degrees API (at most 0.090) and 0.003% sulfur (at most 0.010).
  - The U.S. figure never falls outside its PADDs' range (499 months).
  - The U.S. crude run went from 32.46 degrees API in 1985 down to 30.20 in 2005, and back up to 33.75 in 2025. Sulfur peaked near 1.42% in 2005 and was 1.30% in 2025.

## The pulls

1. The route's metadata (frequencies, facets, 1985-01 to 2026-07).
2. One page of 2025, to read the processes, areas and units.
3. to 6. The trial's four pages (1985 on). The write reused them (0 requests).

EIA's key is read from `.env` and never saved: the probe's copies replace it with `<key>`.

## Errors

- **The cross-check's first filter took "crude oil and petroleum products" with "crude oil",** doubling every PADD. It was narrowed to crude oil alone and run again.
- **A page address the connector's template guessed** (an EIA data browser page never read) was meant to be replaced by the API route before any run, but the replacing command failed unseen, so the first write carried it in its header and `sources.csv`. Session 2245 found it, set the route in its place and wrote the table again offline (the same 15,968 rows).

## Decisions made without you

- **EIA's crude quality as the session's own choice,** for the reasons above.
- **`degAPI` as Decision 73,** rather than writing gravity under another unit.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia_crude_quality.py`, `tests/test_session2244.py`, this report.
- Changed:
  - `docs/datastandard.md` and `warehouse/validate/erw_validate.py` (Decision 73)
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`
  - the coverage, sources, archive manifest and license files
  - `docs/redivis/release-v1/`
- On the data machine only: `runs/c101/s2244/`, `runs/s2244_*`, `warehouse/raw/eia_crude_quality/`.
