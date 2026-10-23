# Session 909 report: chain 052 written first; every country's electricity (EIA's International Energy Statistics)

23 October 2026, from 07:39 UTC, on lab-desktop (the data machine), the first session of `queue/done/051-day-23-october-data-world-gas-hydro.md`. Model spend USD 0. Pulls: EIA, 6 requests of 20 (api.eia.gov's robots path, two counts of the API's records, the API's country list, www.eia.gov's robots file, and the bulk file `INTL.zip`).

## Read these first

- **Chain 052 written and pushed first:** `queue/next/052-day-23-october-data-world-oil-reactors-stocks.md` (sessions 923 to 936, machine: data), committed alone and pushed to main (`f214d8d5`) with a snapshot pair (0 differences), before any other work. At 07:47 UTC chain 049's last session took 052 from the queue by mistake and put it back (`19833548`); it waits for this chain's session 922.
- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `eia_world_electricity_annual`, 332,254 rows, 4,421 series, 1980 to 2024, 264 areas: 213 countries with a 2024 figure, 7 former countries (the Soviet Union, Yugoslavia, Czechoslovakia, the two Germanies, Serbia and Montenegro, the Netherlands Antilles), 2 parts of a country (the Hawaiian Trade Zone, the U.S. Pacific Islands) and EIA's regions and groups (the world, continents, OECD, OPEC, the IEO regions). Each area's generation and capacity by source, consumption, imports, exports, net imports and distribution losses, EIA's billion kWh as MWh and its million kW as MW, in the entity form of session 886's table (`eia_intl:<EIA code>:<product>`). A column `x_area` says which kind each area is, so a sum over countries takes `country` and `former` only.
- **Read from EIA's bulk file, not the API:** the API counts 399,208 electricity records from 1980 (80 pages of 5,000), four times the session's ceiling. EIA's bulk download of the same statistics (`https://www.eia.gov/opendata/bulk/INTL.zip`, 24 MB, last modified 19 October 2026) holds them in one request, with the same 399,208 values; robots allows `/opendata/`. Session 923 (the world's oil and gas) can read the same saved file with no request.
- **The cross-checks:**
  - **The U.S., Canada and Mexico against session 886's table, read from the API:** 4,131 rows in both, none in one only, every value equal (largest difference 0) and every node name equal.
  - **The world against the countries summed** (country and former), each year 1980 to 2024: total generation, total capacity, consumption and nuclear generation within 0.01 percent in all 45 years; solar within 0.03 percent in the 42 years with a world figure above zero.
- **The world in 2024:** generation 30,664 TWh (coal 10,387, natural gas 6,648, hydro 4,512, nuclear 2,735, wind 2,512, solar 2,090), capacity 9,758 GW. China 10,162 TWh, the U.S. 4,393, India 2,052, Russia 1,160, Japan 907, Brazil 737.
- **Negative values kept as EIA gives them:** 2,404 rows of pumped storage's net generation (a plant uses more than it gives back), 2,506 net imports, and one consumption figure (Sierra Leone, 2009, minus 1,900 MWh), which looks like an error of EIA's and is named here, not mended.

## Decisions made without you

- **The bulk file in place of the API the queue file named,** since the API's pages for every country are four times the ceiling; the values are the same (the cross-check above).
- **`geo` left empty:** EIA's codes are three-letter and its own; no ISO 3166 code is guessed (the validator's `geo` takes two-letter codes, and the ERW has no checked map). The code is in the entity, the name in `node`.
- **A source id of its own, `eia:international_bulk`,** so that session 886's connector and this one do not write each other's description over in `sources.csv`.
- **The U.S., Canada and Mexico kept in this table too,** so the world table sums on its own; session 886's table stays as it is.

## For Samuel's ruling

- None new.

## Errors

- **This machine's first request to www.eia.gov's robots file carried a User-Agent naming the owner's e-mail address,** typed by hand in a one-line probe instead of the connectors' User-Agent. Every request after it, and the connector, sends the ERW's own (`ERW-connector/0.1`, the repository's address). Nothing else was sent.
- api.eia.gov has no robots file: its `/robots.txt` answers HTTP 403 with EIA's "API_KEY_MISSING", as any path does without a key.

## Files

- New: `warehouse/connectors/eia_intl_bulk.py`, `tests/test_session909.py` (4 tests), this report, `queue/next/052-day-23-october-data-world-oil-reactors-stocks.md` (on main).
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c051/`, `runs/s909*`, `warehouse/raw/eia_intl_bulk/`.
