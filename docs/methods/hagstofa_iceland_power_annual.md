# Iceland's public power plants: installed capacity and generation, a year (Statistics Iceland, table IDN02101)

Energy Research Warehouse (ERW), method note written in session 2397 (chain 113) with the table, first written on 24 October 2026.

Tables: `hagstofa_iceland_power_annual`

## Publisher and address

Statistics Iceland (Hagstofa Islands), table IDN02101, "Installed capacity and generation in public power plants 1976-2019", in its PxWeb database (environment, energy, production and consumption: `https://px.hagstofa.is/pxen/pxweb/en/Umhverfi/Umhverfi__4_orkumal__2_framleidslaognotkun/`). Statistics Iceland gives the figures' source as the National Energy Authority (Orkustofnun), documents OS-2018-T006-01 and OS-2019-T006-01. It is read through the PxWeb API (no key), one JSON-stat 2.0 query by POST with an empty query (every value): `https://px.hagstofa.is/pxen/api/v1/en/Umhverfi/4_orkumal/2_framleidslaognotkun/IDN02101.px`. Source id `hagstofa:IDN02101`. Connector: `warehouse/connectors/hagstofa_iceland_electricity.py` (session 2397). px.hagstofa.is and statice.is have no robots file (HTTP 404, reads 691 and 701); www.hagstofa.is asks a crawl delay of 10 seconds (read 698).

## Vintage and revision

1976 to 2019. Written by the write under the lock (offline), which read the answer saved at 2026-10-24T10:14:30Z (`retrieved_at`). `vintage` is the answer's "updated", 2015-12-10T10:41:00Z, though the table holds years to 2019. Every table of the folder ends by 2020; Statistics Iceland no longer extends them. Every run that is not `--offline` asks again and writes the table again (`write_snapshot`).

## Shape and variables

Series, 88 rows, one entity (`hagstofa:is`).

- `variable`:
  - `capacity`: "Installed capacity at end of period, MW", 44 years, in MW. It is the capacity at the year's end, written on the year's first day.
  - `generation`: "Annual generation of energy, GWh", 44 years, in MWh (the table's GWh times 1,000).
- `node`: the measure as Statistics Iceland names it; `x_table` IDN02101.
- `ts_utc` the year's first day; `freq` P1Y; `geo` IS.

Generation, TWh: 1976 2.42, 1990 4.45, 2000 7.68, 2010 17.06, 2019 19.49. Capacity: 502.7 MW in 1976, 2,923.4 MW in 2019.

## Reading the source

- The run stops at once, asking nothing, while `hagstofa_energy` or px.hagstofa.is is paused.
- One request a run (timeout 120 seconds), saved as `warehouse/raw/hagstofa_energy/query_IDN02101.json` with its time of retrieval; `--offline` reads it.
- The table's second unit, "Hlutfall" (a share, 100 in every cell), is not taken; only "Magn" (the quantity) is.
- The run stops, and no file is written, for any of these:
  - dimensions other than Year and Energy (and Unit);
  - energy labels other than the two expected;
  - no single unit "Magn";
  - a year not of four digits;
  - a value array not the size of the dimensions;
  - an answer with no value;
  - a measure and year given twice.
- A cell without a number has no row. Nothing is filled.

## License

Public. `license_verdicts.csv` records Statistics Iceland (Hagstofa Islands), read 702 (session 2397): "may be public", for public and for commercial use. Its Open data access page: "All published content on the Statistics Iceland website may be reused, copied, and shared in any format or medium for any purpose as long as Statistics Iceland is credited as the author in accordance with the Creative Commons Attribution 4.0 International (CC BY 4.0) license." The header credits Statistics Iceland.

## Cross-checks (session 2397)

- Generation over `owid_ember_electricity_annual`'s demand for Iceland: 1.007 to 1.021, 2000 to 2019 (Iceland has no interconnector).
- Over `eurostat_electricity_monthly`'s net production for Iceland, the full years 2017 to 2019: 1.000.

## What it does not hold

- **Table IDN02100 (1904 to 1975).** It was read in session 2397 but is not taken: its figures run about twice IDN02101's where the two meet (1975: 992.4 MW and 4,591 GWh; 1976: 502.7 MW and 2,421.4 GWh), and neither table explains the step. The parser reads it; `TABLES` leaves it out.
- Heavy industry's use (IDN02103) and use by sector (IDN02104), not taken within the session's ceiling; the years after 2019; generation by source; prices.
