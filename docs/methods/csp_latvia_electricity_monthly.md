# Latvia's electricity production, imports and exports, a month (CSP table ENB010m)

Energy Research Warehouse (ERW), method note written in session 2317 (chain 106) for a table first written on 24 October 2026 (session 2314).

Tables: `csp_latvia_electricity_monthly`

## Publisher and address

The Central Statistical Bureau of Latvia (CSP), Official Statistics Portal, table ENB010m, "Electricity production, imports, exports and consumption (million. kWh) by Indicator and Time period". It is read through the portal's PxWeb API (no key): the table's metadata by GET and one JSON-stat 2.0 query by POST, both at `https://data.stat.gov.lv/api/v1/en/OSP_PUB/START/NOZ/EN/ENB/ENB010m`. Source id `csp:ENB010m`. Connector: `warehouse/connectors/csp_latvia_electricity.py` (session 2314).

data.stat.gov.lv has no robots file (HTTP 404, read 519). CSP's own site, stat.gov.lv, answered HTTP 403 to its robots file (read 520) and was not asked again.

## Vintage and revision

January 2006 to August 2026, written by run `20261024T063211Z`, which read the saved metadata and answer. The query was answered at 2026-10-24T06:31:10Z (`retrieved_at`). `vintage` is the answer's "updated", 2026-09-25T10:00:00Z, in every row. Every run that is not `--offline` asks for the metadata and the whole table again and writes the table again (`write_snapshot`).

## Shape and variables

Series, 2,039 rows, ten indicators.

- `entity`: `csp:lv`.
- `variable`: the indicator's English name in snake case, its leading dots dropped.
- `node`: the indicator as CSP writes it. `x_code`: its code.
- `unit` MWh: the table's million kWh times 1,000.
- `ts_utc`: the month's first day. `freq` P1M, `geo` LV.

| `variable` | `x_code` | Months |
|---|---|---|
| total_gross_electricity_production | GEP | 248, from 2006-01 |
| hydro_power_plants_hpp | HPP | 248 |
| combined_heat_and_power_plants_chp | CHP | 248 |
| wind_turbines | WT | 248 |
| solar_power_plants | SPP | 44, from 2023-01 |
| total_net_electricity_production | NEP | 248 |
| battery_energy_storage_system_bess | BESS | 11, from 2025-10 |
| imports | IMP | 248 |
| exports | EXP | 248 |
| available_for_the_internal_market | INTM | 248 |

Four values are 0 and are kept; none is negative. Totals are CSP's lines.

TWh a year (the twelve months summed here for this note):

| `variable` | 2006 | 2015 | 2025 |
|---|---|---|---|
| total_gross_electricity_production | 4.89 | 5.54 | 5.96 |
| hydro_power_plants_hpp | 2.70 | 1.87 | 2.96 |
| combined_heat_and_power_plants_chp | 2.15 | 3.52 | 2.11 |
| wind_turbines | 0.04 | 0.15 | 0.21 |
| solar_power_plants | | | 0.68 |
| total_net_electricity_production | 4.68 | 5.38 | 5.79 |
| imports | 2.81 | 5.25 | 3.89 |
| exports | 0.30 | 3.42 | 2.49 |
| available_for_the_internal_market | 7.19 | 7.21 | 7.20 |

January to August 2026: gross production 4.87 TWh, solar 1.37 TWh, the battery line 0.04 TWh.

## Reading the source

- The run stops at once, asking nothing, while `csp_latvia_electricity` or the host data.stat.gov.lv is paused.
- Two requests a run. The metadata GET is fetched fresh (timeout 60 seconds, 1 second's pause after it). HTTP 404 stops the run; any other failure is tried up to `RETRIES` (4) times (`iso_prices.fetch_raw`).
  - The metadata must have exactly the three variables `INDICATOR`, `ContentsCode` and `TIME`, and the unit "million. kWh"; else the run stops.
  - The POST asks for every indicator and month (timeout 180 seconds). It is tried once, and an answer other than HTTP 200 stops the run.
- `--offline` reads `query_ENB010m.json` and stops if it is missing.
- The run stops, and no file is written, for any of these:
  - an answer without the three dimensions;
  - a value array not the size of the dimensions;
  - a month not of the form YYYYMmm;
  - an answer with no value;
  - an indicator and month given twice.
- A cell left empty has no row. Nothing is filled. An "updated" beginning 9999 would be written as no vintage.

## License

Internal. The portal's database page carries no licence or terms text (read 521), and CSP's own site refused the reader. No verdict is recorded; `sources.csv` flags the source `internal`.

## Cross-checks (session 2314, full years 2016 to 2025)

- Against `eurostat_electricity_monthly` (Latvia):
  - net production 0.999 to 1.000 of Eurostat's net production TOTAL;
  - imports and exports 1.000 in every year;
  - wind 1.000 to 1.048.
- The internal-market line over `owid_ember_electricity_annual`'s demand: 0.943 to 0.975.
- Within the table:
  - the four sources sum to gross production within 1,000 MWh in all 248 months;
  - net production plus imports less exports equals the internal-market line within 1,000 MWh, but for:
    - August 2011 (11 GWh), September 2011 (8 GWh) and September 2012 (2 GWh), unexplained;
    - December 2025 to August 2026, where the line equals that sum plus the battery line.

## What it does not hold

- Months before 2006; production by fuel within CHP; prices (ENC040 and ENC050, in EUR, not taken); capacity (ENA040, annual).
