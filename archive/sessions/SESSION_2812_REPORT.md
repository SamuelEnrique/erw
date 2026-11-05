# Session 2812 report: Europe's nuclear fuel cycle facilities and nuclear heat (Eurostat, nrg_inf_nuc), the session's own choice

26 October 2026, from about 05:13 to 05:20 UTC, on lab-desktop (the data machine), chain 143, unattended. Precheck passed (`runs/c143/pre2812.out`). Model spend USD 0. Pulls: 8 of 20.

## Read these first

- **TEN00119 first, not available:** session 2799's reading of Eurostat's dataflow list named TEN00119, the market share of the largest generator in each electricity market. The API answered HTTP 403, "NOT_AVAILABLE: The data is temporarily unavailable". `fetch_raw` retried it three times, so **four requests were spent on one address**. A single probe of the next dataset showed the API itself answering. TEN00119 is left for a later chain.
- **`eurostat_nuclear_fuel_cycle_annual` is new:** Eurostat's nuclear energy facilities (nrg_inf_nuc), 2009 to 2024. Each European country's:
  - enrichment capacity, in SWU (Eurostat's tSWU times 1,000);
  - the production and capacity of fresh fuel, MOX fuel and reprocessing plants, in tonnes of heavy metal (unit `t`);
  - nuclear heat production, in MWh (Eurostat's ktoe times 11,630).

  4,247 rows, 40 areas, 8 items. The table has been written, validated, archived and put in coverage. It is held from the live set and from Redivis storage until session 2815's draft. Its sector is `power;uranium`, as the ERW's other nuclear tables.
- **Why this source:** the ERW holds the US fuel cycle (EIA's uranium marketing, enrichment prices) and Europe's nuclear generation, but not Europe's fuel cycle plants. No connector, note or unlanded chain names it.
- **Figures, 2024:**
  - enrichment capacity: France 7.5 million SWU, the Netherlands 5.0, Germany 3.5; the EU 16.0;
  - reprocessing: France alone in every year;
  - nuclear heat: the EU's 1,801 TWh.
- **Cross-check: nuclear electricity over nuclear heat.** `eurostat_electricity_production_annual`'s nuclear gross production (N900H) divided by this table's heat gives a **median of 0.34 over 231 country years** (5th to 95th percentile 0.33 to 0.37): a plant's thermal efficiency.
  - France 2023: 338.2 TWh from 1,025.0 TWh of heat (0.33).
  - **France's 2024 heat (88,138 ktoe, flag p) is 2023's figure carried forward:** with 2024's 380.5 TWh of electricity it gives 0.37. Kept as published; the note says so.
- **Not written:** the burnup of discharged fuel (BAA_IRRADF, GWd/tHM, 543 observations), a unit the ERW does not hold. Kept as published:
  - 3,610 zeros (most countries have no fuel cycle plant);
  - 31 blanks, with no row;
  - the United Kingdom, Kosovo and EA21, left out.

  No production exceeds its plant's capacity (1,573 comparisons).

## The requests

| n | What | Outcome |
|---|---|---|
| 1 | ec.europa.eu's robots file | 200, byte for byte session 2806's |
| 2 to 5 | TEN00119's data (one fetch, three retries) | HTTP 403, temporarily unavailable |
| 6 | nrg_inf_nuc's data (probe, one request) | 200 |
| 7 | nrg_inf_nuc's data, into the connector's raw folder | 200, byte for byte the probe's |
| 8 | the PLANT_TEC codelist | 200 |

Reads recorded: 1620 and 1621.

## Decisions made without you

- **ktoe converted to MWh** (41.868 GJ a toe), tSWU to SWU, and tHM written as `t`, so that no new unit was needed.
- **The burnup left out,** rather than a unit Decision made.

## For Samuel's ruling

- None new.

## Files

- New:
  - `warehouse/connectors/eurostat_nuclear_facilities.py`
  - `tests/test_session2812.py` (5 tests, passing)
  - this report
- Changed:
  - the table's registration and holds;
  - the license record (reads 1620 and 1621) and `docs/licenses.md`;
  - coverage, sources, the archive manifest and the release v1 records.
- On the data machine only:
  - `runs/c143/s2812/`, `runs/license_reads/s2812/`;
  - `warehouse/raw/eurostat_nuclear_facilities/`, `warehouse/raw/eurostat_largest_generator/` (the failed answer).
