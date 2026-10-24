# Norway's hydropower reservoirs, a week (NVE's reservoir statistics)

Energy Research Warehouse (ERW), method note written in session 2513 (chain 122) for a table first written on 24 October 2026 (session 2516).

Tables: `nve_norway_reservoirs_weekly`

## Publisher and address

The Norwegian Water Resources and Energy Directorate (NVE), its reservoir statistics (magasinstatistikk), published each Wednesday at 13:00 Norwegian time, through its API: `https://biapi.nve.no/magasinstatistikk/api/Magasinstatistikk/HentOffentligData`. One GET, no key, a JSON list. Source id `nve:magasinstatistikk`. Connector: `warehouse/connectors/nve_norway_reservoirs.py` (session 2516). biapi.nve.no and api.nve.no have no robots file (reads 924, 928); www.nve.no asks a crawl delay of 20 seconds (read 926).

## Vintage and revision

The weeks from 1995 to the week to 18 October 2026, written by run `20261024T182250Z` (the write under the lock, offline), which read the answer saved at 2026-10-24T17:57:48Z. The answer gives the next publication's date (`neste_Publiseringsdato`, 28 October 2026 13:00); each run takes the whole history again.

## Shape and variables

Series, 44,793 rows, 9 entities. `entity` `nve:no:<area>`: `no` (the country), `no1` to `no5` (the price areas, NVE's area type EL), `region_1` to `region_3` (the water regions, type VASS). `ts_utc` the date NVE gives the week (`dato_Id`, its last day), 00:00 UTC: the reservoirs' level is a stock at that date. `freq` P1W; `geo` NO; `node` the area type and number with the ISO week; `x_iso_week` the ISO week.

| `variable` | NVE's field | Unit |
|---|---|---|
| `filling_share` | `fyllingsgrad` times 100 | pct |
| `stored_energy` | `fylling_TWh` times 1,000,000 | MWh |
| `capacity` | `kapasitet_TWh` times 1,000,000 | MWh |

In the week to 18 October 2026 the country's reservoirs held 60.56 TWh of 87.44 TWh (69.3 percent); NO2, the south-west, 52.9 percent; NO4, the north, 90.3 percent.

## Reading the source

- The run stops at once, asking nothing, while `nve_reservoirs` or biapi.nve.no is paused.
- One request a run (timeout 120 seconds); `--offline` reads the saved answer (`warehouse/raw/nve_reservoirs/answer.json`). Session 2516's write read the answer its probe had saved (the probe's request 3), with that request's time.
- **Not taken:** last week's share and the change (`fyllingsgrad_forrige_uke`, `endring_fyllingsgrad`), which the table's own rows give.
- **Fields without a row:** a field without a number.
- The run stops, and no file is written, for: an answer that is not a list, an area type other than NO, EL and VASS, an area's week given twice, a date not of the form YYYY-MM-DD.

Nothing is filled.

## License

Public. NVE's API documentation (read 929): "Data som ligger på api.nve.no er lisensiert under Norsk lisens for offentlige data (NLOD) som er kompatibel med CC Navngivelse 3.0 Norge (CC BY 3.0)." Verdict (session 2516): may be public, sold or not. The header names NVE. Held from the live set; in the next Stanford draft.

## Cross-checks (session 2516)

- The five price areas' capacities, and the three regions', each sum to the country's (87.44 TWh in the week to 18 October 2026).

## What it does not hold

- Inflow, production and the reservoirs' history before 1995; Sweden's and Finland's reservoirs; prices.
