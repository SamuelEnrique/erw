# Session 954 report: critical minerals for storage and grids (the U.S. Geological Survey)

23 October 2026, from 12:31 UTC, on lab-desktop (the data machine), a session of `queue/done/054-day-23-october-data-federal-royalties-wind-costs-minerals.md`. Model spend USD 0. Pulls: 4 requests of 15 (ScienceBase's robots file, asked in a call of its own and read first; a catalogue search; the data release's item; its CSV).

## Read these first

- **One table written, validated, archived, in coverage (sector metals, public), in the release package, both holds:** `usgs_mcs_critical_minerals`, 692 rows, 299 series, 2021 to 2025, from the Mineral Commodity Summaries 2026 Data Release, "Commodity Salient U.S. and World Statistics" (one CSV of every chapter), for the six chapters the chain names: lithium, cobalt, nickel, natural graphite, copper and the rare earths. Each chapter's U.S. salient statistics (production, imports, exports, apparent consumption, prices, stocks, employment, net import reliance), its import sources (shares of 2021 to 2024) and world mine production and reserves by country.
- **Two units added to the vocabulary, the data standard and the validator together** (Decision 56): `t` (metric tons) and `USD/kg`. Thousand metric tons are written as `t` times 1,000; cents per pound as `USD/lb` over 100.
- **USGS's marks have no row:** 26 dashes (zero, as USGS prints it), 17 W (withheld to avoid disclosing company data), 7 s, 6 NA, 5 E (net exporter) and 15 bounds such as ">50"; each counted in the header.
- **The cross-checks:** copper (LME grade A cash) and nickel (LME cash) against `wb_commodity_prices_monthly`'s annual averages within 0.2 percent for 2021 to 2024 (copper 2024: 9,143 and 9,142 USD/t); cobalt (LME cash) against `imf_commodity_prices` within 1 percent for 2021 to 2024. USGS's 2025 figures are its estimates of early 2026 (copper 2.5 percent under the World Bank's year, nickel 1.1, cobalt 5). The IMF's lithium series is on another basis (it runs six to ten times USGS's battery-grade carbonate) and is not compared.

## Decisions made without you

- **The six chapters the chain names, not all 89:** the file holds every chapter; the others (manganese, vanadium, the heavy rare earths and the rest) are a later session's.
- **ScienceBase's content signals** ("ai-train=no, use=reference" for every reader) **read as no bar:** the ERW stores and serves the data and trains no model; USGS's data are in the U.S. public domain (verdict of session 496).
- **The file's Windows-1252 punctuation written plainly:** its em dash in "Salient Statistics" and "United States" as a colon, its en dashes as hyphens, so no em dash reaches the repository.
- **The import sources' period** (2021 to 2024) as `ts_utc` 2021-01-01 with `freq` P4Y.

## Errors

- **Two em dashes typed as escapes in the connector landed as the character** (the memory's warning); found by the dash count before the commit and replaced with `chr(0x2014)` by code point.
- **Until this chain lands, main's validator does not know `t` and `USD/kg`:** a coverage rebuild on this machine from main's code before the landing would mark this table blocked. The write ran with the branch's validator copied in and main's put back.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/usgs_mcs.py`, `tests/test_session954.py` (4 tests), this report.
- Changed: `warehouse/validate/erw_validate.py`, `docs/datastandard.md` (Decision 56), `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c054/s954/`, `runs/license_reads/s954/`, `runs/s954*`, `warehouse/raw/usgs_mcs/`.
